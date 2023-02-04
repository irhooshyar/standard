
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentGeneralDefinition, DocumentParagraphs, Standard
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

class TerminologyIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):

        for doc in documents: #  documents --> general definitions

            def_id = int(doc['id'])
            document_id = int(doc['document_id_id']) if doc['document_id_id'] else 0
            document_name = doc['document_name'] if doc['document_name'] else 'نامشخص'
            keyword = doc['keyword'] if doc['keyword'] else 'نامشخص'
            is_abbreviation = 1 if doc['is_abbreviation'] else 0
            text = doc['text'] if doc['text'] else 'نامشخص'
            document_approval_date = doc['document_approval_date'] if doc['document_approval_date'] else 'نامشخص'
            document_approval_reference_name = doc['document_approval_reference_name'] if doc['document_approval_reference_name'] else 'نامشخص'
            document_level_name = doc['document_level_name'] if doc['document_level_name'] else 'نامشخص'
            document_subject_name = doc['document_subject_name'] if doc['document_subject_name'] else 'نامشخص'

            new_doc = {
                'def_id': def_id,
                'keyword': keyword,
                'text': text,
                'is_abbreviation': is_abbreviation ,
                'document_id': document_id,
                'document_name': document_name,
                'document_approval_date' : document_approval_date ,
                'document_approval_reference_name' : document_approval_reference_name,
                'document_level_name' : document_level_name,
                'document_subject_name' : document_subject_name
            }

            new_document = {
                "_index": self.name,
                "_id": def_id,
                # "pipeline":"attachment",
                "_source":new_doc,
            }
            yield new_document


def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = DocumentGeneralDefinition.__name__
    index_name = standardIndexName(Country,model_name)

    country_lang = Country.language

    if country_lang == "انگلیسی":
        # settings = es_config.EN_Settings
        # mappings = es_config.EN_Mappings
        # Document_Model = en_model.DocumentGeneralDefinition
        return
    
    else:
        settings = es_config.FA_Settings
        mappings = es_config.Terminology_Mappings
        Document_Model = DocumentGeneralDefinition


    documents = Document_Model.objects.filter(document_id__country_id__id=Country.id).annotate(
        document_name=F('document_id__name'),
        document_approval_date=F('document_id__approval_date'),
        document_approval_reference_name=F('document_id__approval_reference_name'),
        document_level_name=F('document_id__level_name'),
        document_subject_name=F('document_id__subject_name'),
    ).values()


    new_index = TerminologyIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder,documents,do_parallel=True)

