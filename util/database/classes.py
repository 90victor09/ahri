import psycopg2.extras

from .util import is_table_exists


CLASSES_TABLE_NAME = 'classes'


def is_classes_table_exists(conn):
    return is_table_exists(conn, CLASSES_TABLE_NAME)


def create_classes_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {CLASSES_TABLE_NAME} (
                id bigint NOT NULL PRIMARY KEY,
                name varchar(255) NOT NULL,
                CONSTRAINT classes_uniq UNIQUE (id, name)
            )
        """)
    conn.commit()


def save_classes(conn, classes_dict):
    with conn.cursor() as cursor:
        psycopg2.extras.execute_values(
            cursor,
            f"INSERT INTO {CLASSES_TABLE_NAME} (id, name) VALUES %s ON CONFLICT ON CONSTRAINT classes_uniq DO NOTHING;",
            [(idx, name) for name, idx in classes_dict.items()]
        )
    conn.commit()


def retrieve_classes(conn):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT id, name FROM {CLASSES_TABLE_NAME}')
        return {name: idx for idx, name in cursor.fetchall()}
