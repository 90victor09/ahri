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

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} QUERY [...]")
    exit(1)

api_base = os.environ['APP_API_BASE'].rstrip('/')

queries = sys.argv[1::]

resp = requests.post(f"{api_base}/api/classify", json={
    'text': queries
})

data = resp.json()
if resp.status_code != 200:
    log.error(f"Failed to send query: {data['error']}")
    exit(1)

log.info(f"Response: {data['result']}")
