import nltk
import numpy as np
import pandas as pd
import hazm
import requests
import time
import torch
from sentence_transformers import models, SentenceTransformer, util

from elasticsearch import Elasticsearch
from abdal import es_config
from elasticsearch import helpers
from collections import deque
import base64

es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)

def load_st_model(model_name_or_path):
    word_embedding_model = models.Transformer(model_name_or_path)
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True,
        pooling_mode_cls_token=False,
        pooling_mode_max_tokens=False)
    
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
    return model

def apply(folder_name, Country):
    res_query= {
    "range": {
        "attachment.content_length":{
        "gte": 50
        }
    }
    }

    response = client.search(index="fava_documentparagraphs_graph",
        request_timeout=120,
        query=res_query,
        size=50
    )

    total_hits = response['hits']['total']['value']
    print(total_hits)

    result = response['hits']['hits']

    corpus = []
    paragraph_dict = {}
    i = 0
    for res in result:
        paragraph_text = res["_source"]["attachment.content"]
        paragraph_id = res["_source"]["paragraph_id"]

        corpus.append(paragraph_text)
        paragraph_dict[i] = {'id':paragraph_id, 'text':paragraph_text, 'BERT_WikiNLI':[], 
                            'BERT_WikiTriplet':[], 'BERT_FarsTail':[]}
        i+=1
    
    # Load the Sentence-Transformer
    embedder = load_st_model('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
    corpus_embeddings = embedder.encode(corpus, show_progress_bar=True)

    
    for i in range(corpus_embeddings):
        paragraph_dict[i]['BERT_WikiNLI'] = corpus_embeddings[i]

    print(i)
    print(paragraph_dict[i])
