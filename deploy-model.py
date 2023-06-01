#!/usr/bin/env python3

import os
import sys

import requests

from util.log import getLogger

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

log = getLogger(__name__)

if 'APP_API_BASE' not in os.environ:
    log.error("APP_API_BASE env var should be specified")
    exit(1)

if 'APP_API_KEY' not in os.environ:
    log.error("APP_API_KEY env var should be specified")
    exit(1)


if len(sys.argv) < 2:
    print(f"{sys.argv[0]} MODEL_NAME")
    exit(1)

api_base = os.environ['APP_API_BASE'].rstrip('/')
api_key = os.environ['APP_API_KEY']

model_id = sys.argv[1]

resp = requests.post(f"{api_base}/api/models/load", params={
    'api_key': api_key,
    'model_id': model_id
})

data = resp.json()
if resp.status_code != 200:
    log.error(f"Failed to deploy model: {data['error']}")
    exit(1)

assert(data['result'] == 'ok')

log.info("Model deployed successfully")
