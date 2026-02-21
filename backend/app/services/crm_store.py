from __future__ import annotations

import json
import shutil
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PIPELINE_STAGES = (
    'lead',
    'qualificado',
    'proposta',
    'negociacao',
    'fechado-ganho',
    'fechado-perdido',
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def parse_json_dict(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def normalize_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    clean: list[str] = []
    for tag in tags:
        item = tag.strip().lower()
        if not item or item in seen:
            continue
        seen.add(item)
        clean.append(item)
    return clean


class CRMStore:
    def __init__(self, database_path: str, backup_dir: str) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        self.db_path = Path(database_path)
        self.backup_dir = Path(backup_dir)

        if not self.db_path.is_absolute():
            self.db_path = base_dir / self.db_path
        if not self.backup_dir.is_absolute():
            self.backup_dir = base_dir / self.backup_dir

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.write_lock = threading.Lock()
        self._init_schema()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON;')
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    company TEXT,
                    job_title TEXT,
                    status TEXT NOT NULL DEFAULT 'lead',
                    source TEXT NOT NULL DEFAULT 'site',
                    tags TEXT NOT NULL DEFAULT '[]',
                    consent INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    stage TEXT NOT NULL DEFAULT 'lead',
                    owner TEXT,
                    estimated_value REAL NOT NULL DEFAULT 0,
                    close_probability INTEGER NOT NULL DEFAULT 10,
                    notes TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    last_activity_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    lead_id INTEGER,
                    channel TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    due_date TEXT,
                    done INTEGER NOT NULL DEFAULT 0,
                    auto_generated INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    entity_id INTEGER,
                    action TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    details TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def _insert_audit(
        self,
        cur: sqlite3.Cursor,
        *,
        entity: str,
        entity_id: int | None,
        action: str,
        by: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        cur.execute(
            """
            INSERT INTO audit_logs (entity, entity_id, action, performed_by, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entity, entity_id, action, by, json.dumps(details or {}, ensure_ascii=True), utc_now()),
        )

    def _backup_daily(self) -> None:
        if not self.db_path.exists():
            return
        backup_name = f"crm-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.db"
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            shutil.copy2(self.db_path, backup_path)

    def backup_now(self) -> str:
        if not self.db_path.exists():
            raise ValueError('Banco CRM indisponivel')
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        backup_path = self.backup_dir / f'crm-backup-{timestamp}.db'
        shutil.copy2(self.db_path, backup_path)
        return str(backup_path)

    def _lead_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'id': int(row['id']),
            'contact_id': int(row['contact_id']),
            'contact_name': row['contact_name'],
            'contact_email': row['contact_email'],
            'contact_phone': row['contact_phone'],
            'company': row['company'],
            'job_title': row['job_title'],
            'source': row['source'],
            'tags': parse_json_list(row['tags']),
            'stage': row['stage'],
            'owner': row['owner'],
            'estimated_value': float(row['estimated_value']),
            'close_probability': int(row['close_probability']),
            'notes': row['notes'] or '',
            'is_active': bool(row['is_active']),
            'last_activity_at': row['last_activity_at'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        }

    def _task_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'id': int(row['id']),
            'lead_id': int(row['lead_id']),
            'title': row['title'],
            'due_date': row['due_date'],
            'done': bool(row['done']),
            'auto_generated': bool(row['auto_generated']),
            'lead_stage': row['lead_stage'],
            'owner': row['owner'],
            'contact_name': row['contact_name'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        }

    def _fetch_lead(self, conn: sqlite3.Connection, lead_id: int) -> dict[str, Any]:
        row = conn.execute(
            """
            SELECT
                l.*,
                c.name AS contact_name,
                c.email AS contact_email,
                c.phone AS contact_phone,
                c.company,
                c.job_title,
                c.source,
                c.tags
            FROM leads l
            JOIN contacts c ON c.id = l.contact_id
            WHERE l.id = ?
            """,
            (lead_id,),
        ).fetchone()
        if row is None:
            raise ValueError('Lead nao encontrado')
        return self._lead_from_row(row)

    def capture_lead(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        email = payload['email'].strip().lower()
        tags = normalize_tags(payload.get('tags', []))

        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()
            contact = cur.execute("SELECT * FROM contacts WHERE email = ?", (email,)).fetchone()
            deduplicated = contact is not None

            if contact:
                merged_tags = normalize_tags(parse_json_list(contact['tags']) + tags)
                cur.execute(
                    """
                    UPDATE contacts
                    SET name = ?, phone = ?, company = ?, job_title = ?, status = ?, source = ?, tags = ?, consent = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        payload['name'],
                        payload.get('phone'),
                        payload.get('company'),
                        payload.get('job_title'),
                        payload.get('status', 'lead'),
                        payload.get('source', 'site'),
                        json.dumps(merged_tags, ensure_ascii=True),
                        int(bool(payload.get('consent', True))),
                        now,
                        int(contact['id']),
                    ),
                )
                contact_id = int(contact['id'])
                self._insert_audit(cur, entity='contact', entity_id=contact_id, action='updated', by='system')
            else:
                cur.execute(
                    """
                    INSERT INTO contacts (name, email, phone, company, job_title, status, source, tags, consent, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload['name'],
                        email,
                        payload.get('phone'),
                        payload.get('company'),
                        payload.get('job_title'),
                        payload.get('status', 'lead'),
                        payload.get('source', 'site'),
                        json.dumps(tags, ensure_ascii=True),
                        int(bool(payload.get('consent', True))),
                        now,
                        now,
                    ),
                )
                contact_id = int(cur.lastrowid)
                self._insert_audit(cur, entity='contact', entity_id=contact_id, action='created', by='system')

            lead = cur.execute(
                """
                SELECT * FROM leads
                WHERE contact_id = ? AND is_active = 1
                ORDER BY id DESC LIMIT 1
                """,
                (contact_id,),
            ).fetchone()

            reopened = False
            if lead and lead['stage'] not in ('fechado-ganho', 'fechado-perdido'):
                lead_id = int(lead['id'])
                reopened = True
                cur.execute(
                    """
                    UPDATE leads
                    SET owner = ?, estimated_value = ?, close_probability = ?, notes = ?, last_activity_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        payload.get('owner'),
                        float(payload.get('estimated_value', 0) or 0),
                        int(payload.get('close_probability', 10) or 10),
                        payload.get('notes'),
                        now,
                        now,
                        lead_id,
                    ),
                )
                self._insert_audit(cur, entity='lead', entity_id=lead_id, action='reengaged', by='system')
            else:
                stage = payload.get('stage', 'lead')
                if stage not in PIPELINE_STAGES:
                    stage = 'lead'
                cur.execute(
                    """
                    INSERT INTO leads (
                        contact_id, stage, owner, estimated_value, close_probability, notes, is_active, last_activity_at, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                    """,
                    (
                        contact_id,
                        stage,
                        payload.get('owner'),
                        float(payload.get('estimated_value', 0) or 0),
                        int(payload.get('close_probability', 10) or 10),
                        payload.get('notes'),
                        now,
                        now,
                        now,
                    ),
                )
                lead_id = int(cur.lastrowid)
                self._insert_audit(cur, entity='lead', entity_id=lead_id, action='created', by='system')

            conn.commit()
            self._backup_daily()
            return {
                'deduplicated_contact': deduplicated,
                'reopened_lead': reopened,
                'lead': self._fetch_lead(conn, lead_id),
            }

    def list_contacts(self, *, status: str | None = None, tag: str | None = None, search: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT id, name, email, phone, company, job_title, status, source, tags, consent, created_at, updated_at
            FROM contacts WHERE 1 = 1
        """
        params: list[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if search:
            term = f"%{search.strip().lower()}%"
            query += " AND (lower(name) LIKE ? OR lower(email) LIKE ? OR lower(company) LIKE ? OR phone LIKE ?)"
            params.extend([term, term, term, term])
        query += " ORDER BY updated_at DESC"

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        required_tag = tag.strip().lower() if tag else None
        items: list[dict[str, Any]] = []
        for row in rows:
            tags = parse_json_list(row['tags'])
            if required_tag and required_tag not in tags:
                continue
            items.append(
                {
                    'id': int(row['id']),
                    'name': row['name'],
                    'email': row['email'],
                    'phone': row['phone'],
                    'company': row['company'],
                    'job_title': row['job_title'],
                    'status': row['status'],
                    'source': row['source'],
                    'tags': tags,
                    'consent': bool(row['consent']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                }
            )
        return items

    def list_leads(
        self,
        *,
        stage: str | None = None,
        owner: str | None = None,
        active_only: bool = True,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                l.*,
                c.name AS contact_name,
                c.email AS contact_email,
                c.phone AS contact_phone,
                c.company,
                c.job_title,
                c.source,
                c.tags
            FROM leads l
            JOIN contacts c ON c.id = l.contact_id
            WHERE 1 = 1
        """
        params: list[Any] = []
        if stage:
            query += " AND l.stage = ?"
            params.append(stage)
        if owner:
            query += " AND lower(l.owner) = ?"
            params.append(owner.strip().lower())
        if active_only:
            query += " AND l.is_active = 1"
        if search:
            term = f"%{search.strip().lower()}%"
            query += " AND (lower(c.name) LIKE ? OR lower(c.email) LIKE ? OR lower(c.company) LIKE ?)"
            params.extend([term, term, term])
        query += " ORDER BY l.updated_at DESC"

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._lead_from_row(row) for row in rows]

    def update_lead(self, lead_id: int, updates: dict[str, Any], *, by: str) -> dict[str, Any]:
        allowed = {
            'stage': 'stage',
            'owner': 'owner',
            'estimated_value': 'estimated_value',
            'close_probability': 'close_probability',
            'is_active': 'is_active',
            'notes': 'notes',
        }

        assignments: list[str] = []
        params: list[Any] = []
        for key, column in allowed.items():
            if updates.get(key) is None:
                continue
            value = updates[key]
            if key == 'is_active':
                value = int(bool(value))
            assignments.append(f"{column} = ?")
            params.append(value)

        if updates.get('touchpoint'):
            assignments.append("last_activity_at = ?")
            params.append(utc_now())

        assignments.append("updated_at = ?")
        params.append(utc_now())

        with self.write_lock, self.connect() as conn:
            if assignments:
                cur = conn.cursor()
                cur.execute(
                    f"UPDATE leads SET {', '.join(assignments)} WHERE id = ?",
                    (*params, lead_id),
                )
                if cur.rowcount == 0:
                    raise ValueError('Lead nao encontrado')
                self._insert_audit(cur, entity='lead', entity_id=lead_id, action='updated', by=by, details=updates)
                conn.commit()
                self._backup_daily()
            return self._fetch_lead(conn, lead_id)

    def create_interaction(self, payload: dict[str, Any], *, by: str) -> dict[str, Any]:
        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()
            contact = cur.execute("SELECT id FROM contacts WHERE id = ?", (payload['contact_id'],)).fetchone()
            if contact is None:
                raise ValueError('Contato nao encontrado')

            lead_id = payload.get('lead_id')
            if lead_id is not None:
                lead = cur.execute("SELECT id FROM leads WHERE id = ?", (lead_id,)).fetchone()
                if lead is None:
                    raise ValueError('Lead nao encontrado')

            now = utc_now()
            cur.execute(
                """
                INSERT INTO interactions (contact_id, lead_id, channel, summary, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload['contact_id'],
                    lead_id,
                    payload['channel'],
                    payload['summary'],
                    json.dumps(payload.get('metadata', {}), ensure_ascii=True),
                    now,
                ),
            )
            interaction_id = int(cur.lastrowid)
            if lead_id is not None:
                cur.execute("UPDATE leads SET last_activity_at = ?, updated_at = ? WHERE id = ?", (now, now, lead_id))

            self._insert_audit(cur, entity='interaction', entity_id=interaction_id, action='created', by=by)
            conn.commit()
            self._backup_daily()

            row = conn.execute(
                """
                SELECT i.*, c.name AS contact_name, c.email AS contact_email
                FROM interactions i
                JOIN contacts c ON c.id = i.contact_id
                WHERE i.id = ?
                """,
                (interaction_id,),
            ).fetchone()
            if row is None:
                raise ValueError('Interacao nao encontrada')
            return {
                'id': int(row['id']),
                'contact_id': int(row['contact_id']),
                'lead_id': int(row['lead_id']) if row['lead_id'] is not None else None,
                'contact_name': row['contact_name'],
                'contact_email': row['contact_email'],
                'channel': row['channel'],
                'summary': row['summary'],
                'metadata': parse_json_dict(row['metadata']),
                'created_at': row['created_at'],
            }

    def list_interactions(
        self,
        *,
        contact_id: int | None = None,
        lead_id: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT i.*, c.name AS contact_name, c.email AS contact_email
            FROM interactions i
            JOIN contacts c ON c.id = i.contact_id
            WHERE 1 = 1
        """
        params: list[Any] = []
        if contact_id is not None:
            query += " AND i.contact_id = ?"
            params.append(contact_id)
        if lead_id is not None:
            query += " AND i.lead_id = ?"
            params.append(lead_id)
        query += " ORDER BY i.created_at DESC LIMIT ?"
        params.append(min(max(limit, 1), 300))

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                'id': int(row['id']),
                'contact_id': int(row['contact_id']),
                'lead_id': int(row['lead_id']) if row['lead_id'] is not None else None,
                'contact_name': row['contact_name'],
                'contact_email': row['contact_email'],
                'channel': row['channel'],
                'summary': row['summary'],
                'metadata': parse_json_dict(row['metadata']),
                'created_at': row['created_at'],
            }
            for row in rows
        ]

    def create_task(self, payload: dict[str, Any], *, by: str) -> dict[str, Any]:
        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()
            lead = cur.execute("SELECT id FROM leads WHERE id = ?", (payload['lead_id'],)).fetchone()
            if lead is None:
                raise ValueError('Lead nao encontrado')

            now = utc_now()
            cur.execute(
                """
                INSERT INTO tasks (lead_id, title, due_date, done, auto_generated, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload['lead_id'],
                    payload['title'],
                    payload.get('due_date'),
                    int(bool(payload.get('done', False))),
                    int(bool(payload.get('auto_generated', False))),
                    now,
                    now,
                ),
            )
            task_id = int(cur.lastrowid)
            self._insert_audit(cur, entity='task', entity_id=task_id, action='created', by=by)
            conn.commit()
            self._backup_daily()
            return self._fetch_task(conn, task_id)

    def _fetch_task(self, conn: sqlite3.Connection, task_id: int) -> dict[str, Any]:
        row = conn.execute(
            """
            SELECT
                t.*,
                l.stage AS lead_stage,
                l.owner,
                c.name AS contact_name
            FROM tasks t
            JOIN leads l ON l.id = t.lead_id
            JOIN contacts c ON c.id = l.contact_id
            WHERE t.id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            raise ValueError('Tarefa nao encontrada')
        return self._task_from_row(row)

    def update_task(self, task_id: int, *, done: bool, by: str) -> dict[str, Any]:
        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE tasks SET done = ?, updated_at = ? WHERE id = ?", (int(done), utc_now(), task_id))
            if cur.rowcount == 0:
                raise ValueError('Tarefa nao encontrada')
            self._insert_audit(cur, entity='task', entity_id=task_id, action='updated', by=by, details={'done': done})
            conn.commit()
            self._backup_daily()
            return self._fetch_task(conn, task_id)

    def list_tasks(
        self,
        *,
        lead_id: int | None = None,
        owner: str | None = None,
        done: bool | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                t.*,
                l.stage AS lead_stage,
                l.owner,
                c.name AS contact_name
            FROM tasks t
            JOIN leads l ON l.id = t.lead_id
            JOIN contacts c ON c.id = l.contact_id
            WHERE 1 = 1
        """
        params: list[Any] = []
        if lead_id is not None:
            query += " AND t.lead_id = ?"
            params.append(lead_id)
        if owner:
            query += " AND lower(l.owner) = ?"
            params.append(owner.strip().lower())
        if done is not None:
            query += " AND t.done = ?"
            params.append(int(done))
        query += " ORDER BY t.updated_at DESC LIMIT ?"
        params.append(min(max(limit, 1), 500))

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._task_from_row(row) for row in rows]

    def run_stalled_lead_automation(self, *, stale_days: int, by: str) -> dict[str, Any]:
        threshold = (datetime.now(timezone.utc) - timedelta(days=max(stale_days, 1))).replace(microsecond=0).isoformat()
        created_ids: list[int] = []
        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                """
                SELECT l.id AS lead_id, c.name AS contact_name
                FROM leads l
                JOIN contacts c ON c.id = l.contact_id
                WHERE l.is_active = 1
                  AND l.stage NOT IN ('fechado-ganho', 'fechado-perdido')
                  AND l.last_activity_at < ?
                  AND NOT EXISTS (
                    SELECT 1 FROM tasks t
                    WHERE t.lead_id = l.id AND t.done = 0 AND t.auto_generated = 1
                  )
                """,
                (threshold,),
            ).fetchall()

            now = utc_now()
            for row in rows:
                title = f"Follow-up automatico: contatar {row['contact_name']}"
                cur.execute(
                    """
                    INSERT INTO tasks (lead_id, title, due_date, done, auto_generated, created_at, updated_at)
                    VALUES (?, ?, ?, 0, 1, ?, ?)
                    """,
                    (int(row['lead_id']), title, now, now, now),
                )
                task_id = int(cur.lastrowid)
                created_ids.append(task_id)
                self._insert_audit(cur, entity='task', entity_id=task_id, action='auto_created', by=by)

            conn.commit()
            self._backup_daily()
            tasks = [self._fetch_task(conn, task_id) for task_id in created_ids]

        return {
            'threshold_days': max(stale_days, 1),
            'stalled_leads': len(rows),
            'tasks_created': len(created_ids),
            'tasks': tasks,
        }

    def dashboard(self, *, stale_days: int = 7) -> dict[str, Any]:
        threshold = (datetime.now(timezone.utc) - timedelta(days=max(stale_days, 1))).replace(microsecond=0).isoformat()
        with self.connect() as conn:
            total_contacts = int(conn.execute("SELECT COUNT(*) AS total FROM contacts").fetchone()['total'])
            total_leads = int(conn.execute("SELECT COUNT(*) AS total FROM leads").fetchone()['total'])
            open_leads = int(conn.execute("SELECT COUNT(*) AS total FROM leads WHERE is_active = 1").fetchone()['total'])
            qualified_leads = int(
                conn.execute(
                    "SELECT COUNT(*) AS total FROM leads WHERE stage IN ('qualificado', 'proposta', 'negociacao')",
                ).fetchone()['total']
            )
            won_deals = int(conn.execute("SELECT COUNT(*) AS total FROM leads WHERE stage = 'fechado-ganho'").fetchone()['total'])
            lost_deals = int(conn.execute("SELECT COUNT(*) AS total FROM leads WHERE stage = 'fechado-perdido'").fetchone()['total'])
            stalled_leads = int(
                conn.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM leads
                    WHERE is_active = 1
                      AND stage NOT IN ('fechado-ganho', 'fechado-perdido')
                      AND last_activity_at < ?
                    """,
                    (threshold,),
                ).fetchone()['total']
            )
            estimated_revenue = float(
                conn.execute(
                    """
                    SELECT COALESCE(SUM(estimated_value * close_probability / 100.0), 0) AS total
                    FROM leads
                    WHERE stage != 'fechado-perdido'
                    """,
                ).fetchone()['total']
            )
            by_stage_rows = conn.execute("SELECT stage, COUNT(*) AS total FROM leads GROUP BY stage ORDER BY total DESC").fetchall()
            by_source_rows = conn.execute("SELECT source, COUNT(*) AS total FROM contacts GROUP BY source ORDER BY total DESC").fetchall()

        conversion_rate = round((won_deals / total_leads * 100.0), 2) if total_leads else 0.0
        return {
            'total_contacts': total_contacts,
            'total_leads': total_leads,
            'open_leads': open_leads,
            'qualified_leads': qualified_leads,
            'won_deals': won_deals,
            'lost_deals': lost_deals,
            'stalled_leads': stalled_leads,
            'estimated_revenue': round(estimated_revenue, 2),
            'conversion_rate': conversion_rate,
            'by_stage': [{'stage': row['stage'], 'total': int(row['total'])} for row in by_stage_rows],
            'by_source': [{'source': row['source'], 'total': int(row['total'])} for row in by_source_rows],
        }

    def list_audit(self, *, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, entity, entity_id, action, performed_by, details, created_at
                FROM audit_logs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (min(max(limit, 1), 1000),),
            ).fetchall()
        return [
            {
                'id': int(row['id']),
                'entity': row['entity'],
                'entity_id': int(row['entity_id']) if row['entity_id'] is not None else None,
                'action': row['action'],
                'performed_by': row['performed_by'],
                'details': parse_json_dict(row['details']),
                'created_at': row['created_at'],
            }
            for row in rows
        ]
