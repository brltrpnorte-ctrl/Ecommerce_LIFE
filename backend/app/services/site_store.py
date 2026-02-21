from __future__ import annotations

import json
import shutil
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.data.content_defaults import DEFAULT_CATALOG, DEFAULT_SITE_CONTENT
from app.models.schemas import AdminContentUpdateRequest, CatalogContent, Product, SiteContent


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class SiteStore:
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
        self._seed_defaults()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS site_payloads (
                    key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS site_revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def _backup_daily(self) -> None:
        if not self.db_path.exists():
            return
        backup_name = f"crm-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.db"
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            shutil.copy2(self.db_path, backup_path)

    def _seed_defaults(self) -> None:
        default_site = SiteContent.model_validate(DEFAULT_SITE_CONTENT).model_dump()
        default_catalog = CatalogContent.model_validate(DEFAULT_CATALOG).model_dump()
        now = utc_now()

        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()

            for key, payload in (('site_content', default_site), ('catalog', default_catalog)):
                row = cur.execute('SELECT key FROM site_payloads WHERE key = ?', (key,)).fetchone()
                if row is None:
                    cur.execute(
                        'INSERT INTO site_payloads (key, payload, updated_at) VALUES (?, ?, ?)',
                        (key, json.dumps(payload, ensure_ascii=True), now),
                    )

            conn.commit()

    def _read_payload(self, conn: sqlite3.Connection, key: str) -> dict[str, Any]:
        row = conn.execute('SELECT payload FROM site_payloads WHERE key = ?', (key,)).fetchone()
        if row is None:
            raise ValueError(f'Payload ausente: {key}')
        try:
            parsed = json.loads(row['payload'])
        except json.JSONDecodeError as exc:
            raise ValueError(f'Payload invalido para {key}') from exc
        if not isinstance(parsed, dict):
            raise ValueError(f'Payload invalido para {key}')
        return parsed

    def get_site_content(self) -> dict[str, Any]:
        with self.connect() as conn:
            raw = self._read_payload(conn, 'site_content')
        return SiteContent.model_validate(raw).model_dump()

    def get_catalog(self) -> dict[str, Any]:
        with self.connect() as conn:
            raw = self._read_payload(conn, 'catalog')
        return CatalogContent.model_validate(raw).model_dump()

    def list_categories(self) -> list[dict[str, str]]:
        catalog = self.get_catalog()
        categories = catalog['categories']
        return [dict(item) for item in categories]

    def list_brands(self) -> list[str]:
        catalog = self.get_catalog()
        return [str(item) for item in catalog['brands']]

    def list_products(self) -> list[Product]:
        catalog = self.get_catalog()
        return [Product.model_validate(item) for item in catalog['products']]

    def get_admin_content(self) -> dict[str, Any]:
        with self.connect() as conn:
            site = SiteContent.model_validate(self._read_payload(conn, 'site_content')).model_dump()
            catalog = CatalogContent.model_validate(self._read_payload(conn, 'catalog')).model_dump()
            rows = conn.execute("SELECT updated_at FROM site_payloads WHERE key IN ('site_content', 'catalog')").fetchall()

        timestamps = [str(row['updated_at']) for row in rows]
        return {
            'site_content': site,
            'catalog': catalog,
            'updated_at': max(timestamps) if timestamps else utc_now(),
        }

    def update_admin_content(self, payload: dict[str, Any], *, by: str = 'admin') -> dict[str, Any]:
        parsed = AdminContentUpdateRequest.model_validate(payload)
        site_content = parsed.site_content.model_dump()
        catalog = parsed.catalog.model_dump()

        site_json = json.dumps(site_content, ensure_ascii=True)
        catalog_json = json.dumps(catalog, ensure_ascii=True)
        max_payload_bytes = 1_500_000
        if len(site_json.encode('utf-8')) > max_payload_bytes:
            raise ValueError('site_content excede o tamanho maximo permitido')
        if len(catalog_json.encode('utf-8')) > max_payload_bytes:
            raise ValueError('catalog excede o tamanho maximo permitido')

        now = utc_now()
        details = {
            'hero_slides': len(site_content['hero_slides']),
            'story_gallery': len(site_content['story_gallery']),
            'categories': len(catalog['categories']),
            'brands': len(catalog['brands']),
            'products': len(catalog['products']),
        }

        with self.write_lock, self.connect() as conn:
            cur = conn.cursor()
            cur.execute('UPDATE site_payloads SET payload = ?, updated_at = ? WHERE key = ?', (site_json, now, 'site_content'))
            cur.execute('UPDATE site_payloads SET payload = ?, updated_at = ? WHERE key = ?', (catalog_json, now, 'catalog'))
            cur.execute(
                'INSERT INTO site_revisions (actor, action, details, created_at) VALUES (?, ?, ?, ?)',
                (by, 'admin_content_updated', json.dumps(details, ensure_ascii=True), now),
            )
            conn.commit()
            self._backup_daily()

        return {
            'site_content': site_content,
            'catalog': catalog,
            'updated_at': now,
        }
