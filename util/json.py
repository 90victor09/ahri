import json

def lines_parser(path):
    with open(path, 'r') as fp:
        for line in fp:
            obj = json.loads(line)
            yield obj


