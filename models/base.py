
from util.data import compress_pickle, decompress_pickle


class BaseModel:
    def __init__(self):
        self.classifier = None

    def create_new(self):
        pass

    def load(self, fp):
        self.classifier = decompress_pickle(fp.read())

    def save(self, fp):
        fp.write(compress_pickle(self.classifier))

    def train(self, X, y):
        self.classifier.fit(X, y)

    def predict(self, X):
        self.predict(X)
