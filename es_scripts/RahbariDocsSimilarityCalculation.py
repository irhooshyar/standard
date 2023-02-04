
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, DocumentSimilarity, Rahbari, RahbariSimilarity, SimilarityType, ParagraphSimilarity, Standard
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

    RahbariSimilarity.objects.filter(
        doc1__country_id=Country).delete()


    es_url = es_config.ES_URL
    client = Elasticsearch(es_url, timeout=40)



    index_name = es_config.DOTIC_DOC_INDEX

    indices_dict = {
        index_name + "_bm25_index":"BM25"
    }

    for index, measure in indices_dict.items():
        calculate_rahbari_sim(Country, client, index, measure)



def calculate_rahbari_sim(Country, client, index_name, sim_measure):
    rahbari_index = "rahbarifull_document"


    document_list = Rahbari.objects.all().values()

    Create_List = []
    batch_size = 10000
    res_query = {}
    i = 0
    docs_count = len(document_list)

    for document in document_list:
        res_query = {
            'bool':{
                'must':[],
                'filter':[
                    {
                        'terms':{
                            'level_name.keyword':['اسناد بالادستی','قانون']
                        }
                    }
                ]
            }
        }
        like_query = {
            "more_like_this": {
                "analyzer": "persian_custom_analyzer",
                "fields": ["attachment.content"],
                "like": [
                    {
                        "_index":rahbari_index ,
                        "_id": "{}".format(document['document_id_id']),
                    }

                ],
                "min_term_freq": 5,
                "max_query_terms": 100000,
                "min_doc_freq": 2,
                "max_doc_freq": 150000,
                "min_word_length": 4,
                "minimum_should_match":"60%"
            }
        }
        res_query['bool']['must'].append(like_query)
        response = client.search(index=index_name,
                                 _source_includes=['name'],
                                 request_timeout=40,
                                 query=res_query,
                                #  highlight={
                                #      "type": "fvh",
                                #      "fields": {
                                #          "attachment.content":
                                #          {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                #           "number_of_fragments": 0
                                #           }
                                #      }},
                                 size=10
                                 )


        doc_res = response['hits']['hits']
        similarity_type = SimilarityType.objects.get(name=sim_measure)

        for doc in doc_res:

            similarity = doc['_score']

            # highlighted_text = doc["highlight"]["attachment.content"][0]

            similarity = round(similarity, 2)
            
            RahbariSimilarity_obj = RahbariSimilarity(doc1_id=document['document_id_id'], doc2_id=doc['_id'],
                                                similarity=similarity, similarity_type=similarity_type
                                                # highlighted_text=highlighted_text
                                                )
            Create_List.append(RahbariSimilarity_obj)

        if Create_List.__len__() > batch_size:
            RahbariSimilarity.objects.bulk_create(Create_List)
            print('====================\n')
            print(f'{len(Create_List)} created.')
            print('====================\n')

            Create_List = []
        
        i +=1
        print(f'{i}/{docs_count}')

    RahbariSimilarity.objects.bulk_create(Create_List)