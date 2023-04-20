import os
import hashlib

import json

import psycopg2
import psycopg2.extras


TABLE_NAME = 'dataset'

def connect():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_DB'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn

def create_data_table(conn):
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

    #cursor.execute(f"""
    #    CREATE TABLE {TABLE_NAME} (
    #        id bigint PRIMARY KEY,
    #        link varchar(255) NOT NULL,
    #        headline varchar(255) NOT NULL,
    #        category varchar(255) NOT NULL,
    #        short_description TEXT NOT NULL,
    #        authors varchar(255) NOT NULL,
    #        date varchar(255) NOT NULL,
    #    )
    #""")
    cursor.execute(f"""
        CREATE TABLE {TABLE_NAME} (
            id bigserial PRIMARY KEY,
            data TEXT NOT NULL,
            hash varchar(255) NOT NULL UNIQUE,
            ver int NOT NULL
        )
    """)

    cursor.close()
    conn.commit()

def create_classes_table(conn):
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {CLASSES_TABLE_NAME}")

    cursor.execute(f"""
        CREATE TABLE {CLASSES_TABLE_NAME} (
            id bigint NOT NULL PRIMARY KEY,
            name varchar(255) NOT NULL
        )
    """)

    cursor.close()
    conn.commit()

def _chunkify(d, target_len=500):
    chunk = []
    for i in d:
        chunk.append(i)
        if len(chunk) >= target_len:
            yield chunk
            chunk = []

def get_last_version(cursor):
    cursor.execute(f'SELECT MAX(ver) FROM {TABLE_NAME}')
    return cursor.fetchone()[0] or 0

def save_data(conn, data):
    with conn.cursor() as cursor:
        current_version = get_last_version(cursor) + 1
        
        for chunk in _chunkify(data):
            psycopg2.extras.execute_values(
                cursor,
                f"INSERT INTO {TABLE_NAME} (data, hash, ver) VALUES %s ON CONFLICT DO NOTHING",
                [(json.dumps(i), hashlib.md5(json.dumps(i).encode('utf-8')).digest().hex(), current_version) for i in chunk]
            )
            conn.commit()
    

def retrieve_data(conn, version=None, chunk_size=500):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT id, data, hash, ver FROM {TABLE_NAME}' + ('' if version is None else f' WHERE ver = {version}'))
        yield cursor.fetchmany(chunk_size)



def save_classes(conn, classes_dict):
    with conn.cursor() as cursor:
        cursor = conn.cursor()

        psycopg2.extras.execute_values(
            cursor,
            f"INSERT INTO {CLASSES_TABLE_NAME} (id, name) VALUES %s",
            [(k, v) for k,v in classes_dict]
        )

    conn.commit()

def retrieve_classes(conn):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT id, name FROM {CLASSES_TABLE_NAME}')
        return {
            k: v for k,v in cursor.fetchall()
        }

