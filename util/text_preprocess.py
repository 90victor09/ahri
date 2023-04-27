
import re


def replace_chars(q):
    return q.replace('%', ' percent') \
            .replace('$', ' dollar ') \
            .replace('₹', ' rupee ') \
            .replace('€', ' euro ') \
            .replace('@', ' at ')


def remove_shortforms(q):
    contractions = {
        "ain't": "am not",
        "can't": "can not",
        "can't've": "can not have",
        "'cause": "because",
        "he'd": "he would",
        "he'd've": "he would have",
        "he's": "he is",
        "how'd": "how did",
        "how'd'y": "how do you",
        "how's": "how is",
        "i'd": "i would",
        "i'd've": "i would have",
        "i'm": "i am",
        "it'd": "it would",
        "it'd've": "it would have",
        "it's": "it is",
        "let's": "let us",
        "ma'am": "madam",
        "o'clock": "of the clock",
        "shan't": "shall not",
        "sha'n't": "shall not",
        "shan't've": "shall not have",
        "she'd": "she would",
        "she'd've": "she would have",
        "she's": "she is",
        "so's": "so as",
        "that'd": "that would",
        "that'd've": "that would have",
        "that's": "that is",
        "there'd": "there would",
        "there'd've": "there would have",
        "there's": "there is",
        "they'd": "they would",
        "they'd've": "they would have",
        "we'd": "we would",
        "we'd've": "we would have",
        "what's": "what is",
        "when's": "when is",
        "where'd": "where did",
        "where's": "where is",
        "who's": "who is",
        "why's": "why is",
        "won't": "will not",
        "won't've": "will not have",
        "y'all": "you all",
        "y'all'd": "you all would",
        "y'all'd've": "you all would have",
        "y'all're": "you all are",
        "y'all've": "you all have",
        "you'd": "you would",
        "you'd've": "you would have",
    }

    q_decontracted = []
    for word in q.split():
        if word in contractions:
            word = contractions[word]
        q_decontracted.append(word)

    return ' '.join(q_decontracted) \
        .replace("'ve", " have") \
        .replace("n't", " not") \
        .replace("'re", " are") \
        .replace("'ll", " will")


def trim_punctuation(q):
    return re.sub(re.compile('\W'), ' ', q).strip()


stopwords_exclude = None
def remove_stopwords(text):
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    global stopwords_exclude
    if not stopwords_exclude:
        try:
            stopwords_exclude = stopwords.words('english')
            word_tokenize("a")
        except LookupError:
            import nltk
            nltk.download('punkt')
            nltk.download('stopwords')
            stopwords_exclude = stopwords.words('english')

    s = ""
    for w in word_tokenize(text):
        if w not in stopwords_exclude:
            s += str(w) + " "
    
    return s
