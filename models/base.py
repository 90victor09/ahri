import random
import sys

from util.data import compress_pickle, decompress_pickle


class BaseModel:
    def __init__(self):
        self.classifier = None

    def create_new(self, model_params):
        pass

    def load(self, fp):
        fp.seek(0)
        self.classifier = decompress_pickle(fp.read())

    def save(self, fp):
        fp.seek(0)
        fp.write(compress_pickle(self.classifier))

    # noinspection PyMethodMayBeStatic
    def pre_train(self, X, y):
        return X, y

    def train(self, X, y):
        self.classifier.fit(X, y)

    def predict(self, X):
        return self.classifier.predict(X)
