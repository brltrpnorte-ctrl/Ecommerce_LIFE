from __future__ import annotations

import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    delete,
    inspect,
    text,
)
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.pool import NullPool


metadata = MetaData()


site_payloads = Table(
    'site_payloads',
    metadata,
    Column('key', String(120), primary_key=True),
    Column('payload', Text, nullable=False),
    Column('updated_at', String(64), nullable=False),
)

site_revisions = Table(
    'site_revisions',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('actor', String(120), nullable=False),
    Column('action', String(120), nullable=False),
    Column('details', Text, nullable=False),
    Column('created_at', String(64), nullable=False),
)

contacts = Table(
    'contacts',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('email', String(255), nullable=False, unique=True),
    Column('phone', String(40)),
    Column('company', String(255)),
    Column('job_title', String(255)),
    Column('status', String(80), nullable=False, default='lead'),
    Column('source', String(80), nullable=False, default='site'),
    Column('tags', Text, nullable=False, default='[]'),
    Column('consent', Integer, nullable=False, default=1),
    Column('created_at', String(64), nullable=False),
    Column('updated_at', String(64), nullable=False),
)

leads = Table(
    'leads',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('contact_id', Integer, ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False),
    Column('stage', String(80), nullable=False, default='lead'),
    Column('owner', String(255)),
    Column('estimated_value', Float, nullable=False, default=0),
    Column('close_probability', Integer, nullable=False, default=10),
    Column('notes', Text),
    Column('is_active', Integer, nullable=False, default=1),
    Column('last_activity_at', String(64), nullable=False),
    Column('created_at', String(64), nullable=False),
    Column('updated_at', String(64), nullable=False),
)

interactions = Table(
    'interactions',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('contact_id', Integer, ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False),
    Column('lead_id', Integer, ForeignKey('leads.id', ondelete='SET NULL')),
    Column('channel', String(80), nullable=False),
    Column('summary', Text, nullable=False),
    Column('metadata', Text, nullable=False, default='{}'),
    Column('created_at', String(64), nullable=False),
)

tasks = Table(
    'tasks',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('lead_id', Integer, ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
    Column('title', Text, nullable=False),
    Column('due_date', String(64)),
    Column('done', Integer, nullable=False, default=0),
    Column('auto_generated', Integer, nullable=False, default=0),
    Column('created_at', String(64), nullable=False),
    Column('updated_at', String(64), nullable=False),
)

audit_logs = Table(
    'audit_logs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('entity', String(120), nullable=False),
    Column('entity_id', Integer),
    Column('action', String(120), nullable=False),
    Column('performed_by', String(120), nullable=False),
    Column('details', Text, nullable=False, default='{}'),
    Column('created_at', String(64), nullable=False),
)


SITE_TABLES = (site_payloads, site_revisions)
CRM_TABLES = (contacts, leads, interactions, tasks, audit_logs)
ALL_TABLES = SITE_TABLES + CRM_TABLES
AUTO_ID_TABLES = {table.name for table in ALL_TABLES if 'id' in table.c and table.c.id.primary_key}
TABLES_BY_NAME = {table.name: table for table in ALL_TABLES}


def normalize_database_url(url: str) -> str:
    value = (url or '').strip()
    if not value:
        return value

    value = _encode_password_in_url(value)
    value = _ensure_supabase_sslmode(value)

    if value.startswith('postgres://'):
        value = 'postgresql://' + value[len('postgres://') :]
    if value.startswith('postgresql://') and '+psycopg' not in value and '+psycopg2' not in value:
        value = 'postgresql+psycopg://' + value[len('postgresql://') :]
    return value


def _ensure_supabase_sslmode(url: str) -> str:
    parsed = urlsplit(url)
    host = (parsed.hostname or '').lower()
    if 'supabase.' not in host:
        return url

    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    if any(key.lower() == 'sslmode' for key, _ in query_items):
        return url

    query_items.append(('sslmode', 'require'))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query_items), parsed.fragment))


def _encode_password_in_url(url: str) -> str:
    # Users often paste provider URLs with raw passwords containing reserved chars
    # like '@', '!' or '#'. Encode only the password segment and preserve existing '%xx'.
    if '://' not in url:
        return url

    scheme, remainder = url.split('://', 1)
    # isolate authority (userinfo@host:port) from path/query/fragment
    cut_positions = [pos for sep in ('/', '?', '#') if (pos := remainder.find(sep)) != -1]
    authority_end = min(cut_positions) if cut_positions else len(remainder)
    authority = remainder[:authority_end]
    suffix = remainder[authority_end:]

    if '@' not in authority:
        repaired = _repair_missing_at_before_supabase_host(scheme, authority, suffix)
        return repaired or url

    userinfo, hostpart = authority.rsplit('@', 1)
    if ':' not in userinfo:
        return url

    username, password = userinfo.split(':', 1)
    encoded_password = quote(password, safe='%')
    if encoded_password == password:
        return url

    return f'{scheme}://{username}:{encoded_password}@{hostpart}{suffix}'


