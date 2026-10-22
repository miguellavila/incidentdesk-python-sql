"""Incident tracker CLI for a local SQLite database; no network dependencies."""
from __future__ import annotations

import argparse
import html
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name('schema.sql')
SEVERITIES = ('low', 'medium', 'high', 'critical')
STATUSES = ('open', 'investigating', 'resolved')


def connect(database: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA.read_text(encoding='utf-8'))
    connection.commit()


def add_incident(connection: sqlite3.Connection, title: str, severity: str, notes: str = '') -> int:
    if not title.strip():
        raise ValueError('O título não pode estar vazio')
    if severity not in SEVERITIES:
        raise ValueError('Severidade inválida')
    with connection:
        cursor = connection.execute(
            'INSERT INTO incidents (title, severity, notes) VALUES (?, ?, ?)',
            (title.strip(), severity, notes),
        )
    return int(cursor.lastrowid)


def update_status(connection: sqlite3.Connection, incident_id: int, status: str) -> bool:
    if status not in STATUSES:
        raise ValueError('Status inválido')
    with connection:
        cursor = connection.execute('UPDATE incidents SET status=? WHERE id=?', (status, incident_id))
    return cursor.rowcount > 0


def list_incidents(connection: sqlite3.Connection, status: str | None = None) -> list[sqlite3.Row]:
    if status is not None and status not in STATUSES:
        raise ValueError('Status inválido')
    return connection.execute(
        'SELECT * FROM incidents WHERE (? IS NULL OR status = ?) ORDER BY id DESC',
        (status, status),
    ).fetchall()


def html_report(records: list[sqlite3.Row]) -> str:
    rows = '\n'.join(
        '<tr>' + ''.join(f'<td>{html.escape(str(row[key]), quote=True)}</td>'
                            for key in ('id', 'title', 'severity', 'status', 'created_at', 'notes')) + '</tr>'
        for row in records
    )
    return ('<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
            '<title>Incidentes de Segurança</title><style>'
            'body{font:16px system-ui;margin:3rem auto;max-width:1100px;padding:0 1rem}'
            'table{width:100%;border-collapse:collapse}th,td{padding:.7rem;border:1px solid #ddd;text-align:left}'
            'th{background:#eee}tr:nth-child(even){background:#f7f7f7}</style>'
            '<h1>Incidentes de Segurança</h1><table><thead><tr>'
            '<th>ID</th><th>Título</th><th>Severidade</th><th>Status</th>'
            '<th>Criado em</th><th>Notas</th></tr></thead><tbody>'
            + rows + '</tbody></table></html>')


def main() -> int:
    parser = argparse.ArgumentParser(description='Gerenciador local de incidentes')
    parser.add_argument('--db', type=Path, default=Path('incidents.db'))
    sub = parser.add_subparsers(dest='command', required=True)
    add = sub.add_parser('add', help='Cadastrar incidente')
    add.add_argument('title')
    add.add_argument('--severity', required=True, choices=SEVERITIES)
    add.add_argument('--notes', default='')
    listing = sub.add_parser('list', help='Listar incidentes')
    listing.add_argument('--status', choices=STATUSES)
    update = sub.add_parser('status', help='Atualizar status')
    update.add_argument('id', type=int)
    update.add_argument('value', choices=STATUSES)
    export = sub.add_parser('export', help='Gerar relatório HTML local')
    export.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        with connect(args.db) as conn:
            initialize(conn)
            if args.command == 'add':
                print('Incidente criado:', add_incident(conn, args.title, args.severity, args.notes))
            elif args.command == 'list':
                for row in list_incidents(conn, args.status):
                    print(f"#{row['id']} [{row['severity']}] {row['status']}: {row['title']}")
            elif args.command == 'status':
                if not update_status(conn, args.id, args.value):
                    parser.error('Incidente não encontrado')
                print('Status atualizado')
            elif args.command == 'export':
                args.output.write_text(html_report(list_incidents(conn)), encoding='utf-8')
                print('Relatório salvo em:', args.output)
    except (OSError, sqlite3.Error, ValueError) as exc:
        parser.exit(1, f'Erro: {exc}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
