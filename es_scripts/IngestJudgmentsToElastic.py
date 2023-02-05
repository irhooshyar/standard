
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Judgment, Standard
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

class JudgementIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):
        
        for doc in documents:

            judgement_id = int(doc['id'])
            doc_id = doc['document_id_id']
            doc_name = doc['doc_name']
            doc_file_name = doc['doc_file_name']
            judgment_number = doc['judgment_number'] if doc['judgment_number'] != None else 'نامشخص'
            judgment_date = doc['judgment_date'] if doc['judgment_date'] != None else 'نامشخص'
            judgment_year = doc['judgment_year'] if doc['judgment_year'] != None else 0
            complaint_serial = doc['complaint_serial'] if doc['complaint_serial'] != None else 'نامشخص'
            conclusion_display_name = doc['conclusion_name'] if doc['conclusion_name'] != None else 'نامشخص'
            subject_type_display_name = doc['subject_type_name'] if doc['subject_type_name'] != None else 'نامشخص'
            judgment_type = doc['judgment_type_name'] if doc['judgment_type_name'] != None else 'نامشخص'
            complainant = doc['complainant'] if doc['complainant'] != None else 'نامشخص'
            complaint_from = doc['complaint_from'] if doc['complaint_from'] not in ['nan', None] else 'نامشخص'
            categories = doc['categories_name'] if doc['categories_name'] != None else 'نامشخص'
            affected_document_name = doc['affected_document_name'] if doc['affected_document_name'] != None else 'نامشخص'
            subject_complaint =  doc['subject_complaint'] if doc['subject_complaint'] != None else 'نامشخص'
            judge_name = doc['judge'] if doc['judge_name_id'] != None else 'نامشخص'

            if doc_file_name in files_dict:
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "document_id": doc_id,
                    "name": doc_name,
                    "document_file_name": doc_file_name,
                    "judgment_id": judgement_id,
                    "judgment_number": judgment_number,
                    "judgment_date": judgment_date,
                    "judgment_year": judgment_year,
                    "complaint_serial": complaint_serial,
                    "conclusion_display_name": conclusion_display_name,
                    "subject_type_display_name": subject_type_display_name,
                    "judgment_type": judgment_type,
                    "complainant": complainant,
                    "complaint_from": complaint_from,
                    "categories": categories,
                    "affected_document_name": affected_document_name,
                    "subject_complaint":subject_complaint,
                    "judge_name": judge_name,
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
    model_name = Judgment.__name__
    index_name = standardIndexName(Country,model_name)

    settings = es_config.FA_Settings
    mappings = es_config.Judement_Mappings

    judgments = Judgment.objects.filter(document_id__country_id__id=Country.id).annotate(
        doc_name = F('document_id__name'),
        doc_file_name = F('document_id__file_name'),
        conclusion_name = F('conclusion_display_name__name'),
        subject_type_name = F('subject_type_display_name__name'),
        judgment_type_name = F('judgment_type__name'),
        categories_name = F('categories__name'),
        judge = F('judge_name__name'),
    ).values()

    new_index = JudgementIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder,judgments,do_parallel=True)

