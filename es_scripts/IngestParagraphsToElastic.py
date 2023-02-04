
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
from en_doc import models as en_model


# ---------------------------------------------------------------------------------

class ParagraphIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self,files_dict,paragraphs):

        for para in paragraphs:
            paragraph_id = para['para_id']
            document_id = para['doc_id']
            document_name = para['doc_name']
            type_name = para['type_name']

            approval_reference_name = para['approval_reference_name'] if para['approval_reference_name'] != None else 'نامشخص'
            level_name =  para['level_name'] if para['level_name'] != None else 'نامشخص'
            approval_year = para['approval_year'] if para['approval_year'] != None else 0
            
            para_text = para['para_text']

            text_bytes = bytes(para_text,encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_para = {
                "paragraph_id": paragraph_id,
                "document_id": document_id,
                "document_name": document_name,
                "type_name":type_name,
                'approval_reference_name':approval_reference_name,
                'level_name':level_name,
                'approval_year':approval_year,
                "clause_type": "نامشخص",
                "clause_number": 0,
                "data": base64_file
            }


            new_paragraph = {
                "_index": self.name,
                "_id": paragraph_id,
                "pipeline":"attachment",
                "_source":new_para,
            }
            yield new_paragraph



def apply(folder, Country,is_for_ref):
    settings = {}
    mappings = {}
    model_name = DocumentParagraphs.__name__
    
    index_name = standardIndexName(Country,model_name)

    if is_for_ref == 1:
        index_name = index_name + "_graph"

        print(is_for_ref)
        
    country_lang = Country.language

    if country_lang in ["فارسی","استاندارد"]:
        settings = es_config.Paragraphs_Settings_2 if is_for_ref == 1 else es_config.Paragraphs_Settings_3
        mappings = es_config.Paragraphs_Mappings

    elif country_lang == "انگلیسی":
        settings = es_config.EN_Settings
        mappings = es_config.EN_Paragraphs_Mappings


    Paragraphs_Model = DocumentParagraphs if country_lang in ['فارسی','استاندارد'] else en_model.DocumentParagraphs

    paragraphs = Paragraphs_Model.objects.filter(
        document_id__country_id__id = Country.id).annotate(
            para_id = F('id')).annotate(
                doc_id = F('document_id__id')).annotate(
                doc_name = F('document_id__name'), 
                type_name = F('document_id__type_name'),
                approval_reference_name = F('document_id__approval_reference_name'),
                approval_year=Cast(Substr('document_id__approval_date', 1, 4), IntegerField()),
                level_name = F('document_id__level_name')).annotate(
                para_text = F('text')).values(

        'para_id','doc_id','doc_name',
        'para_text','type_name','approval_reference_name', 
        'approval_year', 'level_name'
    )
    print(len(paragraphs))
    new_index = ParagraphIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder, paragraphs,do_parallel=True)

