
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Rahbari, Standard, Type
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
            doc_id = doc['document_id_id']
            doc_name = doc['document_name']
            subject_name = doc['subject_name']
            approval_reference_name = doc['approval_reference_name']
            approval_date = doc['approval_date']

            doc_file_name = doc['document_file_name']
            rahbari_date = doc['rahbari_date'] if doc['rahbari_date'] != None else 'نامشخص'
            rahbari_year = doc['rahbari_year'] if doc['rahbari_year'] != None else 0
            labels = doc['labels'] if doc['labels'] != None else 'نامشخص'

            labels = labels.split("؛")



            labels = list(map(lambda label_item:label_item.strip(),labels))
            if '' in labels:
                labels.remove('')
                
            # print(labels.__len__())
            rahbari_type = doc['rahbari_type_name'] if doc['rahbari_type_name'] != None else 'نامشخص'
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
                    "rahbari_type":rahbari_type,
                    "subject_name":subject_name,
                    "approval_reference_name":approval_reference_name,
                    "approval_date":approval_date,
                    "data": base64_file
                }

                new_document = {
                    "_index": self.name,
                    "_id": doc_id,
                    "pipeline": "attachment",
                    "_source": new_doc,
                }

                yield new_document


def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = Document.__name__
    index_name = standardIndexName(Country, model_name)

    settings = es_config.FA_Settings
    mappings = es_config.Rahbari_Mappings

    Rahbaries = Rahbari.objects.filter(document_id__country_id__id=Country.id).annotate(
        rahbari_type_name = F('rahbari_type__name'),
        subject_name = F('document_id__subject_name'),
        approval_reference_name = F('document_id__approval_reference_name'),
        approval_date = F('document_id__approval_date'),
    ).values()

    new_index = RahbariIndex(index_name, settings, mappings)
    new_index.create()

    new_index.bulk_insert_documents(folder, Rahbaries, do_parallel=True)

