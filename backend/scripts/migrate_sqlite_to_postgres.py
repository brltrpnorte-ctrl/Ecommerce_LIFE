from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import delete, select

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import ALL_TABLES, create_app_engine, ensure_schema, existing_table_names, reset_postgres_sequences  # noqa: E402
from app.core.settings import get_settings  # noqa: E402


def resolve_source_path(raw_path: str | None, default_path: str) -> Path:
    candidate = Path(raw_path) if raw_path else Path(default_path)
    if not candidate.is_absolute():
        candidate = BACKEND_DIR / candidate
    return candidate


def migrate(*, source_sqlite: Path, target_url: str, yes: bool = False, dry_run: bool = False) -> None:
    if not source_sqlite.exists():
        raise FileNotFoundError(f'SQLite de origem nao encontrado: {source_sqlite}')

    source_engine = create_app_engine(database_url=None, sqlite_path=source_sqlite)
    target_engine = create_app_engine(database_url=target_url, sqlite_path=None)

    if target_engine.dialect.name != 'postgresql':
        raise RuntimeError('O alvo de migracao precisa ser PostgreSQL/Supabase')

    source_tables = existing_table_names(source_engine)
    tables_to_copy = [table for table in ALL_TABLES if table.name in source_tables]

    if not tables_to_copy:
        raise RuntimeError('Nenhuma tabela conhecida encontrada no SQLite de origem')

    counts: dict[str, int] = {}
    with source_engine.connect() as source_conn:
        for table in tables_to_copy:
            rows = source_conn.execute(select(table)).mappings().all()
            counts[table.name] = len(rows)

    print('Resumo da migracao (origem SQLite -> alvo PostgreSQL):')
    for table in tables_to_copy:
        print(f' - {table.name}: {counts.get(table.name, 0)} registros')

    if dry_run:
        print('\nDry-run concluido. Nenhuma alteracao foi aplicada no PostgreSQL.')
        return

    if not yes:
        raise RuntimeError('Use --yes para confirmar limpeza e copia no banco alvo')

    ensure_schema(target_engine, include='all')

    with source_engine.connect() as source_conn, target_engine.begin() as target_conn:
        for table in reversed(tables_to_copy):
            target_conn.execute(delete(table))

        for table in tables_to_copy:
            rows = [dict(row) for row in source_conn.execute(select(table)).mappings().all()]
            if rows:
                target_conn.execute(table.insert(), rows)

    reset_postgres_sequences(target_engine, table_names=[table.name for table in tables_to_copy])
    print('\nMigracao concluida com sucesso.')


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description='Migra dados do backend (SQLite) para PostgreSQL/Supabase.')
    parser.add_argument('--source-sqlite', help='Caminho do arquivo SQLite de origem (default: settings.database_path).')
    parser.add_argument(
        '--target-url',
        help='Connection string PostgreSQL alvo. Se omitido, usa DATABASE_URL_MIGRATIONS (ou DATABASE_URL).',
    )
    parser.add_argument('--dry-run', action='store_true', help='Apenas exibe contagem das tabelas sem escrever no alvo.')
    parser.add_argument('--yes', action='store_true', help='Confirma limpeza e copia no banco PostgreSQL alvo.')
    args = parser.parse_args()

    source_path = resolve_source_path(args.source_sqlite, settings.database_path)
    target_url = (args.target_url or settings.migrations_database_url or settings.runtime_database_url or '').strip()

    if not target_url:
        raise RuntimeError('DATABASE_URL_MIGRATIONS (ou --target-url) nao configurado')

    migrate(source_sqlite=source_path, target_url=target_url, yes=args.yes, dry_run=args.dry_run)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
