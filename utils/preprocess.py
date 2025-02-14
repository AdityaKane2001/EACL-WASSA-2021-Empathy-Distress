# File of the class PreprocessText, containing various functions for text preprocessing
# File: preprocess.py
# Author: Atharva Kulkarni


import pandas as pd
import numpy as np
import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.corpus import words, wordnet, brown
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import unicodedata
from pycontractions import Contractions
from autocorrect import Speller
from utils import Utils

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('words')
nltk.download('brown')






class Preprocess():
    """" Class containing various helper functions """   
    
    
    # -------------------------------------------- Class Constructor --------------------------------------------
    
    def __init__(self, mode="normalize", contractions_model_path="/content/GoogleNews-vectors-negative300.bin"):
        """ Class Constructor
        @param contractions_model_path (str): model to be loaded for contractions expansion.
        """
        self.utils = Utils()
        self.stop_words = stopwords.words('english')
        self.wordnet_lemmatizer = WordNetLemmatizer()
        self.speller = Speller(lang='en')
        self.wordlist = set(words.words()).union(set(wordnet.words()), set(brown.words()))
        self.nouns = ['NNP', 'NNPS']
        self.nlp = spacy.load('en_core_web_sm')
        if mode == "normalize":
            self.cont = Contractions(contractions_model_path)
            self.cont.load_models()
            
        
        
       
     
    # -------------------------------------------- Function to expand contractions --------------------------------------------
    
    def expand_contractions(self, text):
        """ Function to expand contractions
        @param text (str): input text to euxpand contractions.
        return text (str): Contraction expanded text.
        """
        text = list(self.cont.expand_texts([text], precise=True))[0]
        return text
    
      
    
    
    # -------------------------------------------- Function to Correct Spellings --------------------------------------------
       
    def correct_spelling(self, word, pos):
        """ Function to autocorrect words
        @param word (str): misspelled words
        @param proper_noun (list): list of proper nouns to ignore
        return corrected word

        """
        if word.lower() in self.wordlist or pos in self.nouns:
            return word
        else:
            return self.speller(word.lower())
        
        
        
    
    # --------------------------------------- Remove Wordplay ---------------------------------------
    
    def remove_wordplay(self, word, pos):
        pattern = re.compile(r"(\w*)(\w)\2(\w*)")
        substitution_pattern = r"\1\2\3"
        while True:
            if word.lower() in self.wordlist or pos in self.nouns:
                return word
            new_word = pattern.sub(substitution_pattern, word)
            if new_word != word:
                word = new_word
                continue
            else:
                return new_word
                
                
                
                    
    # -------------------------------------------- Function to normalize input text --------------------------------------------
    
    def normalize_text(self, text):
        """ Function to normalzie text inputs.
        @param text (str): Input text.
        """
        # Adding space for all puntuation marks
        text = re.sub(r"([\w/'+$\s-]+|[^\w/'+$\s-]+)\s*", r"\1 ", text)

        # Remove accented words
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

        # Remove long spaces
        text = re.sub(r'^\s*|\s\s*', ' ', text).strip()

        tokenized_text = text.split()
        
        abbr_dict = self.utils.get_dict("../resources/nrc-resources/social-media-abbreviations.csv", key_column="acronym", value_column="full_form")
        for i in range(len(tokenized_text)):
            x = re.sub(r'[^\w\s]', '', tokenized_text[i]).lower()
            
            # Expand acronyms
            if x in abbr_dict.keys():
                tokenized_text[i] = abbr_dict[x]

            # Expand contracitons
            tokenized_text[i] = self.expand_contractions(tokenized_text[i])    
        
        # Get Part of speech for each word
        tokens_pos = nltk.pos_tag(tokenized_text)

        # Remove wordplay
        tokenized_text = [self.remove_wordplay(word, pos) for word, pos in tokens_pos]
        
        # Combine words into sentence.    
        text = ""
        for word in tokenized_text:
            text = text + " " + word
        
        text = self.speller(text)
        return text
        

        
      
    # -------------------------------------------- Function to Normalize corpus --------------------------------------------
        
    def normalize_corpus(self, df, column_name):
        """ Function to normalize corpus.
        @param corpus (list): corpus list.
        @param column_name (str): name of column to normalize.
        """
        df[column_name] = df[column_name].apply(lambda text: self.normalize_text(text))
        return df
    
    
    
    
    # -------------------------------------------- Function to clean text --------------------------------------------
        
    def clean_text(self, text, remove_stopwords=True, lemmatize=True):
        """ Function to clean text
        @param text (str): text to be cleaned
        @param remove_stopwords (bool): To remove stopwords or not.
        @param lemmatize (bool): to lemmatize or not.
        """
        # Remove emails 
        text = re.sub('\S*@\S*\s?', '', text)
        
        # Remove new line characters 
        text = re.sub('\s+', ' ', text) 
        
        # Remove distracting single quotes 
        text = re.sub("\'", '', text)

        # Remove puntuations and numbers
        text = re.sub('[^a-zA-Z]', ' ', text)

        # Remove single characters
        text = re.sub('\s+[a-zA-Z]\s+^I', ' ', text)
        
        # remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.lower()

        if not remove_stopwords and not lemmatize:
            return text

        # Remove unncecessay stopwords
        if remove_stopwords:
            text = word_tokenize(text)
            text = " ".join([word for word in text if word not in self.stop_words])
        
        # Word lemmatization
        if lemmatize:
            text = self.nlp(text)
            lemmatized_text = []
            for word in text:
                if word.lemma_.isalpha():
                    if word.lemma_ != '-PRON-':
                        lemmatized_text.append(word.lemma_.lower())
                    # else:
                        # lemmatized_text.append(word.lower())
            text = " ".join([word.lower() for word in lemmatized_text])
                
        return text
        
        
        
        
