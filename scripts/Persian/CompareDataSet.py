from scripts.Persian import Preprocessing
from doc.models import Document, Country, Compare_Dataset_CUBE, DocumentParagraphs
import math
from itertools import chain
import time
import threading
from abdal import config
from abdal import es_config
from elasticsearch import Elasticsearch

es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)

def standardIndexName(Country,model_name):

    file_name = Country.file_name

    index_name = file_name.split('.')[0] + '_' + model_name
    index_name = index_name.replace(' ','_')
    index_name = index_name.replace(',','_')
    index_name = index_name.lower()

    return index_name

def apply(folder_name):
    t = time.time()

    MarKazPaZhohesh = Country.objects.get(id=3)
    Dotic = Country.objects.get(id=1)

    CompareCountry(MarKazPaZhohesh, Dotic)
    CompareCountry(Dotic, MarKazPaZhohesh)

    print("time ", time.time() - t)


def CompareCountry(src_country, target_country):
    src_document_list = Document.objects.filter(country_id=src_country)
    Compare_Dataset_CUBE.objects.filter(src_country_id=src_country).delete()
    index_name = standardIndexName(target_country, Document.__name__)
    Create_List = []

    i = 0
    for document in src_document_list:
        print(i/src_document_list.__len__())
        i += 1

        name_term_query = {
            "term": {
                "name.keyword": document.name
            }
        }

        response = client.search(index=index_name,
                                 _source_includes=['name'],
                                 request_timeout=40,
                                 query=name_term_query,
                                 size=1
                                 )

        if len(response['hits']['hits']) > 0:
            result_doc_id = response['hits']['hits'][0]['_id']
            result_doc_name = response['hits']['hits'][0]['_source']['name']

            object = Compare_Dataset_CUBE(
                src_country_id=src_country,
                src_document_id=document,
                src_document_name=document.name,
                src_document_approval_date=document.approval_date,
                dest_country_id=target_country,
                dest_document_id_id=result_doc_id,
                dest_document_name=result_doc_name,
                dest_document_approval_date=Document.objects.get(id=result_doc_id).approval_date,
                type="سند دقیقا یکسان"
            )
            Create_List.append(object)

        else:
            like_query = {
                "more_like_this": {
                    "analyzer": "persian_custom_analyzer",
                    "fields": ["name"],
                    "like": document.name,
                    "min_term_freq": 1,
                    "max_query_terms": 500,
                    "min_doc_freq": 1,
                    "max_doc_freq": 150000,
                    "min_word_length": 1,
                    "minimum_should_match": "90%"
                }
            }

            response = client.search(index=index_name,
                                     _source_includes=['name'],
                                     request_timeout=40,
                                     query=like_query,
                                     size=1
                                     )

            if len(response['hits']['hits']) > 0:
                result_doc_id = response['hits']['hits'][0]['_id']
                result_doc_name = response['hits']['hits'][0]['_source']['name']

                object = Compare_Dataset_CUBE(
                    src_country_id=src_country,
                    src_document_id=document,
                    src_document_name=document.name,
                    src_document_approval_date=document.approval_date,
                    dest_country_id=target_country,
                    dest_document_id_id=result_doc_id,
                    dest_document_name=result_doc_name,
                    dest_document_approval_date=Document.objects.get(id=result_doc_id).approval_date,
                    type="سند با شباهت بالا"
                )
                Create_List.append(object)

            else:

                like_query = {
                    "more_like_this": {
                        "analyzer": "persian_custom_analyzer",
                        "fields": ["name"],
                        "like": document.name,
                        "min_term_freq": 1,
                        "max_query_terms": 500,
                        "min_doc_freq": 1,
                        "max_doc_freq": 150000,
                        "min_word_length": 1,
                        "minimum_should_match": "60%"
                    }
                }

                response = client.search(index=index_name,
                                         _source_includes=['name'],
                                         request_timeout=40,
                                         query=like_query,
                                         size=1
                                         )

                if len(response['hits']['hits']) == 0:

                    object = Compare_Dataset_CUBE(
                        src_country_id=src_country,
                        src_document_id=document,
                        src_document_name=document.name,
                        src_document_approval_date=document.approval_date,
                        type="بدون سند مشابه (اطمینان بالا)"
                    )
                    Create_List.append(object)

    Compare_Dataset_CUBE.objects.bulk_create(Create_List)





