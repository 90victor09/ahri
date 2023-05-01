import json
import pickle

import zstandard as zstd


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


def flatmap(d):
    for chunk in d:
        for x in chunk:
            yield x


def chunk_to_labelresult_pair(classes, chunk):
    _id, data, _hash, ver = chunk
    obj = json.loads(data)
    return obj['short_description'], classes[obj['category']]


def compress_pickle(obj):
    return zstd.compress(pickle.dumps(obj, protocol=5))


def decompress_pickle(s):
    return pickle.loads(zstd.decompress(s))
