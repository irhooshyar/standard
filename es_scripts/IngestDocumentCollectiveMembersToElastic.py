
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Document, DocumentCollectiveMembers
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

class DocumentCollectiveMembersIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):

        for doc in documents: #  documents --> document collective members
            id = int(doc['id'])
            document_id = int(doc['document_id_id']) if doc['document_id_id'] else 0
            document_name = doc['document_name'] if doc['document_name'] else 'نامشخص'
            document_approval_date = doc['document_approval_date'] if doc['document_approval_date'] else 'نامشخص'
            document_approval_reference_name = doc['document_approval_reference_name'] if doc['document_approval_reference_name'] else 'نامشخص'
            document_level_name = doc['document_level_name'] if doc['document_level_name'] else 'نامشخص'
            document_subject_name = doc['document_subject_name'] if doc['document_subject_name'] else 'نامشخص'
            paragraph_id = int(doc['paragraph_id_id']) if doc['paragraph_id_id'] else 0
            paragraph_text = doc['paragraph_text'] if doc['paragraph_text'] else 'نامشخص'
            paragraph_number = int(doc['paragraph_number']) if doc['paragraph_number'] else 0
            collective_actor_id = int(doc['collective_actor_id_id']) if doc['collective_actor_id_id'] else 0
            collective_actor_name = doc['collective_actor_name'] if doc['collective_actor_name'] else 'نامشخص'
            name = doc['name'] if doc['name'] else 'نامشخص'
            members_list = []
            for member_id,member_info in doc['members'].items():
                member_name = member_info['name'] if member_info['name'] else 'نامشخص'
                member_form = member_info['form'] if member_info['form'] else 'نامشخص'
                member_obj = {"id":member_id, "name":member_name, "form":member_form}
                members_list.append(member_obj)
            members = members_list
            
            members_count = int(doc['members_count']) if doc['members_count'] else 0
            has_next_paragraph_members = True if doc['has_next_paragraph_members'] else False
            next_paragraphs = doc['next_paragraphs'] if doc['next_paragraphs'] else 'نامشخص'
            obligation = doc['obligation'] if doc['obligation'] else 'نامشخص'

            text_bytes = bytes(doc['paragraph_text'], encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_doc = {
                'id': id,
                'document_id': document_id,
                'document_name': document_name,
                'document_approval_date' : document_approval_date ,
                'document_approval_reference_name' : document_approval_reference_name,
                'document_level_name' : document_level_name,
                'document_subject_name' : document_subject_name,
                'paragraph_id': paragraph_id,
                'paragraph_text': paragraph_text,
                'paragraph_number': paragraph_number,
                'collective_actor_id': collective_actor_id,
                'collective_actor_name': collective_actor_name,
                'name': name,
                'members': members,
                'members_count': members_count,
                'has_next_paragraph_members': has_next_paragraph_members,
                'next_paragraphs': next_paragraphs,
                'obligation': obligation,
                "data": base64_file
            }

            new_document = {
                "_index": self.name,
                "_id": id,
                "pipeline":"attachment",
                "_source":new_doc,
            }
            yield new_document


def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = DocumentCollectiveMembers.__name__
    index_name = standardIndexName(Country,model_name)

    settings = es_config.FA_Settings
    mappings = es_config.DocumentCollectiveMembers_Mappings
    Document_Model = DocumentCollectiveMembers


    documents = Document_Model.objects.filter(document_id__country_id__id=Country.id).annotate(
        document_name=F('document_id__name'),
        document_approval_date=F('document_id__approval_date'),
        document_approval_reference_name=F('document_id__approval_reference_name'),
        document_level_name=F('document_id__level_name'),
        document_subject_name=F('document_id__subject_name'),
        paragraph_text=F('paragraph_id__text'),
        paragraph_number=F('paragraph_id__number'),
        collective_actor_name=F('collective_actor_id__name'),
    ).values()



    new_index = DocumentCollectiveMembersIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder,documents,do_parallel=True)

