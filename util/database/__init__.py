import os

import psycopg2

from . import classes
from . import dataset
from . import models
from . import settings
from .util import is_table_exists


def connect():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_DB'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn
