import os
import hashlib

import json

import psycopg2
import psycopg2.extras

from .data import chunkify


DATASET_TABLE_NAME = 'dataset'
CLASSES_TABLE_NAME = 'classes'
MODELS_TABLE_NAME = 'models'


def connect():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_DB'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn


def is_table_exists(conn, tablename):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM information_schema.tables WHERE table_name=%s", (tablename,))
        return bool(cursor.rowcount)


def is_data_table_exists(conn):
    return is_table_exists(conn, DATASET_TABLE_NAME)


def is_classes_table_exists(conn):
    return is_table_exists(conn, CLASSES_TABLE_NAME)


def is_models_table_exists(conn):
    return is_table_exists(conn, MODELS_TABLE_NAME)


def create_data_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {DATASET_TABLE_NAME}")

        cursor.execute(f"""
            CREATE TABLE {DATASET_TABLE_NAME} (
                id bigserial PRIMARY KEY,
                data TEXT NOT NULL,
                hash varchar(255) NOT NULL UNIQUE,
                ver int NOT NULL
            )
        """)
    conn.commit()


def get_last_dataset_version(cursor):
    cursor.execute(f'SELECT MAX(ver) FROM {DATASET_TABLE_NAME}')
    return cursor.fetchone()[0] or 0


def save_data(conn, data):
    with conn.cursor() as cursor:
        current_version = get_last_dataset_version(cursor) + 1

        for chunk in chunkify(data, target_len=2000):
            psycopg2.extras.execute_values(
                cursor,
                f"INSERT INTO {DATASET_TABLE_NAME} (data, hash, ver) VALUES %s ON CONFLICT DO NOTHING",
                [(
                    json.dumps(i, sort_keys=True),
                    hashlib.md5(json.dumps(i, sort_keys=True).encode('utf-8')).digest().hex(),
                    current_version
                ) for i in chunk]
            )
            conn.commit()


def retrieve_data_chunks(conn, version=None, chunk_size=500):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT id, data, hash, ver FROM {DATASET_TABLE_NAME}' + ('' if version is None else f' WHERE ver = {version}'))

        while True:
            data = cursor.fetchmany(chunk_size)
            if not data:
                break
            yield data


def create_classes_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {CLASSES_TABLE_NAME} (
                id bigint NOT NULL PRIMARY KEY,
                name varchar(255) NOT NULL
            )
        """)
    conn.commit()


def save_classes(conn, classes_dict):
    with conn.cursor() as cursor:
        psycopg2.extras.execute_values(
            cursor,
            f"INSERT INTO {CLASSES_TABLE_NAME} (id, name) VALUES %s",
            [(idx, name) for name, idx in classes_dict.items()]
        )
    conn.commit()


def retrieve_classes(conn):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT id, name FROM {CLASSES_TABLE_NAME}')
        return {name: idx for idx, name in cursor.fetchall()}


def create_models_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {MODELS_TABLE_NAME} (
                id bigserial PRIMARY KEY,
                name varchar(255) NOT NULL,
                dataset_version bigint NOT NULL,
                data bytea NOT NULL
            )
        """)
    conn.commit()


def save_model(conn, name, dataset_version, file):
    file.seek(0)
    with conn.cursor() as cursor:
        cursor.execute(f'INSERT INTO {MODELS_TABLE_NAME}(name, dataset_version, data) VALUES (%s, %s, %s)', (name, dataset_version, file.read()))
    conn.commit()


def get_model_dataset_version(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(f'SELECT MAX(dataset_version) FROM {MODELS_TABLE_NAME} WHERE name = %s', (name,))
        return cursor.fetchone()[0] or None


def retrieve_model(conn, name, file, dataset_version=None):
    file.seek(0)
    with conn.cursor() as cursor:
        if dataset_version is not None:
            cursor.execute(f'SELECT data, dataset_version FROM {MODELS_TABLE_NAME} WHERE name = %s AND dataset_version = %s', (name, dataset_version))
        else:
            cursor.execute(f'SELECT data, dataset_version FROM {MODELS_TABLE_NAME} WHERE name = %s ORDER BY dataset_version DESC LIMIT 1', (name,))

        ret = cursor.fetchall()[0]
        data = ret[0]
        dataset_version = ret[1]
        file.write(data)

    conn.commit()
    return dataset_version
