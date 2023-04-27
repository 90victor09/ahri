#!/usr/bin/env python3

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

import sys

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} MODEL_NAME [dataset_version]")
    exit(0)

model_name = sys.argv[1]
dataset_version = None
if len(sys.argv) > 2:
    dataset_version = sys.argv[2]

import tempfile
import json

from util.imp_helper import import_class
from util import database

with database.connect() as conn:
    classes = database.retrieve_classes(conn)

    if not database.is_models_table_exists(conn):
        database.create_models_table(conn)

    model = import_class(f'models.{model_name}')()

    if dataset_version is None:
        with conn.cursor() as cursor:
            dataset_version = database.get_last_dataset_version(cursor)

    current_dataset_version = database.get_model_dataset_version(conn, model_name)
    if current_dataset_version is not None:
        with tempfile.TemporaryFile('wb') as fp:
            trained_dataset_version = database.retrieve_model(conn, model_name, fp, None)
            if trained_dataset_version >= dataset_version:
                print("Model already trained on these dataset (%s >= %s)" % (trained_dataset_version, dataset_version))
                exit(0)

            model.load(fp)
    else:
        model.create_new()

    for chunk in database.retrieve_data_chunks(conn, dataset_version):
        X, y = [], []

        for id, data, hash, ver in chunk:
            obj = json.loads(data)
            X.append(obj['short_description'])
            y.append(list(classes.keys())[list(classes.values()).index(obj['category'])])

        model.train(X, y)

    with tempfile.TemporaryFile('wb') as fp:
        model.save(fp)
        database.save_model(conn, model_name, dataset_version, fp)
