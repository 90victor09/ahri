#!/usr/bin/env python3
import itertools
import time
from functools import partial

from sklearn import metrics

from util.data import flatmap, chunk_to_labelresult_pair
from util.imp_helper import create_model
from util.log import getLogger

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

import sys

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} MODEL_NAME [...]")
    exit(0)

model_names = list(sys.argv)
model_names = model_names[1:]

import tempfile

from util import database

log = getLogger(__name__)


# def get_data_generators(classes):
#     src_gen = map(partial(chunk_to_labelresult_pair, classes), flatmap(database.retrieve_data_chunks(conn)))
#     X, y = itertools.tee(src_gen, 2)
#     return map(lambda x: x[0], X), map(lambda x: x[0], y)


with database.connect() as conn:
    X, y_true = [], []
    classes = database.retrieve_classes(conn)

    log.info(f"Started loading complete dataset")
    for _x, _y in map(partial(chunk_to_labelresult_pair, classes), flatmap(database.retrieve_data_chunks(conn))):
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
        with tempfile.TemporaryFile('w+b') as fp:
            try:
                model_type, trained_dataset_version = database.retrieve_model(conn, model_name, fp, None)
            except database.ModelNotFoundException:
                log.warning(f"Model '{model_name}' not found")
                continue

            model = create_model(model_type)
            model.load(fp)

            log.info(f"Evaluating {model_name}")
            start = time.time()

            y_pred = model.predict(X)

            end = time.time()
            dur = end - start

            scores = {'time': dur}
            for name, scorer in scoring.items():
                scores[name] = scorer(y_true, y_pred)

            log.info(f"Model {model_name}, time: {dur}, scores: {scores}")
            model_scores[model_name] = scores

    # model_scores = {
    #     'tfidf_ovr_svc': {'accuracy': 0.8119054586008713, 'precision': 0.8203614280319834, 'recall': 0.8119054586008713, 'time': 1.3974192142486572},
    #     'tfidf_dt': {'accuracy': 0.39318820496115986, 'precision': 0.38545765407461896, 'recall': 0.39318820496115986, 'time': 1.2614936828613281},
    #     'tfidf_svc': {'accuracy': 0.8119054586008713, 'precision': 0.8203614280319834, 'recall': 0.8119054586008713, 'time': 1.2259268760681152},
    #     'tfidf_nb': {'accuracy': 0.3829357301782727, 'precision': 0.564694677512381, 'recall': 0.3829357301782727, 'time': 1.335000991821289}
    # }

    if len(model_scores.values()) == 0:
        log.warning("Not enough scores to make a decision")
        exit(0)

    max_time = max(map(lambda x: x['time'], model_scores.values()))

    adjusted_scores = {
        k: (v['accuracy'] * (max_time - v['time']) / max_time) for k, v in model_scores.items()
    }

    log.info(f"Adjusted scores: {adjusted_scores}")

    best_model = max(adjusted_scores.items(), key=lambda x: x[1])
    log.info(f"Best model: {best_model}")



