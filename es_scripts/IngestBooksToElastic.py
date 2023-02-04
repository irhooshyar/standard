
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

class BookIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):

        for doc in documents:

            doc_id = int(doc['document_id_id'])
            book_name = doc['name']
            publisher_name = doc['publisher_name']
            subject = doc['subject']
            year = int(doc['year'])
            pagecount = int(doc['pagecount'])
            status = doc['status']

            doc_file_name = ""

            if 'file_name' in doc and doc['file_name'] != None:
                doc_file_name = doc['file_name']
            else:
                doc_file_name = book_name

            if doc_file_name in files_dict:
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "document_id": doc_id,
                    "raw_file_name":doc_file_name,
                    "book_name": book_name,
                    "publisher_name" : publisher_name,
                    "subject_name" : subject,
                    "published_year" :year,
                    "pages_count" : pagecount,
                    "status" : status,
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

    index_name = "book_search_index"
    new_index = None

    country_lang = Country.language
    
    settings = es_config.FA_Settings
    mappings = es_config.Book_Mappings

    new_index = BookIndex(index_name, settings, mappings)


    documents = Book.objects.filter(document_id__country_id__id = Country.id).annotate(
        file_name = F('document_id__file_name')
    ).values()
    new_index.create()
    new_index.bulk_insert_documents(folder,documents,do_parallel=True)

