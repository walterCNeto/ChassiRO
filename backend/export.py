#!/usr/bin/env python3
"""
Export do chassi universal de RCSA para formatos consumiveis.

Uso:
    python export.py to-json    [--output chassi.json]
    python export.py to-sqlite  [--output chassi.sqlite]
    python export.py stats

Le do Postgres (variaveis em .env ou ambiente) e gera snapshot.
"""

import os
import json
import sqlite3
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import click
import psycopg
from psycopg.rows import dict_row


# ============================================================
# Conexao Postgres
# ============================================================

def get_pg_dsn() -> str:
    """Le DSN do ambiente. Suporta DATABASE_URL ou variaveis individuais."""
    if dsn := os.getenv("DATABASE_URL"):
        return dsn
    host     = os.getenv("PGHOST", "localhost")
    port     = os.getenv("PGPORT", "5432")
    user     = os.getenv("PGUSER", "chassi")
    password = os.getenv("PGPASSWORD", "chassi")
    dbname   = os.getenv("PGDATABASE", "chassi")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def connect_pg() -> psycopg.Connection:
    return psycopg.connect(get_pg_dsn(), row_factory=dict_row)


# ============================================================
# Serializacao
# ============================================================

class ChassiEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


# ============================================================
# Tabelas a exportar
# ============================================================

# Ordem de export importa para SQLite (FKs)
EXPORT_TABLES = [
    "reguladores",
    "tipos_entidade",
    "tipo_entidade_regulador",
    "segmentos",
    "atividades_canonicas",
    "processos",
    "riscos",
    "normas",
    "norma_artigos",
    "norma_aplicabilidade_tipo_entidade",
    "norma_aplicabilidade_segmento",
    "norma_aplicabilidade_atividade",
    "vinculo_norma_processo",
    "vinculo_norma_risco",
    "vinculo_processo_risco",
    "chassi_versions",
    "chassi_changelog",
]


def fetch_table(conn: psycopg.Connection, table: str) -> list[dict]:
    """Le todas as linhas de uma tabela como dicionarios."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table}")
        return list(cur.fetchall())


# ============================================================
# Comando: stats
# ============================================================

@click.group()
def cli():
    """Chassi Universal de RCSA - ferramentas de export."""
    pass


@cli.command()
def stats():
    """Mostra estatisticas do chassi atual."""
    with connect_pg() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM v_chassi_stats")
        s = cur.fetchone()

    if not s:
        click.echo("Nenhuma estatistica encontrada.", err=True)
        sys.exit(1)

    click.echo("=" * 50)
    click.echo("CHASSI UNIVERSAL DE RCSA - ESTATISTICAS")
    click.echo("=" * 50)
    click.echo(f"Versao atual:               {s['versao_atual']}")
    click.echo(f"Reguladores ativos:         {s['reguladores_ativos']}")
    click.echo(f"Tipos de entidade:          {s['tipos_entidade']}")
    click.echo(f"Segmentos:                  {s['segmentos']}")
    click.echo(f"Atividades canonicas:       {s['atividades']}")
    click.echo(f"Normas vigentes / total:    {s['normas_vigentes']} / {s['normas_total']}")
    click.echo(f"Processos (P0):             {s['processos_total']} ({s['processos_p0']} no P0)")
    click.echo(f"Riscos (R0):                {s['riscos_total']} ({s['riscos_r0']} no R0)")
    click.echo(f"Vinculos norma->processo:   {s['vinculos_norma_processo']}")
    click.echo(f"Vinculos processo->risco:   {s['vinculos_processo_risco']}")
    click.echo("=" * 50)


# ============================================================
# Comando: to-json
# ============================================================

@cli.command(name="to-json")
@click.option("--output", "-o", default="chassi.json",
              help="Arquivo de saida (default: chassi.json)")
@click.option("--indent", default=2, type=int,
              help="Indentacao do JSON (default: 2)")
def to_json(output: str, indent: int):
    """Exporta o chassi inteiro para JSON."""
    output_path = Path(output)

    payload: dict = {}
    with connect_pg() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT version, released_at, notas FROM chassi_versions WHERE is_current = TRUE"
            )
            v = cur.fetchone()
            if v:
                payload["_metadata"] = {
                    "version": v["version"],
                    "released_at": v["released_at"].isoformat() if v["released_at"] else None,
                    "exported_at": datetime.now().isoformat(),
                    "notas": v["notas"],
                }

        for table in EXPORT_TABLES:
            rows = fetch_table(conn, table)
            payload[table] = rows
            click.echo(f"  [json] {table}: {len(rows)} linhas")

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=indent, ensure_ascii=False, cls=ChassiEncoder)

    size_kb = output_path.stat().st_size / 1024
    click.echo(f"\nExportado para {output_path} ({size_kb:.1f} KB)")


# ============================================================
# Comando: to-sqlite
# ============================================================

# Mapeamento de tipos Postgres -> SQLite
PG_TO_SQLITE_TYPES = {
    "text": "TEXT",
    "varchar": "TEXT",
    "integer": "INTEGER",
    "bigint": "INTEGER",
    "smallint": "INTEGER",
    "boolean": "INTEGER",
    "date": "TEXT",
    "timestamp with time zone": "TEXT",
    "timestamp without time zone": "TEXT",
    "numeric": "REAL",
}


def get_table_columns(conn: psycopg.Connection, table: str) -> list[dict]:
    """Le metadados das colunas da tabela."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default,
                   ordinal_position
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        return list(cur.fetchall())