def _repair_missing_at_before_supabase_host(scheme: str, authority: str, suffix: str) -> str | None:
    # Handles malformed copied URLs where the separator "@" before the host was removed,
    # e.g. postgresql://user:passaws-1-...pooler.supabase.com:6543/postgres
    host_match = re.search(
        r'(aws-\d-[a-z0-9-]+\.pooler\.supabase\.com|db\.[a-z0-9]+\.supabase\.co)(?::\d+)?$',
        authority,
        re.IGNORECASE,
    )
    if not host_match:
        # fallback for generic supabase domain
        host_match = re.search(r'([a-zA-Z0-9.-]+\.supabase\.(?:co|com))(?::\d+)?$', authority, re.IGNORECASE)
        if not host_match:
            return None

    host_start = host_match.start()
    # include optional ":port" suffix when present
    port_match = re.search(r':\d+$', authority[host_match.end() :])
    hostpart = authority[host_start:]
    if port_match:
        hostpart = authority[host_start : host_match.end() + port_match.end()]

    userinfo = authority[:host_start]
    if not userinfo or ':' not in userinfo:
        return None

    username, password = userinfo.split(':', 1)
    encoded_password = quote(password, safe='%')
    return f'{scheme}://{username}:{encoded_password}@{hostpart}{suffix}'


def _create_engine_from_url(url: str) -> Engine:
    normalized = normalize_database_url(url)
    common_kwargs: dict[str, Any] = {
        'future': True,
        'pool_pre_ping': True,
    }

    if normalized.startswith('sqlite'):
        common_kwargs['connect_args'] = {'check_same_thread': False}
        return create_engine(normalized, **common_kwargs)

    # On Vercel/serverless, prefer no local pool; Supabase pooler handles multiplexing.
    if os.getenv('VERCEL'):
        common_kwargs['poolclass'] = NullPool
    else:
        common_kwargs['pool_size'] = 5
        common_kwargs['max_overflow'] = 2

    return create_engine(normalized, **common_kwargs)


def create_app_engine(*, database_url: str | None, sqlite_path: str | Path | None) -> Engine:
    if database_url and database_url.strip():
        return _create_engine_from_url(database_url)

    if sqlite_path is None:
        raise ValueError('sqlite_path obrigatorio quando database_url nao for informado')

    sqlite_file = Path(sqlite_path)
    sqlite_file.parent.mkdir(parents=True, exist_ok=True)
    return _create_engine_from_url(f"sqlite+pysqlite:///{sqlite_file.as_posix()}")


def ensure_schema(engine: Engine, *, include: str = 'all') -> None:
    if include == 'site':
        tables = list(SITE_TABLES)
    elif include == 'crm':
        tables = list(CRM_TABLES)
    else:
        tables = list(ALL_TABLES)

    metadata.create_all(engine, tables=tables)


def existing_table_names(engine: Engine) -> set[str]:
    return set(inspect(engine).get_table_names())


def reset_postgres_sequences(engine: Engine, table_names: list[str] | None = None) -> None:
    if engine.dialect.name != 'postgresql':
        return

    names = table_names or sorted(AUTO_ID_TABLES)
    with engine.begin() as conn:
        for table_name in names:
            table = TABLES_BY_NAME.get(table_name)
            if table is None or 'id' not in table.c:
                continue
            conn.execute(
                text(
                    f"""
                    SELECT setval(
                      pg_get_serial_sequence('{table_name}', 'id'),
                      COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                      (SELECT COUNT(*) > 0 FROM {table_name})
                    )
                    """
                )
            )


def clear_tables(engine: Engine, table_names: list[str]) -> None:
    # delete in reverse dependency order
    ordered = [TABLES_BY_NAME[name] for name in table_names if name in TABLES_BY_NAME]
    with engine.begin() as conn:
        for table in reversed(ordered):
            conn.execute(delete(table))


def _split_executescript(script: str) -> list[str]:
    return [statement.strip() for statement in script.split(';') if statement.strip()]


def _convert_qmark_sql(sql: str, params: Any) -> tuple[str, dict[str, Any]]:
    if params is None:
        return sql, {}
    if isinstance(params, dict):
        return sql, params

    if not isinstance(params, (tuple, list)):
        seq = [params]
    else:
        seq = list(params)

    if '?' not in sql:
        return sql, {f'p{idx}': value for idx, value in enumerate(seq)}

    parts = sql.split('?')
    rebuilt = [parts[0]]
    binds: dict[str, Any] = {}
    for idx, part in enumerate(parts[1:]):
        key = f'p{idx}'
        rebuilt.append(f':{key}')
        rebuilt.append(part)
        binds[key] = seq[idx]
    return ''.join(rebuilt), binds


