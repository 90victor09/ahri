#!/usr/bin/env python3

if __name__ != '__main__':
    exit(1)

import sys

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} SRC_PATH")
    exit(0)

import json
from util import database
from util.json import lines_parser

src_path = sys.argv[1]

with database.connect() as conn:
    database.create_data_table(conn)
    database.save_data(conn, lines_parser(src_path))

    classes = {}
    i = 1
    for obj in lines_parser(src_path):
        if obj['category'] in classes:
            continue
        classes[obj['category']] = i
        i += 1

    database.save_classes(conn, classes)

