#!/usr/bin/env python
# coding: utf-8

# In[28]:


import re
import fitz
import spacy
#import requests
#import IPython
import pathlib
import nltk
import pandas as pd
import numpy as np
#nltk.download('wordnet')
#nltk.download('stopwords')
from nltk.corpus import stopwords
#from nltk.stem.porter import PorterStemmer
from nltk.tokenize.treebank import TreebankWordDetokenizer
spacy.load('en_core_web_sm')
from nltk.tokenize import RegexpTokenizer, word_tokenize
from keyphrase_vectorizers import KeyphraseCountVectorizer
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
#nltk.download('wordnet') 
#from nltk.stem.wordnet import WordNetLemmatizer


# In[18]:


def build_corpus(files_path):
    text_dict = {'title': [],
                 'text': []}

    #Iteration über PDF's und in text speichern. Alle PDF's liegen in text_list Es werden nur die ersten beiden Seiten eingelesen
    for file in files_path:
        has_abstract = False
        cur_reader = fitz.open(file)
        text = ''
        text_tmp = ''
        cur_title = cur_reader.metadata['title']

        for i in range(len(cur_reader)):  
            page = cur_reader.load_page(i)

            abstract = page.search_for("abstract")
            if abstract:
                text +=  cur_reader.get_page_text(i)
                has_abstract = True
                break;
            else:
                text_tmp +=  cur_reader.get_page_text(i)

        if not has_abstract:
            text = text_tmp

        text_dict['title'].append(cur_title)
        text_dict['text'].append(text)
        

        cur_reader.close()
        
    return text_dict


# In[19]:


def build_conference(files_path):
    con_dict = {'title': [],
                 'text': []}
    
    for file in files_path:
        cur_reader = fitz.open(file)
        text = ''
        cur_title = cur_reader.metadata['title']
        
        for i in range(len(cur_reader)):  
            page = cur_reader.load_page(i)
            text +=  cur_reader.get_page_text(i)
            
        con_dict['title'].append(cur_title)
        con_dict['text'].append(text)
        
    return con_dict


# In[20]:


def preprocess_corpus(corpus):
    for i in range(len(corpus['title'])):
        detokenize = []
        all_tokens = []
        
        text = corpus['text'][i] 
        tokens = word_tokenize(text) #tokens auf Wortebene

    for i in range(len(tokens)):
        tokens[i] = re.sub("(\\d)+","", tokens[i])   #entfernt Zahlen
        all_tokens.append(tokens[i])
        
    detokenize = TreebankWordDetokenizer().detokenize(all_tokens)
    corpus['text'].append(detokenize)
    
    return corpus


# In[21]:


def get_stopwords():
#Englische Stop Words
    stop_words = set(stopwords.words("english"))
#Hinzufügen eigener Stopwords
    new_words = ["the", "as", "was", "that", "open", "access", "thought", "sees", "agreement", "term", "initially", "people", "eu", "citiations", "de", "authors",
                "com", "citations", "table", "et", "al", "conference", "th", "ieee", "fig", "aaai", "www", "org", "yet", "http","open access" ]
    my_stop_words = stop_words.union(new_words)
    
    return my_stop_words


# In[26]:


def generate_keywords(corpus, conference_corpus):
    
    corpus = preprocess_corpus(corpus)
    
    paper_keys = {'keywords': [], 
                'relevance':[],
                'paper': [] }
    
    conference_keys = {'keywords': [], 
                        'relevance':[],
                        'conference': [] }
    
    sentence_model = SentenceTransformer("all-mpnet-base-v2")
    kw_model = KeyBERT(model=sentence_model)
    vectorizer = KeyphraseCountVectorizer(stop_words=get_stopwords())
    

    #iteration über alle PDF's

    for x in range(len(corpus['title'])): 
        doc_embedding, word_embedding = kw_model.extract_embeddings(corpus['text'][x], vectorizer=vectorizer)
        keywords_dist_paper = kw_model.extract_keywords(corpus['text'][x], vectorizer=vectorizer, use_mmr=True, diversity=0.6, 
                                                        top_n=20, doc_embeddings=doc_embedding, 
                                                        word_embeddings=word_embedding)

        
        for i in range(len(keywords_dist_paper)):
            keyword =  keywords_dist_paper[i][0]
            paper_keys['keywords'].append(keyword)
            relevance = keywords_dist_paper[i][1]
            paper_keys['relevance'].append(relevance)
            paper_keys['paper'].append(corpus["title"][x])
            
    for x in range(len(conference_corpus['title'])): 
        doc_embedding, word_embedding = kw_model.extract_embeddings(conference_corpus['text'][x], vectorizer=vectorizer)
        keywords_dist_conference = kw_model.extract_keywords(corpus['text'][x], vectorizer=vectorizer, use_mmr=True, diversity=0.5, 
                                                        top_n=20, doc_embeddings=doc_embedding, 
                                                        word_embeddings=word_embedding)
        
        for i in range(len(keywords_dist_conference)):
            keyword =  keywords_dist_conference[i][0]
            conference_keys['keywords'].append(keyword)
            relevance = keywords_dist_conference[i][1]
            conference_keys['relevance'].append(relevance)
            conference_keys['conference'].append(conference_corpus["title"][x])
            
        #Umwandlung in Dataframe

    df_paper = pd.DataFrame(paper_keys)
    filepath_paper = 'keywords/paper_Keywords.csv'
    df_paper = df_paper.sort_values('relevance',ascending=False)
    df_paper.to_csv(filepath_paper)

    df_conference = pd.DataFrame(conference_keys)
    filepath_conference = 'keywords/conference_Keywords.csv'
    df_conference = df_conference.sort_values('relevance',ascending=False)
    df_conference.to_csv(filepath_conference)

    return paper_keys, conference_keys


# In[11]:


new_words = ["the", "as", "was", "that", "open", "access", 
               "thought", "sees", "agreement", "term", "initially",
               "people", "eu", "citiations", "de", "authors",
               "com", "citations", "table", "et", "al", "conference", 
               "th", "ieee", "fig", "aaai", "www", "org", "yet", "http", 'open access' ]
print(stopwords.words('english'))


# In[16]:


vectorizer = KeyphraseCountVectorizer(stop_words=get_stopwords())
print(vectorizer.get_params())