@dataclass
class CompatResult:
    rows: list[dict[str, Any]]
    rowcount: int = 0

    def fetchone(self) -> dict[str, Any] | None:
        if not self.rows:
            return None
        return self.rows.pop(0)

    def fetchall(self) -> list[dict[str, Any]]:
        rows = self.rows
        self.rows = []
        return rows


class CompatCursor:
    def __init__(self, wrapper: 'CompatConnection') -> None:
        self.wrapper = wrapper
        self.lastrowid: int | None = None
        self.rowcount: int = -1
        self._result = CompatResult(rows=[], rowcount=0)

    def execute(self, sql: str, params: Any = None) -> 'CompatCursor':
        result, lastrowid = self.wrapper._execute(sql, params, track_lastrowid=True)
        self._result = result
        self.lastrowid = lastrowid
        self.rowcount = result.rowcount
        return self

    def fetchone(self) -> dict[str, Any] | None:
        return self._result.fetchone()

    def fetchall(self) -> list[dict[str, Any]]:
        return self._result.fetchall()


class CompatConnection:
    def __init__(self, sa_conn: Connection, *, dialect_name: str, auto_id_tables: set[str]) -> None:
        self._conn = sa_conn
        self.dialect_name = dialect_name
        self.auto_id_tables = auto_id_tables
        self.row_factory = None

    def _execute(self, sql: str, params: Any = None, *, track_lastrowid: bool = False) -> tuple[CompatResult, int | None]:
        raw_sql = sql.strip()
        sql_text = raw_sql
        lastrowid: int | None = None
        auto_consumed = False

        insert_match = re.match(r'(?is)^insert\s+into\s+([a-zA-Z_][a-zA-Z0-9_]*)', raw_sql)
        target_table = insert_match.group(1) if insert_match else None
        should_return_id = (
            track_lastrowid
            and self.dialect_name == 'postgresql'
            and target_table in self.auto_id_tables
            and 'returning' not in raw_sql.lower()
        )
        if should_return_id:
            sql_text = f"{raw_sql} RETURNING id"

        converted_sql, bind_params = _convert_qmark_sql(sql_text, params)
        result = self._conn.execute(text(converted_sql), bind_params)

        if should_return_id and result.returns_rows:
            inserted = result.mappings().first()
            if inserted and inserted.get('id') is not None:
                lastrowid = int(inserted['id'])
            auto_consumed = True
        elif track_lastrowid:
            raw_lastrowid = getattr(result, 'lastrowid', None)
            if raw_lastrowid is not None:
                try:
                    lastrowid = int(raw_lastrowid)
                except (TypeError, ValueError):
                    lastrowid = None

        rows: list[dict[str, Any]] = []
        if result.returns_rows and not auto_consumed:
            rows = [dict(row) for row in result.mappings().all()]

        rowcount = int(result.rowcount) if result.rowcount is not None else 0
        return CompatResult(rows=rows, rowcount=rowcount), lastrowid

    def execute(self, sql: str, params: Any = None) -> CompatResult:
        result, _ = self._execute(sql, params, track_lastrowid=False)
        return result

    def cursor(self) -> CompatCursor:
        return CompatCursor(self)

    def executescript(self, script: str) -> None:
        for statement in _split_executescript(script):
            self._conn.execute(text(statement))

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


class StoreDatabase:
    def __init__(self, *, database_url: str | None, sqlite_path: str | Path | None, auto_id_tables: set[str]) -> None:
        self.database_url = database_url.strip() if isinstance(database_url, str) and database_url.strip() else None
        self.sqlite_path = Path(sqlite_path) if sqlite_path else None
        self.engine = create_app_engine(database_url=self.database_url, sqlite_path=self.sqlite_path)
        self.auto_id_tables = auto_id_tables

    @property
    def dialect_name(self) -> str:
        return self.engine.dialect.name

    @property
    def is_sqlite(self) -> bool:
        return self.dialect_name == 'sqlite'

    @property
    def is_postgres(self) -> bool:
        return self.dialect_name == 'postgresql'

    @contextmanager
    def connect(self):
        sa_conn = self.engine.connect()
        try:
            if self.is_sqlite:
                sa_conn.exec_driver_sql('PRAGMA foreign_keys = ON')
            yield CompatConnection(sa_conn, dialect_name=self.dialect_name, auto_id_tables=self.auto_id_tables)
        except Exception:
            if sa_conn.in_transaction():
                sa_conn.rollback()
            raise
        finally:
            sa_conn.close()
