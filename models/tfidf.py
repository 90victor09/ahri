from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from .base import BaseModel


class TfIdfModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.vectorizer = None
        self.classifier = None

    def create_new(self, model_params):
        self.vectorizer = TfidfVectorizer()
        pass

    def pre_train(self, X, y):
        return self.vectorizer.fit_transform(X), y


class SVCModel(TfIdfModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self, model_params):
        super().create_new(model_params)
        self.classifier = Pipeline([
            ('vectorizer_tfidf', self.vectorizer),
            ('LinearSVC',  LinearSVC())
        ])
        self.classifier.set_params(**model_params)


class OneVsRestSVCModel(TfIdfModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self, model_params):
        super().create_new(model_params)
        self.classifier = Pipeline([
            ('vectorizer_tfidf', self.vectorizer),
            ('OneVsRest',  OneVsRestClassifier(LinearSVC()))
        ])
        self.classifier.set_params(**model_params)


# Hangs on prediction :(
class KNNModel(TfIdfModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self, model_params):
        super().create_new(model_params)
        self.classifier = Pipeline([
            ('vectorizer_tfidf', self.vectorizer),
            ('KNN',  KNeighborsClassifier())
        ])
        self.classifier.set_params(**model_params)


class MultinomialNBModel(TfIdfModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self, model_params):
        super().create_new(model_params)
        self.classifier = Pipeline([
            ('vectorizer_tfidf', self.vectorizer),
            ('MultinomialNB',  MultinomialNB())
        ])
        self.classifier.set_params(**model_params)


class DecisionTreeClassifierModel(TfIdfModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self, model_params):
        super().create_new(model_params)
        self.classifier = Pipeline([
            ('vectorizer_tfidf', self.vectorizer),
            ('DecisionTreeClassifier', DecisionTreeClassifier())
        ])
        self.classifier.set_params(**model_params)


# Fitting too long?
class RandomForestModel(TfIdfModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self, model_params):
        super().create_new(model_params)
        self.classifier = Pipeline([
            ('vectorizer_tfidf', self.vectorizer),
            ('RandomForestClassifier',  RandomForestClassifier())
        ])
        self.classifier.set_params(**model_params)


