#!/usr/bin/env python3

import sys

from util import database
from util.data import json_lines_parser

# noinspection DuplicatedCode
if __name__ != '__main__':
    exit(1)

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} SRC_PATH [recreate]")
    exit(0)


src_path = sys.argv[1]
recreate = True if len(sys.argv) == 3 and sys.argv[2] == 'true' else False

with database.connect() as conn:
    classes = database.classes.retrieve_classes(conn)

    def process_data():
        i = max(classes.values() or [0]) + 1
        for obj in json_lines_parser(src_path):
            yield obj
            if obj['category'] in classes:
                continue
            classes[obj['category']] = i
            i += 1

    if not database.dataset.is_data_table_exists(conn) or recreate:
        database.dataset.create_data_table(conn)
    if not database.classes.is_classes_table_exists(conn) or recreate:
        database.classes.create_classes_table(conn)
    database.dataset.save_data(conn, process_data())
    # print(classes)
    database.classes.save_classes(conn, classes)
