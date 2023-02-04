
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, DocumentSimilarity, SimilarityType, ParagraphSimilarity, Standard
from django.db.models.functions import Substr, Cast
from django.db.models import Max, Min, F, IntegerField, Q
import pandas as pd
from pathlib import Path
import glob
import os
import docx2txt
import time

from scripts.Persian.Preprocessing import standardIndexName


def standardFileName(name):
    name = name.replace(".", "")
    name = arabicCharConvert(name)
    name = persianNumConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  ", " ")

    return name


def persianNumConvert(text):
    persian_num_dict = {"۱": "1", "۲": "2", "۳": "3", "۴": "4",
                        "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9", "۰": "0"}
    for key, value in persian_num_dict.items():
        text = text.replace(key, value)
    return text


def arabicCharConvert(text):
    arabic_char_dict = {"ى": "ی", "ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا",
                        "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ", "\n\n": "\n", "\n ": "\n", }
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)

    return text


def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def numbers_preprocessing(text):
    persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
    for c in persianNumbers:
        text = text.replace(c, str(ord(c)-1776))
    for c in arabicNumbers:
        text = text.replace(c, str(ord(c)-1632))
    return text


def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)
    text = numbers_preprocessing(text)

    return text


def apply(folder, Country):
    # ParagraphSimilarity.objects.filter(
    #     para1__document_id__country_id=Country).delete()
    # print(ParagraphSimilarity.objects.all().count())

    DocumentSimilarity.objects.filter(
        doc1__country_id=Country).delete()
    print(DocumentSimilarity.objects.all().count())

    es_url = es_config.ES_URL
    client = Elasticsearch(es_url, timeout=40)

    model_name = Document.__name__
    if Country.language == "استاندارد":
        model_name = Standard.__name__
    if Country.language == "کتاب":
        model_name = Book.__name__

    index_name = standardIndexName(Country,model_name)

    indices_dict = {
        # "standard_documentparagraphs": "BM25"
        index_name + "_bm25_index":"BM25",
        index_name + "_dfr_index":"DFR",
        index_name + "_dfi_index":"DFI",
    }

    for index, measure in indices_dict.items():
        # calculate_para_sim(Country, client, index, measure)
        # calculate_sim(Country, client, index, measure)
        calculate_standard_sim2(Country, client, index, measure)


