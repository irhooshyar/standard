from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, Standard, DocumentActor
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

class DocumentActorIndex(ES_Index):
    def __init__(self, name, settings, mappings):
        super().__init__(name, settings, mappings)

    def generate_docs(self, files_dict, data):
        for datum in data:
            text_bytes = bytes(datum['_data'], encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_data = {
                'paragraph_id': datum['_paragraph_id'] if datum['_paragraph_id'] is not None else 0,
                'document_id': datum['_document_id'] if datum['_document_id'] is not None else 0,
                'document_name': datum['_document_name'] if datum['_document_name'] is not None else 'نامشخص',
                'document_subject_name': datum['_document_subject_name']
                if datum['_document_subject_name'] is not None else 'نامشخص',
                'document_approval_reference_name': datum['_document_approval_reference_name']
                if datum['_document_approval_reference_name'] is not None else 'نامشخص',
                'document_type_name': datum['_document_type_name']
                if datum['_document_type_name'] is not None else 'نامشخص',
                'document_level_name': datum['_document_level_name']
                if datum['_document_level_name'] is not None else 'نامشخص',
                'document_revoked_type_name': datum['_document_revoked_type_name']
                if datum['_document_revoked_type_name'] is not None else 'نامشخص',
                'document_organization_type_name': datum['_document_organization_type_name']
                if datum['_document_organization_type_name'] is not None else 'نامشخص',
                'document_approval_year': datum['_document_approval_year']
                if datum['_document_approval_year'] is not None else 0,
                'document_advisory_opinion_count': datum['_document_advisory_opinion_count']
                if datum['_document_advisory_opinion_count'] is not None else 0,
                'document_interpretation_rules_count': datum['_document_interpretation_rules_count']
                if datum['_document_interpretation_rules_count'] is not None else 0,

                'duty_type': datum['_duty_type'] if datum['_duty_type'] is not None else 'نامشخص',
                'actor_id': datum['_actor_id'] if datum['_actor_id'] is not None else 0,
                'actor_name': datum['_actor_name'] if datum['_actor_name'] is not None else 'نامشخص',
                'actor_category_id': datum['_actor_category_id'] if datum['_actor_category_id'] is not None else 0,
                'actor_category_name': datum['_actor_category_name']
                if datum['_actor_category_name'] is not None else 'نامشخص',
                'actor_area_id': datum['_actor_area_id'] if datum['_actor_area_id'] is not None else 0,
                'actor_area_name': datum['_actor_area_name'] if datum['_actor_area_name'] is not None else 'نامشخص',
                'actor_type_id': datum['_actor_type_id'] if datum['_actor_type_id'] is not None else 0,
                'actor_type_name': datum['_actor_type_name'] if datum['_actor_type_name'] is not None else 'نامشخص',
                'current_actor_form': datum['_current_actor_form']
                if datum['_current_actor_form'] is not None else 'نامشخص',
                'general_definition_keyword': datum['_general_definition_keyword']
                if datum['_general_definition_keyword'] is not None else 'نامشخص',
                'general_definition_text': datum['_general_definition_text']
                if datum['_ref_paragraph_text'] is not None else 'نامشخص',
                'ref_paragraph_text': datum['_ref_paragraph_text']
                if datum['_general_definition_text'] is not None else 'نامشخص',
                "data": base64_file
            }

            new_data_index = {
                "_index": self.name,
                "_id": datum['_id'],
                "pipeline": "attachment",
                "_source": new_data,
            }
            yield new_data_index


def apply(folder, country):
    model_name = DocumentActor.__name__

    index_name = standardIndexName(country, model_name)

    country_lang = country.language

    settings = es_config.Paragraphs_Settings_2
    mappings = es_config.Document_Actor_Mappings
    model = DocumentActor

    data = model.objects.filter(document_id__country_id__id=country.id). \
        annotate(_id=F('id')). \
        annotate(_paragraph_id=F('paragraph_id__id')). \
        annotate(_document_id=F('document_id__id')). \
        annotate(_document_name=F('document_id__name')). \
        annotate(_document_subject_name=F('document_id__subject_name')). \
        annotate(_document_approval_reference_name=F('document_id__approval_reference_name')). \
        annotate(_document_type_name=F('document_id__type_name')). \
        annotate(_document_level_name=F('document_id__level_name')). \
        annotate(_document_revoked_type_name=F('document_id__revoked_type_name')). \
        annotate(_document_organization_type_name=F('document_id__organization_name')). \
        annotate(_document_approval_year=Cast(Substr('document_id__approval_date', 1, 4), IntegerField())). \
        annotate(_document_advisory_opinion_count=F('document_id__advisory_opinion_count')). \
        annotate(_document_interpretation_rules_count=F('document_id__interpretation_rules_count')). \
        annotate(_data=F('paragraph_id__text')). \
        annotate(_duty_type=F('duty_type')). \
        annotate(_actor_id=F('actor_id__id')). \
        annotate(_actor_name=F('actor_id__name')). \
        annotate(_actor_category_id=F('actor_id__actor_category_id__id')). \
        annotate(_actor_category_name=F('actor_id__actor_category_id__name')). \
        annotate(_actor_area_id=F('actor_id__area__id')). \
        annotate(_actor_area_name=F('actor_id__area__name')). \
        annotate(_actor_type_id=F('actor_type_id__id')). \
        annotate(_actor_type_name=F('actor_type_id__name')). \
        annotate(_current_actor_form=F('current_actor_form')). \
        annotate(_general_definition_keyword=F('general_definition_id__keyword')). \
        annotate(_general_definition_text=F('general_definition_id__text')). \
        annotate(_ref_paragraph_text=F('ref_paragraph_id__text')). \
        values(
        '_id',
        '_paragraph_id',
        '_document_id',
        '_document_name',
        '_document_subject_name',
        '_document_approval_reference_name',
        '_document_type_name',
        '_document_level_name',
        '_document_revoked_type_name',
        '_document_organization_type_name',
        '_document_approval_year',
        '_document_advisory_opinion_count',
        '_document_interpretation_rules_count',
        '_data',
        '_duty_type',
        '_actor_id',
        '_actor_name',
        '_actor_category_id',
        '_actor_category_name',
        '_actor_area_id',
        '_actor_area_name',
        '_actor_type_id',
        '_actor_type_name',
        '_current_actor_form',
        '_general_definition_keyword',
        '_general_definition_text',
        '_ref_paragraph_text',
    )

    new_index = DocumentActorIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder, data, do_parallel=True)
