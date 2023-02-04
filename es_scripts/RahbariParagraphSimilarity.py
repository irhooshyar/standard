
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Document, DocumentParagraphs, DocumentSimilarity, Rahbari, RahbariSimilarity, SimilarityType, RahbariParagraphSimilarity
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

    print(RahbariParagraphSimilarity.objects.all().count())

    RahbariParagraphSimilarity.objects.filter(
        para1__document_id__country_id=Country).delete()

    es_url = es_config.ES_URL
    client = Elasticsearch(es_url, timeout=40)

    # model_name = DocumentParagraphs.__name__
    # index_name = standardIndexName(Country, model_name)  # rahbari para index

    rahbari_para_index = "rahbarifull_documentparagraphs"

    indices_dict = {
        rahbari_para_index: "BM25"
    }

    for index, measure in indices_dict.items():
        calculate_para_sim(Country, client, index, measure)




def get_stopword_list(stopword_file_name):
    stop_words = []
    stop_words_file = str(Path(config.PERSIAN_PATH, stopword_file_name))
    with open(stop_words_file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            stop_words.append(line)
    f.close()
    return stop_words

def calculate_para_sim(Country, client, rahbari_para_index, sim_measure):

    rahbari_sim_docs = RahbariSimilarity.objects.all().values('doc1_id', 'doc2_id')

    i = 0
    row_count = rahbari_sim_docs.count()
    Create_List = []
    batch_size = 10000

    para_stopword_list = get_stopword_list('rahbari_stopwords.txt')
    doc_stopword_list = get_stopword_list('rahbari_doc_name_stopwords.txt')
    res_stopword_list = list(set(para_stopword_list + doc_stopword_list))

    for row in rahbari_sim_docs:
        rahbari_doc_id = row['doc1_id']
        dotic_doc_id = row['doc2_id']

        rahbari_paragraph_id_list = DocumentParagraphs.objects.filter(
            document_id__id=rahbari_doc_id
        ).values_list('id',flat=True).distinct()

        res_query = {}

        for rahbari_para_id in rahbari_paragraph_id_list:

            res_query = {

                "bool": {

                    "must": [

                        {
                            "more_like_this": {
                                "analyzer": "persian_custom_analyzer",
                                "fields": ["attachment.content"],
                                "like": [
                                    {
                                        "_index": rahbari_para_index,
                                        "_id": rahbari_para_id,

                                    }

                                ],
                                "min_term_freq": 1,
                                "max_query_terms": 1000,
                                "min_doc_freq": 2,
                                "min_word_length": 4,
                                "stopword_list":res_stopword_list

                            }
                        }

                    ],

                    "filter": [
                        {"term": {
                            "document_id": dotic_doc_id
                        }
                        }
                    ]

                }

            }

            response = client.search(index=es_config.DOTIC_PARA_INDEX,
                                     _source_includes=[
                                         'paragraph_id', 'document_id'],
                                     request_timeout=40,
                                     query=res_query,
                                     size=1,
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

            similarity_type = SimilarityType.objects.get(name=sim_measure)

            for doc2 in doc_res:

                similarity = doc2['_score']
                highlighted_text = doc2["highlight"]["attachment.content"][0]
                similarity = round(similarity, 2)

                ParaSim_obj = RahbariParagraphSimilarity(para1_id=rahbari_para_id, para2_id=doc2['_id'],
                                                         similarity=similarity, para_similarity_type=similarity_type,
                                                         highlighted_text=highlighted_text)

                Create_List.append(ParaSim_obj)

        if Create_List.__len__() > batch_size:
            RahbariParagraphSimilarity.objects.bulk_create(Create_List)
            print('====================\n')
            print(f'{len(Create_List)} created.')
            print('====================\n')

            Create_List = []

        i += 1
        print(f'{i}/{row_count}')

    RahbariParagraphSimilarity.objects.bulk_create(Create_List)
    print('Completed.')
