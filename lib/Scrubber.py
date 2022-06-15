
import nltk
nltk.download('stopwords');nltk.download('brown');nltk.download('punkt');nltk.download('wordnet'); nltk.download('omw-1.4')
from nltk.corpus import stopwords
import numpy as np
from gensim.models import Word2Vec
from gensim.models.phrases import Phraser, Phrases

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from textblob import TextBlob
import re



class Scrubber ():

    def __init__(self):
        pass

    def CleanText (self, text, length=1024):
        # Change all the text to lower case
        text = text.lower()
        # Converts all '+' and '/' to the word 'and'
        text = re.sub(r'[+|/]', ' and ', text)
        # Removes all characters besides numbers, letters, and commas
        text = re.sub(r'[^\w\d,]', ' ', text)
        # Word Tokenization
        words = text.split()
        # Remove Non-alpha text
        words = [re.sub(r'[^a-z]', '', word) for word in words if word.isalnum()]
        if len (words) > length:
            words = words[0:length]
        # Joins tokenized string into one string
        text = ' '.join(words)
        return text    
        
    def PreprocessText (self, text, min_len=4):  
        
        # Word Tokenization
        words = nltk.word_tokenize(text)

        # Word Lemmatization
        words = [lemmatizer.lemmatize(word) for word in words]
        
        # Removes all stop words from text and words that are less than two characters in length
        words = [word for word in words if word not in stopwords.words('english') and len(word) > min_len]
        '''
            Lemmatization: removes inflectional endings only and
            to return the base or dictionary form of a word, which is known as the lemma
        '''

        return words
    
    def Subject(self, text, min_len=4):
        text_blob = TextBlob(text)
        noun_str  = ' '.join(list(text_blob.noun_phrases))
        words = self.PreprocessText(noun_str, min_len)
        return words

    def Cleaning(self, Text, min_len=3, max_len=16):
        Text = self.CleanText (Text)       
        words = nltk.word_tokenize(Text)
        words = [lemmatizer.lemmatize(word) for word in words]
        stopwords_list = stopwords.words('english') 
        words = [word for word in words if word not in stopwords_list and len(word) >= min_len and len(word) < max_len]
        #words = list (set (words))
        return " ".join(words)
         