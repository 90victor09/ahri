#!/usr/bin/env python3
import json
import tempfile
import sys
from functools import partial

from util.data import chunk_to_labelresult_pair, flatmap
from util.imp_helper import create_model
from util.log import getLogger
from util import database

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

if len(sys.argv) < 3:
    print(f"{sys.argv[0]} MODEL_TYPE MODEL_NAME [dataset_version=0] [params]")
    exit(0)

model_type = sys.argv[1]
model_name = sys.argv[2]
dataset_version = None
model_params = {}

if len(sys.argv) > 3:
    dataset_version = int(sys.argv[3])

if dataset_version is not None and dataset_version < 1:
    dataset_version = None

if len(sys.argv) > 4:
    model_params = json.loads(sys.argv[4])


log = getLogger(__name__)

with database.connect() as conn:
    classes = database.classes.retrieve_classes(conn)

    if not database.models.is_models_table_exists(conn):
        database.models.create_models_table(conn)

    model = create_model(model_type)

    if dataset_version is None:
        with conn.cursor() as cursor:
            dataset_version = database.dataset.get_last_dataset_version(cursor)

    trained_dataset_version = 1
    current_dataset_version = database.models.get_model_dataset_version(conn, model_name)
    if current_dataset_version is not None:
        with tempfile.TemporaryFile('w+b') as fp:
            trained_model_type, trained_dataset_version = database.models.retrieve_model(conn, model_name, fp, None)
            if model_type != trained_model_type:
                log.error(f"Trained model has type {trained_model_type} != {model_type}")
                exit(1)
            if trained_dataset_version >= dataset_version:
                log.info("Model already trained on these dataset versions (%s >= %s)" % (trained_dataset_version, dataset_version))
                exit(0)

            model.load(fp)
            log.info("Loaded existing model")
    else:
        model.create_new(model_params)
        log.info(f"Creating new model type={model_type} with params={model_params}")

    X, y = [], []
    for dver in range(trained_dataset_version, dataset_version+1):
        log.info(f"Loading dataset version={dver}")
        for _x, _y in map(partial(chunk_to_labelresult_pair, classes), flatmap(database.dataset.retrieve_data_chunks(conn, dver))):
            X.append(_x)
            y.append(_y)

    log.info(f"Starting pretraining model")
    # model.pre_train(X, y)
    log.info(f"Starting training model")
    model.train(X, y)

    log.info(f"Saving model type={model_type} name={model_name}")
    with tempfile.TemporaryFile('w+b') as fp:
        model.save(fp)
        database.models.save_model(conn, model_type, model_name, model_params, dataset_version, fp)
