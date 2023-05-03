import hashlib
import json
from functools import partial

import psycopg2.extras

from util import database
from util.data import chunkify, chunk_to_labelresult_pair, flatmap
from .util import is_table_exists

DATASET_TABLE_NAME = 'dataset'


def is_data_table_exists(conn):
    return is_table_exists(conn, DATASET_TABLE_NAME)


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


def retrieve_data_chunks(conn, version=None, chunk_size=5000):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT id, data, hash, ver FROM {DATASET_TABLE_NAME}' + ('' if version is None else f' WHERE ver = {version}'))

        while True:
            data = cursor.fetchmany(chunk_size)
            if not data:
                break
            yield data


def retrieve_full_dataset(conn, classes):
    return map(partial(chunk_to_labelresult_pair, classes), flatmap(database.dataset.retrieve_data_chunks(conn)))
