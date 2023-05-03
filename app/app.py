#!/usr/bin/env python3
import os
import resource
import signal
import sys
import tempfile
from pathlib import Path

from flask import request, Response
from flask import Flask
import psycopg2

from util import database
from util.imp_helper import create_model
from util.log import getLogger

# cgroups OOM fix
if os.path.isfile('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
    with open('/sys/fs/cgroup/memory/memory.limit_in_bytes') as limit:
        mem = int(limit.read())
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))


if __package__ is None:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[1]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError:  # Already removed
        pass


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

model_name = None
model = None

log = getLogger(__name__)

STANDALONE = False


def _load_model(name):
    global model, model_name

    with database.connect() as conn:
        if not database.models.is_models_table_exists(conn):
            log.warning("Models table doesn't exists - skipping model loading")
            return False

        model_name = name
        with tempfile.TemporaryFile('w+b') as fp:
            model_type, dataset_version = database.models.retrieve_model(conn, model_name, fp)
            model = create_model(model_type)
            model.load(fp)
            log.info(f"Loaded model '{model_name}', dataset_version={dataset_version}")
            return True


def _trigger_uwsgi_reload():
    import uwsgi
    # parent_pid = os.getppid()
    # log.info(f"UWSGI ID: {parent_pid}")
    # os.kill(parent_pid, signal.SIGHUP)
    uwsgi.reload()


if 'APP_API_KEY' not in os.environ:
    log.error("Specify APP_API_KEY env var")
    exit(1)
api_key = os.environ['APP_API_KEY']

with database.connect() as conn:
    database.settings.create_settings_table(conn)
    deployed_model = database.settings.get_setting(conn, database.settings.DEPLOYED_MODEL_NAME_KEY)
    if not deployed_model:
        log.info("No model deployed")
    else:
        try:
            _load_model(deployed_model)
        except:
            model_name = None
            model = None
            log.error(f"Failed to load deployed model '{deployed_model}'")
    del deployed_model


@app.get('/healthcheck')
def healthcheck():
    def _check_conn():
        with database.connect() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1")
                    return True
                except psycopg2.OperationalError:
                    return False

    if _check_conn():
        return Response("ok", status=200, mimetype='text/plain')
    else:
        log.error("Failed to check DB connection")
        return Response("db check failed", status=500, mimetype='text/plain')


@app.post('/api/models/load')
def load_model():
    params = dict(request.args)

    if 'api_key' not in params or params['api_key'] != api_key:
        return Response({"error": "Unauthorized"}, 403)

    if 'model_name' not in params:
        return Response({"error": "Param model_name is required"}, 400)

    global model_name, model

    # should check model before saving & reloading
    if not _load_model(params['model_name']):
        return {"result": "failed to load model"}

    with database.connect() as conn:
        database.settings.set_setting(conn, database.settings.DEPLOYED_MODEL_NAME_KEY, model_name)

    if not STANDALONE:
        _trigger_uwsgi_reload()

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

    with database.connect() as conn:
        classes = database.classes.retrieve_classes(conn)

    return {
        "result": [(list(classes.keys())[list(classes.values()).index(x)]) for x in predictions]
    }


if __name__ == '__main__':
    STANDALONE = True
    log.info("Single mode")
    app.run()
