
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, RevokedDocument
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

class RevokedIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)

    def generate_docs(self, files_dict, documents):

        for doc in documents:

            index_doc_id = doc['id']
            dest_doc_id = doc['dest_document_id'] if doc['dest_document_id'] is not None else 0
            dest_doc_name = doc['dest_document_found_name'] if doc['dest_document_found_name'] is not None else doc['dest_document_searched_name']
            dest_doc_file_name = doc['dest_file_name']
            src_doc_id = doc['src_document_id']
            src_doc_name = doc['src_document_name']
            approval_reference_name = doc['approval_reference_name']
            level_name = doc['level_name'] if doc['level_name'] != None else 'نامشخص'
            subject_name = doc['subject_name'] if doc['subject_name'] != None else 'نامشخص'
            type_name = doc['type_name'] if doc['type_name'] != None else 'نامشخص'
            approval_year = doc['approval_year'] if doc['approval_year'] != None else 0
            subject_area_name = doc['subject_area_name'] if doc['subject_area_name'] != None else 'نامشخص'
            subject_sub_area_name = doc['subject_sub_area_name'] if doc['subject_sub_area_name'] != None else 'نامشخص'

            dest_para_id = doc['dest_para_id'] if doc['dest_para_id'] != None else 0
            src_para_id = doc['src_para_id'] if doc['src_para_id'] != None else 0

            revoked_type_name = doc['revoked_type_name']
            revoked_sub_type = doc['revoked_sub_type']
            revoked_size = doc['revoked_size']
            revoked_clauses = doc['revoked_clauses']

            src_approval_date = doc['src_approval_date'] if doc['src_approval_date'] != None else 'نامشخص'
            dest_approval_date = doc['dest_approval_date'] if doc['dest_approval_date'] != None else 'نامشخص'

            # if dest_doc_file_name in files_dict:
            #     base64_file = files_dict[dest_doc_file_name]

            # added not found file text
            not_found_file_addr = str(Path(config.PERSIAN_PATH, 'not_found.txt'))
            not_found_text = open(not_found_file_addr, "rb").read()
            not_found_text = base64.b64encode(not_found_text)
            not_found_text = (str(not_found_text)[2:-1])



            new_doc = {
                'approval_reference_name':approval_reference_name,
                'level_name':level_name,
                'subject_name':subject_name,
                'type_name':type_name,
                'approval_year':approval_year,
                'subject_area_name':subject_area_name,
                'subject_sub_area_name':subject_sub_area_name,
                "src_document_id":src_doc_id,
                "src_document_name":src_doc_name,
                "dest_document_id":dest_doc_id,
                "dest_document_name":dest_doc_name,

                "dest_file_name": dest_doc_file_name if dest_doc_file_name in files_dict else "not_found",
                
                "revoked_type_name":revoked_type_name,
                "revoked_sub_type":revoked_sub_type,
                "revoked_size":revoked_size,
                "src_para_id":src_para_id,
                "dest_para_id":dest_para_id,
                "src_approval_date":src_approval_date,
                "dest_approval_date":dest_approval_date,
                "revoked_clauses":revoked_clauses,
                "data": files_dict[dest_doc_file_name] if dest_doc_file_name in files_dict else not_found_text
            }


            new_document = {
                "_index": self.name,
                "_id": index_doc_id,
                "pipeline":"attachment",
                "_source":new_doc,
            }
            yield new_document


def apply(folder, Country):
    model_name = RevokedDocument.__name__
    index_name = standardIndexName(Country,model_name)

    settings = es_config.FA_Settings
    mappings = es_config.Revoked_Mappings

    RevokedDocuments = RevokedDocument.objects.filter(country_id__id=Country.id).annotate(
        src_document_name = F('src_document__name'),
        approval_reference_name = F('dest_document__approval_reference_name'),
        level_name = F('dest_document__level_name'),
        subject_name = F('dest_document__subject_name'),
        type_name = F('dest_document__type_name'),
        subject_area_name = F('dest_document__subject_area_name'),
        subject_sub_area_name = F('dest_document__subject_sub_area_name'),
        approval_year = Cast(Substr('dest_document__approval_date', 1, 4), IntegerField()),
        dest_document_found_name = F('dest_document__name'),
        dest_document_searched_name = F('dest_document_name'),
        dest_file_name = F('dest_document__file_name'),
        revoked_type_name = F('revoked_type__name'),
        src_approval_date = F('src_document__approval_date'),
        dest_approval_date = F('dest_document__approval_date')
    ).values()

    new_index = RevokedIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder,RevokedDocuments,do_parallel=True)

