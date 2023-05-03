import json

from .util import is_table_exists

MODELS_TABLE_NAME = 'models'


class ModelNotFoundException(Exception):
    pass


def is_models_table_exists(conn):
    return is_table_exists(conn, MODELS_TABLE_NAME)


def create_models_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {MODELS_TABLE_NAME} (
                id bigserial PRIMARY KEY,
                name varchar(255) NOT NULL,
                type varchar(255) NOT NULL,
                params TEXT NOT NULL,
                dataset_version bigint NOT NULL,
                data bytea NOT NULL,
                CONSTRAINT models_uniq UNIQUE (name, dataset_version)
            )
        """)
    conn.commit()


def save_model(conn, model_type, name, params, dataset_version, file):
    file.seek(0)
    with conn.cursor() as cursor:
        cursor.execute(f'INSERT INTO {MODELS_TABLE_NAME}(name, type, params, dataset_version, data) VALUES (%s, %s, %s, %s, %s)', (name, model_type, json.dumps(params), dataset_version, file.read()))
    conn.commit()


def get_model_dataset_version(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(f'SELECT MAX(dataset_version) FROM {MODELS_TABLE_NAME} WHERE name = %s', (name,))
        return cursor.fetchone()[0] or None


def retrieve_model(conn, name, file, dataset_version=None):
    file.seek(0)
    with conn.cursor() as cursor:
        if dataset_version is not None:
            cursor.execute(f'SELECT type, data, dataset_version FROM {MODELS_TABLE_NAME} WHERE name = %s AND dataset_version = %s', (name, dataset_version))
        else:
            cursor.execute(f'SELECT type, data, dataset_version FROM {MODELS_TABLE_NAME} WHERE name = %s ORDER BY dataset_version DESC LIMIT 1', (name,))

        ret = cursor.fetchall()
        if len(ret) == 0:
            raise ModelNotFoundException(f"Model with name={name} not found")
        ret = ret[0]

        model_type = ret[0]
        data = ret[1]
        dataset_version = ret[2]
        file.write(data)

    conn.commit()
    return model_type, dataset_version
