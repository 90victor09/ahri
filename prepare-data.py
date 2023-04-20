#!/usr/bin/env python3

if __name__ != '__main__':
    exit(1)

import sys

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} SRC_PATH DST_PATH")
    exit(0)


import shutil

import json

from util.json import lines_parser
from util.text_preprocess import *

src_path = sys.argv[1]
dst_path = sys.argv[2]


with open(dst_path, 'w') as dst:
    for obj in lines_parser(src_path):
        if not obj['short_description'] or not obj['category']:
            continue

        pipeline = [
            lambda x: str(x).lower(),
            replace_chars,
            remove_shortforms,
            trim_punctuation,
            #remove_stopwords,
        ]

        for transform in pipeline:
            obj['short_description'] = transform(obj['short_description'])
        
        dst.write(json.dumps(obj) + "\n")



