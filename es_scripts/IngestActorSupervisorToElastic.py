from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, Standard, DocumentActor,ActorSupervisor
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

class ActorSupervisorIndex(ES_Index):
    def __init__(self, name, settings, mappings):
        super().__init__(name, settings, mappings)

    def generate_docs(self, files_dict, data):
        for datum in data:
            text_bytes = bytes(datum['paragraph_text'], encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_data = {
                'id': datum['id'],
                'paragraph_id': datum['_paragraph_id'] if datum['_paragraph_id'] is not None else 0,
                'document_id': datum['_document_id'] if datum['_document_id'] is not None else 0,
                'document_name': datum['_document_name'] if datum['_document_name'] is not None else 'نامشخص',
                'source_actor_id': int(datum['source_actor_id_id']) if datum['source_actor_id_id'] else 0,
                'source_actor_name': datum['source_actor_name'] if datum['source_actor_name'] else 'نامشخص',
                'supervisor_actor_id': int(datum['supervisor_actor_id_id']) if datum['supervisor_actor_id_id'] else 0,
                'supervisor_actor_name': datum['supervisor_actor_name'] if datum['supervisor_actor_name'] else 'نامشخص',
                'source_actor_form': datum['source_actor_form'] if datum['source_actor_form'] else 'نامشخص',
                'supervisor_actor_form': datum['supervisor_actor_form'] if datum['supervisor_actor_form'] else 'نامشخص',
                "data": base64_file
            }

            new_data_index = {
                "_index": self.name,
                "_id": datum['id'],
                "pipeline": "attachment",
                "_source": new_data,
            }
            yield new_data_index


def apply(folder, country):
    model_name = ActorSupervisor.__name__

    index_name = standardIndexName(country, model_name)

    settings = es_config.Paragraphs_Settings_2
    mappings = es_config.ActorSupervisor_Mappings
    model = ActorSupervisor

    data = model.objects.filter(document_id__country_id__id=country.id).annotate(
            source_actor_name=F('source_actor_id__name'),
            supervisor_actor_name=F('supervisor_actor_id__name'),
            _paragraph_id=F('paragraph_id__id'),
            _document_id=F('document_id__id'),
            _document_name=F('document_id__name'),
            paragraph_text=F('paragraph_id__text')).values()

    new_index = ActorSupervisorIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder, data, do_parallel=True)