def build_sqlite_create(conn: psycopg.Connection, table: str) -> str:
    """Gera DDL SQLite a partir do schema Postgres."""
    cols = get_table_columns(conn, table)
    parts = []
    for c in cols:
        sqlite_type = PG_TO_SQLITE_TYPES.get(c["data_type"], "TEXT")
        nullable = "" if c["is_nullable"] == "YES" else " NOT NULL"
        parts.append(f'"{c["column_name"]}" {sqlite_type}{nullable}')
    return f'CREATE TABLE IF NOT EXISTS "{table}" (\n  ' + ",\n  ".join(parts) + "\n);"


def serialize_for_sqlite(value):
    """Converte valores para tipos compativeis com SQLite."""
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return value


@cli.command(name="to-sqlite")
@click.option("--output", "-o", default="chassi.sqlite",
              help="Arquivo de saida (default: chassi.sqlite)")
def to_sqlite(output: str):
    """Exporta o chassi inteiro para SQLite."""
    output_path = Path(output)
    if output_path.exists():
        output_path.unlink()

    sqlite_conn = sqlite3.connect(str(output_path))
    sqlite_conn.execute("PRAGMA journal_mode = WAL")
    sqlite_conn.execute("PRAGMA foreign_keys = OFF")

    with connect_pg() as pg_conn:
        for table in EXPORT_TABLES:
            ddl = build_sqlite_create(pg_conn, table)
            sqlite_conn.execute(ddl)

            rows = fetch_table(pg_conn, table)
            if not rows:
                click.echo(f"  [sqlite] {table}: 0 linhas (skip)")
                continue

            columns = list(rows[0].keys())
            placeholders = ",".join(["?"] * len(columns))
            column_list = ",".join(f'"{c}"' for c in columns)
            insert_sql = f'INSERT INTO "{table}" ({column_list}) VALUES ({placeholders})'

            data = [
                tuple(serialize_for_sqlite(row[col]) for col in columns)
                for row in rows
            ]
            sqlite_conn.executemany(insert_sql, data)
            click.echo(f"  [sqlite] {table}: {len(rows)} linhas")

    sqlite_conn.commit()

    # Indices uteis no consumidor
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_processos_parent ON processos(parent_id)',
        'CREATE INDEX IF NOT EXISTS idx_processos_nucleo ON processos(nucleo, nivel)',
        'CREATE INDEX IF NOT EXISTS idx_riscos_parent ON riscos(parent_id)',
        'CREATE INDEX IF NOT EXISTS idx_normas_status ON normas(status)',
        'CREATE INDEX IF NOT EXISTS idx_vnp_processo ON vinculo_norma_processo(processo_id)',
        'CREATE INDEX IF NOT EXISTS idx_vnp_norma ON vinculo_norma_processo(norma_id)',
        'CREATE INDEX IF NOT EXISTS idx_vpr_processo ON vinculo_processo_risco(processo_id)',
        'CREATE INDEX IF NOT EXISTS idx_vpr_risco ON vinculo_processo_risco(risco_id)',
    ]
    for idx_sql in indexes:
        sqlite_conn.execute(idx_sql)
    sqlite_conn.commit()
    sqlite_conn.close()

    size_kb = output_path.stat().st_size / 1024
    click.echo(f"\nExportado para {output_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    cli()
