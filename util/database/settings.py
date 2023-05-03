import psycopg2.extras

from .util import is_table_exists


SETTINGS_TABLE_NAME = 'settings'

DEPLOYED_MODEL_NAME_KEY = 'deployed_model'


def is_settings_table_exists(conn):
    return is_table_exists(conn, SETTINGS_TABLE_NAME)


def create_settings_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {SETTINGS_TABLE_NAME} (
                key varchar(255) NOT NULL UNIQUE,
                value TEXT NOT NULL,
                CONSTRAINT settings_key_uniq UNIQUE (key)
            )
        """)
    conn.commit()


def set_setting(conn, key, value):
    with conn.cursor() as cursor:
        psycopg2.extras.execute_values(
            cursor,
            f"INSERT INTO {SETTINGS_TABLE_NAME} (key, value) VALUES %s ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;",
            [(key, value)]
        )
    conn.commit()


def get_setting(conn, key):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT value FROM {SETTINGS_TABLE_NAME} WHERE key = %s', (key,))
        ret = cursor.fetchall()
        if len(ret) == 0:
            return None
        return ret[0][0]
