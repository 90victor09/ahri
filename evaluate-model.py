#!/usr/bin/env python3
import tempfile
import time
import sys
from functools import partial

from sklearn import metrics

from util import database
from util.imp_helper import create_model
from util.log import getLogger

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} MODEL_NAME [...]")
    exit(0)

model_names = list(sys.argv)
model_names = model_names[1:]

log = getLogger(__name__)


# def get_data_generators(classes):
#     src_gen = map(partial(chunk_to_labelresult_pair, classes), flatmap(database.retrieve_data_chunks(conn)))
#     X, y = itertools.tee(src_gen, 2)
#     return map(lambda x: x[0], X), map(lambda x: x[0], y)


with database.connect() as conn:
    X, y_true = [], []
    classes = database.classes.retrieve_classes(conn)

    if not database.metrics.is_metrics_table_exists(conn):
        database.metrics.create_metrics_table(conn)

    log.info(f"Started loading complete dataset")
    for _x, _y in database.dataset.retrieve_full_dataset(conn, classes):
        X.append(_x)
        y_true.append(_y)
    log.info(f"Completed loading dataset")

    scoring = {
        'accuracy': metrics.accuracy_score,
        'precision': partial(metrics.precision_score, average='weighted'),
        'recall': partial(metrics.recall_score, average='weighted'),
    }

    model_scores = {}

    for model_name in model_names:
        for dataset_version in database.models.get_model_dataset_versions(conn, model_name):
            with tempfile.TemporaryFile('w+b') as fp:
                try:
                    model_type, trained_dataset_version, model_id = database.models.retrieve_model(conn, model_name, fp,
                                                                                                   dataset_version)
                except database.models.ModelNotFoundException:
                    log.warning(f"Model '{model_name}' (dataset version {dataset_version}) not found")
                    continue

                model = create_model(model_type)
                model.load(fp)

                log.info(f"Evaluating {model_name} (model_id = {model_id}, dataset version {dataset_version})")
                start = time.time()

                y_pred = model.predict(X)

                end = time.time()
                dur = end - start

                scores = {'time': dur}
                for name, scorer in scoring.items():
                    scores[name] = scorer(y_true, y_pred)

                log.info(f"Model {model_name} (model_id = {model_id}, version {dataset_version}), time: {dur}, scores: {scores}")
                model_scores[model_id] = model_scores.get(model_id, {})
                model_scores[model_id][dataset_version] = scores

        if model_scores.get(model_id, None):
            database.metrics.save_metrics(conn, model_id, model_scores[model_id])

    log.info("All models has been evaluated")
