import math
import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q, F

from abdal import config
from pathlib import Path
import string
from doc.models import Country, Judgment, JudgmentJudge
from doc.models import Document
from doc.models import DocumentParagraphs, RevokedDocument, RevokedType
from datetime import datetime
from abdal import es_config
import time
from elasticsearch import Elasticsearch
from scripts.Persian.Preprocessing import standardIndexName
from es_scripts import IngestRevokedDocument, IngestDocumentsToElastic
import re

es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)


def search_affected_name_ES(Country, affected_doc_name, current_doc_id):
    current_doc_id = str(current_doc_id)
    index_name = es_config.DOTIC_DOC_INDEX

    # ############### 1. Term Query ###############################
    name_term_query = {
        "term": {
            "name.keyword": affected_doc_name
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name'],
                             request_timeout=40,
                             query=name_term_query,
                             size=2
                             )

    if len(response['hits']['hits']) > 0 and response['hits']['hits'][0]['_id'] != current_doc_id:

        result_doc_id = response['hits']['hits'][0]['_id']


    elif len(response['hits']['hits']) > 1 and response['hits']['hits'][0]['_id'] == current_doc_id:
        result_doc_id = response['hits']['hits'][1]['_id']
    # ############### 2. Match Query ###############################
    else:

        res_query = {
            "match_phrase": {
                "name": affected_doc_name
            }
        }

        response = client.search(index=index_name,
             _source_includes=['document_id', 'name'],
             request_timeout=40,
             query=res_query,
             size=2
         )

        if len(response['hits']['hits']) > 0 and response['hits']['hits'][0]['_id'] != current_doc_id:
            result_doc_id = response['hits']['hits'][0]['_id']
            result_doc_name = response['hits']['hits'][0]['_source']['name']

            diff_term_count = abs(len(set(result_doc_name.split(' '))) - len(set(affected_doc_name.split(' '))))
            if diff_term_count > 2:
                result_doc_id = None
        elif len(response['hits']['hits']) > 1 and response['hits']['hits'][0]['_id'] == current_doc_id:
            result_doc_id = response['hits']['hits'][1]['_id']
            result_doc_name = response['hits']['hits'][1]['_source']['name']
            diff_term_count = abs(len(set(result_doc_name.split(' '))) - len(set(affected_doc_name.split(' '))))
            if diff_term_count > 2:
                result_doc_id = None
        # ############### 3. MLT Query ###############################
        else:

            like_query = {
                "more_like_this": {
                    "analyzer": "persian_custom_analyzer",
                    "fields": ["name"],
                    "like": affected_doc_name,
                    "min_term_freq": 1,
                    "max_query_terms": 200,
                    "min_doc_freq": 1,
                    "max_doc_freq": 150000,
                    "min_word_length": 2,
                    "minimum_should_match": "85%"
                }
            }

            response = client.search(index=index_name,
                                     _source_includes=['name'],
                                     request_timeout=40,
                                     query=like_query,
                                     size=2
                                     )

            if len(response['hits']['hits']) > 0 and response['hits']['hits'][0]['_id'] != current_doc_id:
                result_doc_id = response['hits']['hits'][0]['_id']
                result_doc_name = response['hits']['hits'][0]['_source']['name']

                diff_term_count = abs(len(set(result_doc_name.split(' '))) - len(set(affected_doc_name.split(' '))))
                if diff_term_count > 2:
                    result_doc_id = None
            elif len(response['hits']['hits']) > 1 and response['hits']['hits'][0]['_id'] == current_doc_id:
                result_doc_id = response['hits']['hits'][1]['_id']
                result_doc_name = response['hits']['hits'][1]['_source']['name']
                diff_term_count = abs(len(set(result_doc_name.split(' '))) - len(set(affected_doc_name.split(' '))))
                if diff_term_count > 2:
                    result_doc_id = None
            else:
                result_doc_id = None

    return result_doc_id


def apply(folder_name, Country):
    revoked_type = preprocess_laghv_molgha(Country)
    detect_laghv(Country, revoked_type)
    detect_molgha(Country, revoked_type)
    detect_moghoof(Country)

    update_document_revoked_type(Country)

    IngestRevokedDocument.apply(folder_name, Country)
    IngestDocumentsToElastic.apply(folder_name, Country)

    print("revoked documents added.")


def detect_moghoof(Country):
    batch_size = 1000
    result_list = []
    moghoof = 'موقوف الاجرا'

    # create moghoof type if not already existing
    revoked_type = RevokedType.objects.filter(name=moghoof)
    if not revoked_type.exists():
        revoked_type = RevokedType.objects.create(name=moghoof)
    else:
        revoked_type = revoked_type[0]

    # remove old moghoof docs
    RevokedDocument.objects.filter(country_id=Country, revoked_type__name=moghoof).delete()

    # get docs containing moghoof
    moghoof_doc = Document.objects.filter(country_id=Country, name__icontains=moghoof).exclude(name__icontains='لغو').exclude(name__icontains='ملغی')

    moghoof_verbs = [
        'ماندن',
        'گرديدن',
        'گردیدن',
        'شدن',
        'نمودن',
        'گذاردن',
        'بودن',
        'شناختن',
    ]

    remove_keyword = [
        'موقت',
        'مفاد',
        'قسمت',
        # '',
    ]

    jozii_keyword = [
        'فراز',
        'جزء',
        'تبصره',
        'بندهاي',
        'بند',
        'ماده',
        'مواد',
    ]

    for doc in moghoof_doc:
        doc_name = doc.name
        moghoof_index = doc_name.find(moghoof)

        # skip if moghoof word is not at beginning
        if moghoof_index > 20:
            continue

        # remove moghoof verb
        affected_doc_name = doc_name[moghoof_index + len(moghoof):].strip()
        # print(affected_doc_name)
        for verb in moghoof_verbs:
            # print(verb)
            verb_index = affected_doc_name.find(verb)
            if verb_index < 4 and verb_index != -1:
                affected_doc_name = affected_doc_name[verb_index + len(verb):].strip()
                break

        # remove extra words
        for word in remove_keyword:
            affected_doc_name, _ = remove_from_start(affected_doc_name, word)

        # detect jozii
        affected_doc_name_cp = affected_doc_name
        for word in jozii_keyword:
            affected_doc_name, _ = remove_from_start(affected_doc_name, word)
            if _:
                affected_doc_name = remove_first_word(affected_doc_name)
            while affected_doc_name.find(' ') != -1 and len(affected_doc_name.split(' ')[0]) < 3:
                affected_doc_name = remove_first_word(affected_doc_name)

        # get affected doc id
        result_doc_id = search_affected_name_ES(Country, affected_doc_name, doc.id)

        RevokedDocument_obj = RevokedDocument(
            country_id=Country,
            revoked_type=revoked_type,
            src_document=doc,
            dest_document_id=result_doc_id,
            dest_document_name=affected_doc_name,
            revoked_sub_type='صریح',
            revoked_size='کلی' if affected_doc_name_cp == affected_doc_name else 'جزئی',
            # revoked_size=affected_doc_name,
            revoked_clauses='کل مصوبه' if affected_doc_name_cp == affected_doc_name
            else affected_doc_name_cp.replace(affected_doc_name, ''),
        )

        result_list.append(RevokedDocument_obj)
        if result_list.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(result_list)
            result_list = []

    RevokedDocument.objects.bulk_create(result_list)



def preprocess_laghv_molgha(Country):
    laghv = 'لغو/ملغی'

    # create laghv type if not already existing
    revoked_type = RevokedType.objects.filter(name=laghv)
    if not revoked_type.exists():
        revoked_type = RevokedType.objects.create(name=laghv)
    else:
        revoked_type = revoked_type[0]

    # remove old moghoof docs
    RevokedDocument.objects.filter(country_id=Country, revoked_type__name=laghv).delete()

    return revoked_type


def detect_laghv(Country, revoked_type):
    batch_size = 1000
    result_list = []

    laghv = 'لغو'

    # get docs containing laghv
    moghoof_doc = Document.objects.filter(country_id=Country, name__icontains=laghv)

    moghoof_verbs = [
        'گرديدن',
        'گردیدن',
        'شدن',
        'نمودن',
        'بودن',
        'شناختن',
    ]

    remove_keyword = [
        'موقت',
        'مفاد',
        # '',
    ]

    jozii_keyword = [
        'فراز',
        'جزء',
        'تبصره',
        'بندهاي',
        'بند',
        'ماده',
    ]

    for doc in moghoof_doc:
        doc_name = doc.name
        moghoof_index = doc_name.find(laghv)

        # skip if moghoof word is not at beginning
        if moghoof_index > 20:
            continue

        # remove moghoof verb
        affected_doc_name = doc_name[moghoof_index + len(laghv):].strip()
        # print(affected_doc_name)
        for verb in moghoof_verbs:
            # print(verb)
            verb_index = affected_doc_name.find(verb)
            if verb_index < 4 and verb_index != -1:
                affected_doc_name = affected_doc_name[verb_index + len(verb):].strip()
                break

        # remove extra words
        for word in remove_keyword:
            affected_doc_name, _ = remove_from_start(affected_doc_name, word)

        # detect jozii
        affected_doc_name_cp = affected_doc_name
        for word in jozii_keyword:
            affected_doc_name, _ = remove_from_start(affected_doc_name, word)
            if _:
                affected_doc_name = remove_first_word(affected_doc_name)
            while affected_doc_name.find(' ') != -1 and len(affected_doc_name.split(' ')[0]) < 3:
                affected_doc_name = remove_first_word(affected_doc_name)

        # get affected doc id
        result_doc_id = search_affected_name_ES(Country, affected_doc_name, doc.id)
        # print(doc_name)
        # print(affected_doc_name)
        # if result_doc_id is not None:
        #     # print(result_doc_id)
        #     print(Document.objects.get(id=result_doc_id).name)
        # print("*" * 10)

        RevokedDocument_obj = RevokedDocument(
            country_id=Country,
            revoked_type=revoked_type,
            src_document=doc,
            dest_document_id=result_doc_id,
            dest_document_name=affected_doc_name,
            revoked_sub_type='صریح',
            revoked_size='کلی' if affected_doc_name_cp == affected_doc_name else 'جزئی',
            # revoked_size=affected_doc_name,
            revoked_clauses='کل مصوبه' if affected_doc_name_cp == affected_doc_name
            else affected_doc_name_cp.replace(affected_doc_name, ''),
        )

        result_list.append(RevokedDocument_obj)
        if result_list.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(result_list)
            result_list = []

    RevokedDocument.objects.bulk_create(result_list)


def detect_molgha(Country, revoked_type):
    batch_size = 1000
    result_list = []

    molgha = 'ملغی'

    # get docs containing laghv
    moghoof_doc = Document.objects.filter(country_id=Country, name__icontains=molgha)

    moghoof_verbs = [
        'الاثر شدن',
        'گرديدن',
        'گردیدن',
        'شدن',
        'نمودن',
        'بودن',
        'شناختن',
        'کردن',
    ]

    remove_keyword = [
        'موقت',
        'مفاد',
        # '',
    ]

    jozii_keyword = [
        'فراز',
        'جزء',
        'تبصره',
        'بندهاي',
        'بند',
        'ماده',
    ]

    for doc in moghoof_doc:
        doc_name = doc.name
        moghoof_index = doc_name.find(molgha)

        # skip if moghoof word is not at beginning
        if moghoof_index > 20:
            continue

        # remove moghoof verb
        affected_doc_name = doc_name[moghoof_index + len(molgha):].strip()
        # print(affected_doc_name)
        for verb in moghoof_verbs:
            # print(verb)
            verb_index = affected_doc_name.find(verb)
            if verb_index < 4 and verb_index != -1:
                affected_doc_name = affected_doc_name[verb_index + len(verb):].strip()
                break

        # remove extra words
        for word in remove_keyword:
            affected_doc_name, _ = remove_from_start(affected_doc_name, word)

        # detect jozii
        affected_doc_name_cp = affected_doc_name
        for word in jozii_keyword:
            affected_doc_name, _ = remove_from_start(affected_doc_name, word)
            if _:
                affected_doc_name = remove_first_word(affected_doc_name)
            while affected_doc_name.find(' ') != -1 and len(affected_doc_name.split(' ')[0]) < 3:
                affected_doc_name = remove_first_word(affected_doc_name)

        # get affected doc id
        result_doc_id = search_affected_name_ES(Country, affected_doc_name, doc.id)
        # print(doc_name)
        # print(affected_doc_name)
        # if result_doc_id is not None:
        #     # print(result_doc_id)
        #     print(Document.objects.get(id=result_doc_id).name)
        # print("*" * 10)

        RevokedDocument_obj = RevokedDocument(
            country_id=Country,
            revoked_type=revoked_type,
            src_document=doc,
            dest_document_id=result_doc_id,
            dest_document_name=affected_doc_name,
            revoked_sub_type='صریح',
            revoked_size='کلی' if affected_doc_name_cp == affected_doc_name else 'جزئی',
            # revoked_size=affected_doc_name,
            revoked_clauses='کل مصوبه' if affected_doc_name_cp == affected_doc_name
            else affected_doc_name_cp.replace(affected_doc_name, ''),
        )

        result_list.append(RevokedDocument_obj)
        if result_list.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(result_list)
            result_list = []

    RevokedDocument.objects.bulk_create(result_list)


def remove_first_word(text):
    text = text.strip()
    if text.find(' ') == -1:
        return text
    return ' '.join(text.split(' ')[1:]).strip()


def remove_from_start(text, sub_text, margin=0):
    text = text.strip()
    index = text.find(sub_text)
    if index <= margin and index != -1:
        return text[index + len(sub_text):].strip(), True
    return text, False


def update_document_revoked_type(Country):
    revoked_doc_ids = RevokedDocument.objects.filter(country_id__id=Country.id).values_list('dest_document_id',
                                                                                            flat=True)

    revoked_docs = RevokedDocument.objects.filter(country_id__id=Country.id).annotate(
        revoked_name=F('revoked_type__name')
    ).values()

    # Document.objects.filter(country_id__id=Country.id).update(revoked_type_name='معتبر')

    revoked_doc_dict = {}

    for doc in revoked_docs:
        revoked_doc_dict[doc['dest_document_id']] = {
            'revoked_name': doc['revoked_name'],
            'revoked_sub_type': doc['revoked_sub_type'],
            'revoked_size': doc['revoked_size'],
            'revoked_clauses': doc['revoked_clauses'],
        }

    batch_size = 1000

    selected_doc_list = Document.objects.filter(id__in=revoked_doc_ids)

    for doc in selected_doc_list:
        doc.revoked_type_name = revoked_doc_dict[doc.id]['revoked_name']
        doc.revoked_sub_type = revoked_doc_dict[doc.id]['revoked_sub_type']
        doc.revoked_size = revoked_doc_dict[doc.id]['revoked_size']
        doc.revoked_clauses = revoked_doc_dict[doc.id]['revoked_clauses']

    Document.objects.bulk_update(
        selected_doc_list, ['revoked_type_name', 'revoked_sub_type', 'revoked_size', 'revoked_clauses'], batch_size)

    print('Document Fields updated.')
