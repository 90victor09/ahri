#!/usr/bin/env python3
import os
import sys
import tempfile
from pathlib import Path

from flask import request, Response
from flask import Flask
import psycopg2

if __package__ is None:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[1]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError:  # Already removed
        pass

from util import database
from util.imp_helper import create_model
from util.log import getLogger

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

conn = database.connect()
model_name = None
model = None

log = getLogger(__name__)


def _check_conn():
    global conn
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT 1")
            return True
        except psycopg2.OperationalError:
            return False


def _load_model(name):
    global model, model_name

    if not database.is_models_table_exists(conn):
        log.warning("Models table doesn't exists - skipping model loading")
        return False

    model_name = name
    with tempfile.TemporaryFile('w+b') as fp:
        model_type, dataset_version = database.retrieve_model(conn, model_name, fp)
        model = create_model(model_type)
        model.load(fp)
        log.info(f"Loaded model '{model_name}', dataset_version={dataset_version}")
        return True


if 'APP_API_KEY' not in os.environ:
    log.error("Specify APP_API_KEY env var")
    exit(1)
api_key = os.environ['APP_API_KEY']

if 'APP_DEFAULT_MODELNAME' in os.environ:
    _load_model(os.environ['APP_DEFAULT_MODELNAME'])
else:
    log.info("No model loaded, set APP_DEFAULT_MODELNAME env var")


@app.get('/healthcheck')
def healthcheck():
    global conn
    if _check_conn():
        return Response("ok", status=200, mimetype='text/plain')
    else:
        try:
            conn.close()
            conn = database.connect()
            log.warning("Reconnected to DB")
        except:
            log.error("Failed to reconnect to DB")
        return Response("db check failed", status=500, mimetype='text/plain')


@app.post('/api/models/load')
def load_model():
    params = dict(request.args)

    if 'api_key' not in params or params['api_key'] != api_key:
        return Response({"error": "Unauthorized"}, 403)

    if 'model_name' not in params:
        return Response({"error": "Param model_name is required"}, 400)

    global model_name, model
    if not _load_model(params['model_name']):
        return {"result": "failed to load model"}

    return {"result": "ok"}


@app.post('/api/classify')
def classify():
    if model is None:
        return Response({"error": "Model is not loaded"}, 500)

    params = dict(request.json)
    if 'text' not in params:
        return Response({"error": "Field text is required"}, 400)

    texts = params['text'] if type(params['text']) == list else [str(params['text'])]

    predictions = model.predict(texts)

    classes = database.retrieve_classes(conn)
    return {
        "result": [(list(classes.keys())[list(classes.values()).index(x)]) for x in predictions]
    }


if __name__ == '__main__':
    app.run()
