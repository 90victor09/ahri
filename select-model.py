#!/usr/bin/env python3
import sys

from util import database
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


with database.connect() as conn:
    if not database.metrics.is_metrics_table_exists(conn):
        log.warning("No metrics table - skip")
        exit(0)

    model_data = []

    for model_name in model_names:
        versions = database.models.get_model_versions_with_model_ids(conn, model_name)
        metrics = database.metrics.retrieve_metrics(conn, list(versions.keys()))

        for dataset_version, model_id in versions.items():
            if not metrics.get(model_id, None):
                log.info(f'No metrics for model_id={model_id} name={model_name} - skip.')
                continue
            data = {
                'model_id': model_id,
                'model_name': model_name,
                'dataset_version': dataset_version,
                'adjusted_score': None,
                'metrics': metrics[model_id],
            }

            if data['metrics'].get('accuracy', None) and data['metrics'].get('time', None):
                data['adjusted_score'] = data['metrics']['accuracy'] * 10 - data['metrics']['time'] / 10

            model_data.append(data)

    log.info(f"Adjusted scores: {model_data}")

    best_model = max(model_data, key=lambda x: x['adjusted_score']) if len(model_data) > 0 else None
    if not best_model:
        log.warning("Not enough scores to make a decision")
        exit(0)

    log.info(f"Best model params: {best_model}")
    log.info(f"Best model id: {best_model['model_id']}")