def calculate_sim(Country, client, index_name, sim_measure):
    books = Document.objects.filter(country_id=Country).values()

    res_query = {}
    for book in books:
        res_query = {
            "more_like_this": {
                "analyzer": "persian_custom_analyzer",
                "fields": ["attachment.content"],
                "like": [
                    {
                        "_index": index_name,
                        "_id": "{}".format(book['id']),

                    }

                ],
                "min_term_freq": 5,
                "max_query_terms": 100000,
                "min_doc_freq": 2,
                "max_doc_freq": 20,
                "min_word_length": 4,
                "stop_words": [
                    "کتاب",
                    "فهرست",
                    "شماره",
                    "اصلی",
                    "تهران",
                    "طبقه",
                    "از",
                    "در",
                    "به",
                    "با",
                    "که",
                    "و",
                    "های",
                    "هایی",
                    "ان",
                    "آن",
                    "می",
                    "مي",
                    "نمي",
                    "نمی",
                    "هاي"
                ]
            }
        }

        response = client.search(index=index_name,
                                 _source_includes=['subject'],
                                 # explain=True,
                                 request_timeout=40,
                                 query=res_query,
                                 highlight={
                                     "type": "fvh",
                                     "fields": {
                                         "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                     }},
                                 size=10
                                 )

        # max_score = 0
        # if response['hits']['max_score'] != None:
        #     max_score = float(response['hits']['max_score'])

        doc_res = response['hits']['hits']
        doc_res_dict = {}
        for doc in doc_res:
            doc_res_dict[doc['_id']] = doc
        similarity_type = SimilarityType.objects.get(name=sim_measure)
        for b in books:
            similarity = 0
            highlighted_text = None

            if b['id'] != book['id']:
                b_id = str(b['id'])
                if b_id in doc_res_dict.keys():
                    similarity = doc_res_dict[b_id]['_score']
                    # if max_score != 0:
                    #     similarity = (similarity/max_score)
                    highlighted_text = doc_res_dict[b_id]["highlight"]["attachment.content"][0]

                similarity = round(similarity, 2)
                DocumentSimilarity.objects.create(doc1_id=book['id'], doc2_id=b['id'],
                                                  similarity=similarity, similarity_type=similarity_type,
                                                  highlighted_text=highlighted_text)


def calculate_para_sim(Country, client, index_name, sim_measure):
    para_list = DocumentParagraphs.objects.filter(
        document_id__country_id=Country).values()
        
    para_count = len(para_list)

    Create_List = []
    batch_size = 10000

    res_query = {}
    i = 0
    for para in para_list:
        doc_id = para['document_id_id']
        res_query = {
            
            "bool" : {
                    "must" : {
                        "more_like_this": {
                            "analyzer": "persian_custom_analyzer",
                            "fields": ["attachment.content"],
                            "like": [
                                {
                                    "_index": index_name,
                                    "_id": "{}".format(para['id']),

                                }

                            ],
                            "min_term_freq": 2,
                            "max_query_terms": 1000,
                            "min_doc_freq": 2,
                            "max_doc_freq": 20000,
                            "min_word_length": 4,
                            "stop_words": [
                                "کتاب",
                                "فهرست",
                                "شماره",
                                "اصلی",
                                "تهران",
                                "طبقه",
                                "از",
                                "در",
                                "به",
                                "با",
                                "که",
                                "و",
                                "های",
                                "هایی",
                                "ان",
                                "آن",
                                "می",
                                "مي",
                                "نمي",
                                "نمی",
                                "هاي"
                            ]
                        }
                    },
 
                    "must_not" : {
                        "bool":{
                            "filter":{
                                "term":{
                                    "document_id":doc_id
                                }
                            }
                        }
                    },
  
                    }
                
        }
        
        
        response = client.search(index=index_name,
                                 _source_includes=['paragraph_id','document_id'],
                                 # explain=True,
                                 request_timeout=40,
                                 query=res_query,
                                 highlight={
                                     "type": "fvh",
                                     "fields": {
                                         "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                     }},
                                 )

        doc_res = response['hits']['hits']
        doc_res_dict = {}

        similarity_type = SimilarityType.objects.get(name=sim_measure)

        for doc2 in doc_res:

            similarity = doc2['_score']
            highlighted_text = doc2["highlight"]["attachment.content"][0]
            similarity = round(similarity, 2)

            ParaSim_obj = ParagraphSimilarity(para1_id=para['id'], para2_id=doc2['_id'],
                                                similarity=similarity, para_similarity_type=similarity_type,
                                                highlighted_text=highlighted_text)

            Create_List.append(ParaSim_obj)

        if Create_List.__len__() > batch_size:
            ParagraphSimilarity.objects.bulk_create(Create_List)
            print('====================\n')
            print(f'{len(Create_List)} created.')
            print('====================\n')

            Create_List = []
        
        i +=1
        print(f'{i}/{para_count}')

    ParagraphSimilarity.objects.bulk_create(Create_List)
    print('Completed.')


def calculate_standard_sim(Country, client, index_name, sim_measure):
    books = Document.objects.filter(country_id=Country).values()
    Create_List = []
    batch_size = 1000
    res_query = {}
    for book in books:
        res_query = {
            "more_like_this": {
                "analyzer": "persian_custom_analyzer",
                "fields": ["attachment.content"],
                "like": [
                    {
                        "_index": index_name,
                        "_id": "{}".format(book['id']),

                    }

                ],
                "min_term_freq": 5,
                "max_query_terms": 100000,
                "min_doc_freq": 2,
                "max_doc_freq": 20,
                "min_word_length": 4,
                "stop_words": [
                    "از",
                    "در",
                    "به",
                    "با",
                    "که",
                    "و",
                    "های",
                    "هایی",
                    "ان",
                    "آن",
                    "می",
                    "مي",
                    "نمي",
                    "نمی",
                    "هاي"
                ]
            }
        }

        response = client.search(index=index_name,
                                 _source_includes=['book_name'],
                                 # explain=True,
                                 request_timeout=40,
                                 query=res_query,
                                 highlight={
                                     "type": "fvh",
                                     "fields": {
                                         "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                     }},
                                 size=10
                                 )

        # max_score = 0
        # if response['hits']['max_score'] != None:
        #     max_score = float(response['hits']['max_score'])

        doc_res = response['hits']['hits']
        doc_res_dict = {}
        for doc in doc_res:
            doc_res_dict[doc['_id']] = doc
        similarity_type = SimilarityType.objects.get(name=sim_measure)
        for b in books:
            similarity = 0
            highlighted_text = None

            if b['id'] != book['id']:
                b_id = str(b['id'])
                if b_id in doc_res_dict.keys():
                    similarity = doc_res_dict[b_id]['_score']
                    # if max_score != 0:
                    #     similarity = (similarity/max_score)
                    highlighted_text = doc_res_dict[b_id]["highlight"]["attachment.content"][0]

                similarity = round(similarity, 2)
                DocumentSimilarity.objects.create(doc1_id=book['id'], doc2_id=b['id'],
                                                  similarity=similarity, similarity_type=similarity_type,
                                                  highlighted_text=highlighted_text)



def calculate_standard_sim2(Country, client, index_name, sim_measure):
    document_list = Document.objects.filter(country_id=Country).values()
    Create_List = []
    batch_size = 10000
    res_query = {}
    i = 0
    docs_count = len(document_list)
    for document in document_list:
        res_query = {
            "more_like_this": {
                "analyzer": "persian_custom_analyzer",
                "fields": ["attachment.content"],
                "like": [
                    {
                        "_index": index_name,
                        "_id": "{}".format(document['id']),

                    }

                ],
                "min_term_freq": 5,
                "max_query_terms": 100000,
                "min_doc_freq": 2,
                "max_doc_freq": 20,
                "min_word_length": 4,
                "stop_words": [
                    "از",
                    "در",
                    "به",
                    "با",
                    "که",
                    "و",
                    "های",
                    "هایی",
                    "ان",
                    "آن",
                    "می",
                    "مي",
                    "نمي",
                    "نمی",
                    "هاي"
                ]
            }
        }

        response = client.search(index=index_name,
                                 _source_includes=['name'],
                                 # explain=True,
                                 request_timeout=40,
                                 query=res_query,
                                 highlight={
                                     "type": "fvh",
                                     "fields": {
                                         "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                     }},
                                 size=10
                                 )

        # max_score = 0
        # if response['hits']['max_score'] != None:
        #     max_score = float(response['hits']['max_score'])

        doc_res = response['hits']['hits']
        similarity_type = SimilarityType.objects.get(name=sim_measure)

        for doc in doc_res:

            similarity = doc['_score']

            highlighted_text = doc["highlight"]["attachment.content"][0]

            similarity = round(similarity, 2)
            
            DocumentSimilarity_obj = DocumentSimilarity(doc1_id=document['id'], doc2_id=doc['_id'],
                                                similarity=similarity, similarity_type=similarity_type,
                                                highlighted_text=highlighted_text)
            Create_List.append(DocumentSimilarity_obj)

        if Create_List.__len__() > batch_size:
            DocumentSimilarity.objects.bulk_create(Create_List)
            print('====================\n')
            print(f'{len(Create_List)} created.')
            print('====================\n')

            Create_List = []
        
        i +=1
        print(f'{i}/{docs_count}')

    DocumentSimilarity.objects.bulk_create(Create_List)