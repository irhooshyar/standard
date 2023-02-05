
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Standard
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


# ---------------------------------------------------------------------------------

class DocumentIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):

        for doc in documents:

            doc_id = int(doc['id'])
            doc_name = doc['name']

            doc_file_name = ""

            if 'file_name' in doc and doc['file_name'] != None:
                doc_file_name = doc['file_name']
            else:
                doc_file_name = doc_name

            doc_subject = doc['subject_name'] if doc['subject_name'] != None else 'نامشخص'
            doc_subject_weight = doc['subject_weight'] if doc['subject_weight'] != None else 'نامشخص'
            doc_level = doc['level_name'] if doc['level_name'] != None else 'نامشخص'
            doc_type = doc['type_name'] if doc['type_name'] != None else 'نامشخص'
            doc_advisory_opinion_count = doc['advisory_opinion_count'] if doc['advisory_opinion_count'] != None else 0
            doc_interpretation_rules_count = doc['interpretation_rules_count'] if doc['interpretation_rules_count'] != None else 0
            doc_approval_reference = doc['approval_reference_name'] if doc['approval_reference_name'] != None else 'نامشخص'

            doc_approval_year = doc['approval_year'] if doc['approval_year'] != None else 0
            doc_approval_date = doc['approval_date'] if doc['approval_date'] != None else 'نامشخص'
            doc_communicated_date = doc['communicated_date'] if doc['communicated_date'] != None else 'نامشخص'
            doc_communicated_year = doc['communicated_year'] if doc['communicated_year'] != None else 0
            doc_revoked_type_name = doc['revoked_type_name']

            doc_revoked_sub_type = doc['revoked_sub_type'] if doc['revoked_sub_type'] != None else 'نامشخص'
            doc_revoked_size = doc['revoked_size'] if doc['revoked_size'] != None else 'نامشخص'
            doc_revoked_clauses = doc['revoked_clauses'] if doc['revoked_clauses'] != None else 'نامشخص' 

            subject_area_name = doc['subject_area_name'] if doc['subject_area_name'] != None else 'نامشخص'
            subject_sub_area_name = doc['subject_sub_area_name'] if doc['subject_sub_area_name'] != None else 'نامشخص'
            subject_sub_area_weight = doc['subject_sub_area_weight'] if doc['subject_sub_area_weight'] != None else 0
            subject_sub_area_entropy = doc['subject_sub_area_entropy']
      

            doc_organization_type_name = doc['organization_name'].split('-') if doc['organization_name'] != None else 'نامشخص'

            if doc_file_name in files_dict:
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "document_id": doc_id,
                    "name": doc_name,
                    "approval_reference_name": doc_approval_reference,
                    "approval_date": doc_approval_date,
                    "approval_year": doc_approval_year,
                    "communicated_date": doc_communicated_date,
                    "communicated_year": doc_communicated_year,
                    "raw_file_name": doc_file_name,
                    "level_name": doc_level,
                    "subject_name": doc_subject,
                    "subject_weight": doc_subject_weight,
                    "type_name": doc_type,
                    "revoked_type_name":doc_revoked_type_name,
                    "revoked_sub_type":doc_revoked_sub_type,
                    "revoked_size":doc_revoked_size,
                    "revoked_clauses":doc_revoked_clauses,
                    "organization_type_name":doc_organization_type_name,
                    "advisory_opinion_count": doc_advisory_opinion_count,
                    "interpretation_rules_count": doc_interpretation_rules_count,
                    "subject_area_name": subject_area_name,
                    "subject_sub_area_name": subject_sub_area_name,
                    "subject_sub_area_weight": subject_sub_area_weight,
                    "subject_sub_area_entropy": subject_sub_area_entropy,
                    "data": base64_file
                }


                new_document = {
                    "_index": self.name,
                    "_id": doc_id,
                    "pipeline":"attachment",
                    "_source":new_doc,
                }
                yield new_document







def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = Document.__name__
    index_name = standardIndexName(Country,model_name)
    new_index = None

    country_lang = Country.language
    
    settings = es_config.FA_Settings
    mappings = es_config.FA_Mappings
    Document_Model = Document
    new_index = DocumentIndex(index_name, settings, mappings)

    documents = Document_Model.objects.filter(country_id__id=Country.id).annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField())).annotate(communicated_year=Cast(Substr('communicated_date', 1, 4), IntegerField())).values()


    new_index.create()
    new_index.bulk_insert_documents(folder,documents,do_parallel=True)
    