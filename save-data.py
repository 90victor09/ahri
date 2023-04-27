#!/usr/bin/env python3

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

import sys

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} SRC_PATH [recreate]")
    exit(0)

from util import database
from util.data import json_lines_parser

src_path = sys.argv[1]
recreate = True if len(sys.argv) == 3 and sys.argv[2] == 'true' else False

with database.connect() as conn:
    classes = {}

    def process_data():
        i = 1
        for obj in json_lines_parser(src_path):
            yield obj
            if obj['category'] in classes:
                continue
            classes[obj['category']] = i
            i += 1

    if not database.is_data_table_exists(conn) or recreate:
        database.create_data_table(conn)
    database.save_data(conn, process_data())
    database.save_classes(conn, classes)

