
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
from doc.models import Standard_Branch,Standard,Standard_Status


# ---------------------------------------------------------------------------------

class StandardIndex(ES_Index):
    branch_list = Standard_Branch.objects.all()
    status_list = Standard_Status.objects.all()
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self,files_dict,documents):
        for doc in documents:
            branch_name = self.branch_list.get(id=doc['branch_id']).name if doc['branch_id'] not in [None,'nan'] else 'نامشخص'
            
            subject_category = branch_name.replace('کمیته ملی','').strip()

            status_name = self.status_list.get(id=doc['status_id']).name if doc['status_id'] not in [None,'nan'] else 'نامشخص'

            doc_id = int(doc['document_id_id'])
            doc_subject = doc['subject'] if doc['subject'] else 'نامشخص'
            doc_file_name = doc['standard_number'] if doc['standard_number'] else 'نامشخص'

            file_name_with_extention = doc['file_name_with_extention'] if doc['file_name_with_extention'] else 'نامشخص'
            
            # branch = doc['branch_id']
            ICS = doc['ICS'] if doc['ICS'] not in [None,'nan'] else 'نامشخص'
            # status = doc['status_id']
            appeal_number = doc['appeal_number'] if doc['appeal_number'] else 'نامشخص'
            Description = doc['Description'] if doc['Description'] else 'نامشخص'

            doc_approval_year = doc['approval_year'] if doc['approval_year'] != None else 0

            if doc_file_name in files_dict:
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "document_id": doc_id,
                    "name": doc_subject,
                    "approval_year": doc_approval_year,
                    "standard_number": doc_file_name,
                    "branch": branch_name,
                    "subject_category":subject_category,
                    "ICS": ICS,
                    "status": status_name,
                    "appeal_number": appeal_number,
                    "Description": Description,
                    "file_name_with_extention":file_name_with_extention,
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
    model_name = Standard.__name__
    index_name = standardIndexName(Country,model_name)

    settings = es_config.FA_Settings
    mappings = es_config.Standard_Mappings

    standard_documents = Standard.objects.filter(document_id__country_id__id=Country.id).values()


    new_index = StandardIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder, standard_documents,do_parallel=True)

