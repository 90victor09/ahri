FROM python:3.10

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN echo 'import nltk; nltk.download("punkt"); nltk.download("stopwords")' | python3