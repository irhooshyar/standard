
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Rahbari, Type
from django.db.models.functions import Substr, Cast
from django.db.models import Max, Min, F, IntegerField, Q
import pandas as pd
from pathlib import Path
import glob
import os
import docx2txt
import time
from es_scripts.ES_Index import ES_Index
from es_scripts.ES_Index import readFiles
import time
from elasticsearch import helpers
from collections import deque
from scripts.Persian.Preprocessing import standardIndexName
from en_doc import models as en_model


# ---------------------------------------------------------------------------------

class RahbariIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):
        
        for doc in documents:

            print("**", doc)

            doc_id = doc['document_id_id']
            doc_name = doc['document_name']
            doc_file_name = doc['document_file_name']
            rahbari_date = doc['rahbari_date'] if doc['rahbari_date'] != None else 'نامشخص'
            rahbari_year = doc['rahbari_year'] if doc['rahbari_year'] != None else 0
            labels = doc['labels'] if doc['labels'] != None else 'نامشخص'

            try:
                type_obj = Type.objects.get(id=doc['type_id'])
                type = type_obj.name
            except:
                type = 'نامشخص'

            if doc_file_name in files_dict:
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "document_id": doc_id,
                    "name": doc_name,
                    "raw_file_name": doc_file_name,
                    "rahbari_date": rahbari_date,
                    "rahbari_year": rahbari_year,
                    "labels": labels,
                    "type": type,
                    "data": base64_file
                }


                new_document = {
                    "_index": self.name,
                    "_id": doc_id,
                    "pipeline": "attachment",
                    "_source": new_doc,
                }

                yield new_document


def apply(folder, Country,similarity_type):
    settings = {}
    mappings = {}
    model_name = Rahbari.__name__
    index_name = standardIndexName(Country, model_name)

    if similarity_type == "BM25":
        settings = es_config.Standard_BM25_Settings
        mappings = es_config.BM25_Rahbari_Mappings
        index_name =  index_name + "_bm25_index"

    elif similarity_type == "DFR":
        settings = es_config.Standard_DFR_Settings
        mappings = es_config.DFR_Rahbari_Mappings
        index_name = index_name + "_dfr_index"

    elif similarity_type == "DFI":
        settings = es_config.Standard_DFI_Settings
        mappings = es_config.DFI_Rahbari_Mappings
        index_name = index_name + "_dfi_index"


    Rahbaries = Rahbari.objects.filter(document_id__country_id__id=Country.id).values()

    new_index = RahbariIndex(index_name, settings, mappings)
    new_index.create()

    new_index.bulk_insert_documents(folder, Rahbaries, do_parallel=True)

