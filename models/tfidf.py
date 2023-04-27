from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from base import BaseModel


class SVCModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self):
        self.classifier = Pipeline([
            ('vectorizer_tfidf', TfidfVectorizer()),
            ('SVC',  SVC())
        ])


class KNNModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self):
        self.classifier = Pipeline([
            ('vectorizer_tfidf', TfidfVectorizer()),
            ('KNN',  KNeighborsClassifier())
        ])


class MultinomialNBModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self):
        self.classifier = Pipeline([
            ('vectorizer_tfidf', TfidfVectorizer()),
            ('MultinomialNB',  MultinomialNB())
        ])


class RandomForestModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.classifier = None

    def create_new(self):
        self.classifier = Pipeline([
            ('vectorizer_tfidf', TfidfVectorizer()),
            ('RandomForestClassifier',  RandomForestClassifier())
        ])


