import json

import psycopg2.extras

from .util import is_table_exists


METRICS_TABLE_NAME = 'models_metrics'


def is_metrics_table_exists(conn):
    return is_table_exists(conn, METRICS_TABLE_NAME)


def create_metrics_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {METRICS_TABLE_NAME} (
                id bigint NOT NULL PRIMARY KEY,
                model_id BIGINT NOT NULL REFERENCES models(id),
                metrics TEXT NOT NULL,
                CONSTRAINT metrics_uniq UNIQUE (model_id)
            )
        """)
    conn.commit()


def save_metrics(conn, model_id, metrics_dict):
    with conn.cursor() as cursor:
        psycopg2.extras.execute_values(
            cursor,
            f"INSERT INTO {METRICS_TABLE_NAME} (model_id, metrics) VALUES %s ON CONFLICT ON CONSTRAINT metrics_uniq DO UPDATE SET metrics = EXCLUDED.metrics;",
            [(model_id, json.dumps(metrics_dict, sort_keys=True))]
        )
    conn.commit()


def retrieve_metrics(conn, model_ids):
    with conn.cursor(name='retrieve') as cursor:
        cursor.execute(f'SELECT model_id, metrics FROM {METRICS_TABLE_NAME} WHERE model_id IN %s', (tuple(model_ids),))
        return {model_id: json.loads(metrics_json) for model_id, metrics_json in cursor.fetchall()}

