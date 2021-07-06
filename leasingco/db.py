import pyodbc

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(
            DRIVER = '{ODBC Driver 17 for SQL Server}',
            SERVER = current_app.config['DBSERVER_NAME'],
            DATABASE = current_app.config['DATABASE_NAME'],
            Trusted_Connection = 'yes',
            autocommit = True
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    print(db)
    cursor = g.db.cursor()
    for row in cursor.columns(table='FinanceResults'):
        print(row.column_name)
    # Пока БД не инициализируем, просто проверка подключения
    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Очищает существующие данные и создает новые таблицы."""
    # Пока ничего не делает, просто проверка
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)