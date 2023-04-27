import json
import pickle

import zstandard

def json_lines_parser(path):
    with open(path, 'r') as fp:
        for line in fp:
            obj = json.loads(line)
            yield obj


def chunkify(d, target_len=500):
    chunk = []
    for i in d:
        chunk.append(i)
        if len(chunk) >= target_len:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk


def compress_pickle(obj):
    zstandard.compress(pickle.dumps(obj))


def decompress_pickle(s):
    return zstandard.decompress(pickle.loads(s))
