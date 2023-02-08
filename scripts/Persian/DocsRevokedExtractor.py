import math
import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re
import pandas as pd

from django.db.models import Q,F

from abdal import config
from pathlib import Path
import string
from doc.models import Country, Judgment, JudgmentJudge
from doc.models import  Document
from doc.models import DocumentParagraphs,RevokedDocument,RevokedType
from datetime import datetime
from abdal import es_config
import time
from elasticsearch import Elasticsearch
from scripts.Persian.Preprocessing import standardIndexName
from es_scripts import IngestDocumentsToElastic
import re
import numpy as np

es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)



def mlt_query_search(affected_doc_name,index_name):
    result_doc_id = None

    like_query = {
        "more_like_this": {
            "analyzer": "persian_custom_analyzer",
            "fields": ["name"],
            "like":affected_doc_name,
            "min_term_freq": 1,
            "max_query_terms": 200,
            "min_doc_freq": 1,
            "max_doc_freq": 150000,
            "min_word_length": 2,
            "minimum_should_match":"75%"
        }
    }

    response = client.search(index=index_name,
                            _source_includes = ['name'],
                            request_timeout=40,
                            query=like_query,
                            size=1
                            )

    if len(response['hits']['hits']) > 0:
        result_doc_id = response['hits']['hits'][0]['_id']
        result_doc_name = response['hits']['hits'][0]['_source']['name']
        
        res_doc_name_chars_count = len(result_doc_name.replace(' ',''))
        affected_doc_name_chars_count = len(affected_doc_name.replace(' ',''))

        
        diff_chars_count = abs(res_doc_name_chars_count - affected_doc_name_chars_count )
        if diff_chars_count > 2:
            result_doc_id = None

    return result_doc_id

def match_phrase_query(affected_doc_name,index_name):
    result_doc_id = None
    res_query = {
        "match_phrase":{
            "name":affected_doc_name
        }
    }

    response = client.search(index=index_name,
    _source_includes = ['document_id','name'],
    request_timeout=40,
    query=res_query,
    size=1
    )
    
    if len(response['hits']['hits']) > 0:
        result_doc_id = response['hits']['hits'][0]['_id']
        result_doc_name = response['hits']['hits'][0]['_source']['name']
        
        res_doc_name_chars_count = len(result_doc_name.replace(' ',''))
        affected_doc_name_chars_count = len(affected_doc_name.replace(' ',''))

        
        diff_chars_count = abs(res_doc_name_chars_count - affected_doc_name_chars_count )
        if diff_chars_count > 2:
            result_doc_id = None

    return result_doc_id

def term_query_search(affected_doc_name,index_name):
    result_doc_id = None

    name_term_query = {
        "term":{
            "name.keyword":affected_doc_name
        }
    }

    response = client.search(index=index_name,
    _source_includes = ['document_id','name'],
    request_timeout=40,
    query=name_term_query,
    size=1
    )

    if len(response['hits']['hits']) > 0:

        result_doc_id = response['hits']['hits'][0]['_id']
        result_doc_name = response['hits']['hits'][0]['_source']['name']
    
    return result_doc_id
    


def search_affected_name_ES(Country,affected_doc_name):

    result_doc_id = None

    index_name = es_config.DOTIC_DOC_INDEX

    # ############### 1. Term Query ###############################

    result_doc_id = term_query_search(affected_doc_name,index_name)
    
    # ############### 2. Match Query ###############################

    if result_doc_id == None:
        result_doc_id = match_phrase_query(affected_doc_name,index_name)

    # ############### 3. MLT Query ###############################

    if result_doc_id == None:
        result_doc_id = mlt_query_search(affected_doc_name,index_name)


    return result_doc_id

def apply(folder_name, Country):

    RevokedDocument.objects.filter(country_id__id = Country.id).delete()

    Revoked_Doc_List = []
    Not_Found_Docs_Count = 0

    static_reovked_doc_to_db(Country,Revoked_Doc_List,Not_Found_Docs_Count)
    
    rahahan_revoked_type_peyvast_4(Country,Revoked_Doc_List,Not_Found_Docs_Count) # منقضی
    
    rahahan_revoked_type_peyvast_3(Country,Revoked_Doc_List,Not_Found_Docs_Count)
    rahahan_revoked_type(Country,Revoked_Doc_List,Not_Found_Docs_Count)

    mokhber_doc1_revoke_precess(Country,Revoked_Doc_List,Not_Found_Docs_Count)

    takhalofat_edari_revoked_type(Country,Revoked_Doc_List,Not_Found_Docs_Count)


    update_document_revoked_type(Country)

    print(f"{len(Revoked_Doc_List)} revoked documents found.")
    print(f"{Not_Found_Docs_Count} revoked documents not found.")
    

    # IngestDocumentsToElastic.apply(folder_name,Country)



def static_reovked_doc_to_db(Country,Revoked_Doc_List,Not_Found_Docs_Count):
    excelFile = str(Path(config.PERSIAN_PATH, 'static_revoked_documrnts.xlsx'))

    df = pd.read_excel(excelFile)
    df = df.fillna('-')

    Create_List = []
    batch_size = 1000
    c = 0
    total_size_count = 0
    partial_size_count = 0
    not_found_size = 0

    revoked_type = RevokedType.objects.get(name = 'منسوخ')

    for index,row in df.iterrows():

        if row['dest_document_id'] != '-':

            result_doc_id = row['dest_document_id']


            if result_doc_id not in Revoked_Doc_List:

                Revoked_Doc_List.append(result_doc_id)

                RevokedDocument_obj = RevokedDocument(
                    country_id = Country,
                    revoked_type = revoked_type,
                    src_document_id = row['src_document_id'],
                    dest_document_id = result_doc_id,
                    dest_document_name = row['dest_document_name'],
                    revoked_sub_type = 'صریح',
                    revoked_size = row['revoked_size'],
                    revoked_clauses = row['revoked_clauses'],
                    src_para_id = row['src_para_id']
                )

                Create_List.append(RevokedDocument_obj)
                c += 1

        else:
            RevokedDocument_obj = RevokedDocument(
                country_id = Country,
                revoked_type = revoked_type,
                src_document_id = row['src_document_id'],
                dest_document_name = row['dest_document_name'],
                revoked_sub_type = 'صریح',
                revoked_size = row['revoked_size'],
                revoked_clauses = row['revoked_clauses'],
                src_para_id = row['src_para_id']
            )

            Create_List.append(RevokedDocument_obj)
            Not_Found_Docs_Count += 1      
            not_found_size += 1      


    RevokedDocument.objects.bulk_create(Create_List)

    res_para_size = len(df.index)

    print(f'all revoked docs count: {res_para_size}')
    
    print(f'{c}/{res_para_size} created.')
    print(f'{not_found_size}/{res_para_size} not found.')

    print(f'{total_size_count}/{c} total revoked.')
    print(f'{partial_size_count}/{c} partial revoked.')


# تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]
def rahahan_revoked_type(Country,Revoked_Doc_List,Not_Found_Docs_Count):
    #  پیوست 1 منسوخ صریح شامل (کلی و جزئی)

    start_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
        text = "پیوست 1) - منسوخ ضمنی و با اجرا منتفی").number

    
    end_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
        text = "پیوست 2)- مصوبات معتبر").number



    result_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
    ).filter(number__gt = start_number).filter(number__lt = end_number).filter(
        text__icontains = "نسخ می"
    ).values()


    revoked_type = RevokedType.objects.get(name = 'منسوخ')

    Create_List = []
    batch_size = 1000
    c = 0
    total_size_count = 0
    partial_size_count = 0
    not_found_size = 0

    for para in result_paragraphs:
        para_text =  para['text']

        cropped_text = para_text.split('-')[1]
        revoked_size_segment = para_text.split('-')[-1]
        
        revoked_clauses = revoked_size_segment.split('نسخ')[0].strip()

        try:
            end_index = re.search("[0-9][0-9]* *\/", cropped_text).span()[0]

            affected_doc_name = cropped_text[:end_index].strip()
        
            result_doc_id = search_affected_name_ES(Country,affected_doc_name)

            revoked_size = 'جزئی'

            if revoked_clauses == 'کل مصوبه':
                revoked_size = 'کلی'
                total_size_count += 1
            else:
                partial_size_count += 1

            if result_doc_id != None:

                if result_doc_id not in Revoked_Doc_List:

                    Revoked_Doc_List.append(result_doc_id)

                    RevokedDocument_obj = RevokedDocument(
                        country_id = Country,
                        revoked_type = revoked_type,
                        src_document_id = para['document_id_id'],
                        dest_document_id = result_doc_id,
                        dest_document_name = affected_doc_name,
                        revoked_sub_type = 'صریح',
                        revoked_size = revoked_size,
                        revoked_clauses = revoked_clauses,
                        src_para_id = para['id']
                    )

                    Create_List.append(RevokedDocument_obj)
                    c += 1

            else :
                RevokedDocument_obj = RevokedDocument(
                    country_id = Country,
                    revoked_type = revoked_type,
                    src_document_id = para['document_id_id'],
                    dest_document_name = affected_doc_name,
                    revoked_sub_type = 'صریح',
                    revoked_size = revoked_size,
                    revoked_clauses = revoked_clauses,
                    src_para_id = para['id']
                )

                Create_List.append(RevokedDocument_obj)
                Not_Found_Docs_Count += 1

        except:
            pass


        if Create_List.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(Create_List)
            Create_List = []

    RevokedDocument.objects.bulk_create(Create_List)

    res_para_size = len(result_paragraphs)
    print(f'all para count: {res_para_size}')
    
    print(f'{c}/{res_para_size} created.')
    print(f'{not_found_size}/{res_para_size} not found.')

    print(f'{total_size_count}/{c} total revoked.')
    print(f'{partial_size_count}/{c} partial revoked.')



# تصویب نامه تنقیحی هیات وزیران در موضوع تخلفات اداری [تصویب نامه در خصوص مصوبات معتبر و منسوخ در موضوع تخلفات اداری]
def takhalofat_edari_revoked_type(Country,Revoked_Doc_List,Not_Found_Docs_Count):
    #  پیوست 1 منسوخ صریح شامل (کلی و جزئی)

    start_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع تخلفات اداری [تصویب نامه در خصوص مصوبات معتبر و منسوخ در موضوع تخلفات اداری]",
        text = "پیوست (1)- مصوبات منسوخ ضمنی و با اجرا منتفی").number

    
    end_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع تخلفات اداری [تصویب نامه در خصوص مصوبات معتبر و منسوخ در موضوع تخلفات اداری]",
        text = "پیوست (2)- مصوبات معتبر").number



    result_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع تخلفات اداری [تصویب نامه در خصوص مصوبات معتبر و منسوخ در موضوع تخلفات اداری]",
    ).filter(number__gt = start_number).filter(number__lt = end_number).filter(
        text__icontains = "نسخ می"
    ).values()


    revoked_type = RevokedType.objects.get(name = 'منسوخ')

    Create_List = []
    batch_size = 1000
    c = 0
    total_size_count = 0
    partial_size_count = 0
    not_found_size = 0

    for para in result_paragraphs:
        para_text =  para['text']

        paragraph_num = para_text.split('-')[0]
        affected_doc_name = para_text.split('-')[1]


        revoked_size_segment = para_text.split('-')[-1]
        
        revoked_clauses = revoked_size_segment.split('نسخ')[0].strip()


        try:
        
            result_doc_id = search_affected_name_ES(Country,affected_doc_name)

            revoked_size = 'جزئی'

            if revoked_clauses == 'کل مصوبه':
                revoked_size = 'کلی'
                total_size_count += 1

            else:
                partial_size_count += 1
                if len(revoked_clauses) > 50:
                    revoked_clauses = '-'

            if result_doc_id != None:

                if result_doc_id not in Revoked_Doc_List:

                    Revoked_Doc_List.append(result_doc_id)

                    RevokedDocument_obj = RevokedDocument(
                        country_id = Country,
                        revoked_type = revoked_type,
                        src_document_id = para['document_id_id'],
                        dest_document_id = result_doc_id,
                        dest_document_name = affected_doc_name,
                        revoked_sub_type = 'صریح',
                        revoked_size = revoked_size,
                        revoked_clauses = revoked_clauses,
                        src_para_id = para['id']
                    )

                    Create_List.append(RevokedDocument_obj)
                    c += 1

            else :
                RevokedDocument_obj = RevokedDocument(
                    country_id = Country,
                    revoked_type = revoked_type,
                    src_document_id = para['document_id_id'],
                    dest_document_name = affected_doc_name,
                    revoked_sub_type = 'صریح',
                    revoked_size = revoked_size,
                    revoked_clauses = revoked_clauses,
                    src_para_id = para['id']
                )

                Create_List.append(RevokedDocument_obj)
                Not_Found_Docs_Count += 1

        except:
            not_found_size += 1
            pass


        if Create_List.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(Create_List)
            Create_List = []

    RevokedDocument.objects.bulk_create(Create_List)

    res_para_size = len(result_paragraphs)
    print(f'all para count: {res_para_size}')
    
    print(f'{c}/{res_para_size} created.')
    print(f'{not_found_size}/{res_para_size} not found.')

    print(f'{total_size_count}/{c} total revoked.')
    print(f'{partial_size_count}/{c} partial revoked.')









# تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]
def rahahan_revoked_type_peyvast_3(Country,Revoked_Doc_List,Not_Found_Docs_Count):
    #  پیوست 3 منسوخ صریح شامل (کلی و جزئی)

    start_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
        text = "پیوست 3) - منسوخ صریح و باطل شده").number

    
    end_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
        text = "پیوست 4) – غیرمعتبر با انقضای زمان اجرا").number



    result_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
    ).filter(number__gt = start_number).filter(number__lt = end_number).filter(
        text__icontains = "نسخ صریح"
    ).values()

    print(f'{len(result_paragraphs)} paragraphs found')
    revoked_type = RevokedType.objects.get(name = 'منسوخ')

    Create_List = []
    batch_size = 1000
    c = 0
    total_size_count = 0
    partial_size_count = 0
    not_found_size = 0


    for para in result_paragraphs:
        para_text =  para['text']

        # paragraph_number = para_text.split('-')[0]
        cropped_text = para_text.split('-')[1]
        affected_doc_name = cropped_text.strip()


        result_doc_id = search_affected_name_ES(Country,affected_doc_name)


        revoked_size = 'جزئی'

        if 'کل مصوبه' in para_text:
            revoked_size = 'کلی'
            revoked_clauses = 'کل مصوبه'

            total_size_count += 1
        else:
            partial_size_count += 1
            revoked_clauses = re.split("[0-9][0-9]? ?\/[0-9][0-9]? ?\/[0-9][0-9][0-9][0-9]", para_text)[-1].split('نسخ صریح')[0].strip()
            
            if len(revoked_clauses) > 50:
                revoked_clauses = '-'

        if result_doc_id != None:
 
            if result_doc_id not in Revoked_Doc_List:
                    
                Revoked_Doc_List.append(result_doc_id)
       
                RevokedDocument_obj = RevokedDocument(
                    country_id = Country,
                    revoked_type = revoked_type,
                    src_document_id = para['document_id_id'],
                    dest_document_id = result_doc_id,
                    dest_document_name = affected_doc_name,
                    revoked_sub_type = 'صریح',
                    revoked_size = revoked_size,
                    revoked_clauses = revoked_clauses,
                    src_para_id = para['id']
                )

                Create_List.append(RevokedDocument_obj)
                c += 1

        else:
            Not_Found_Docs_Count += 1

            RevokedDocument_obj = RevokedDocument(
                country_id = Country,
                revoked_type = revoked_type,
                src_document_id = para['document_id_id'],
                dest_document_name = affected_doc_name,
                revoked_sub_type = 'صریح',
                revoked_size = revoked_size,
                revoked_clauses = revoked_clauses,
                src_para_id = para['id']
            )

            Create_List.append(RevokedDocument_obj)


        if Create_List.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(Create_List)
            Create_List = []

    RevokedDocument.objects.bulk_create(Create_List)

    res_para_size = len(result_paragraphs)
    print(f'all para count: {res_para_size}')
    
    print(f'{c}/{res_para_size} created.')
    print(f'{not_found_size}/{res_para_size} not found.')

    print(f'{total_size_count}/{c} total revoked.')
    print(f'{partial_size_count}/{c} partial revoked.')


# تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]
def rahahan_revoked_type_peyvast_4(Country,Revoked_Doc_List,Not_Found_Docs_Count):
    #  پیوست 4 منقضی  شامل (کلی و جزئی)

    start_number = DocumentParagraphs.objects.get(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
        text = "پیوست 4) – غیرمعتبر با انقضای زمان اجرا").number
    
    end_number = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]").order_by("-number")[0].number



    result_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id,
        document_id__name = "تصویب نامه تنقیحی هیات وزیران در موضوع حمل و نقل ریلی (راه اهن)[تصویب نامه در خصوص مصوبات منسوخ در موضوع حمل و نقل ریلی (راه اهن)]",
    ).filter(number__gt = start_number).filter(number__lte = end_number).values()

    print(f'{len(result_paragraphs)} paragraphs found')
    revoked_type = RevokedType.objects.get(name = 'منقضی')

    Create_List = []
    batch_size = 1000
    c = 0
    total_size_count = 0
    partial_size_count = 0
    not_found_size = 0

    my_list = []

    for para in result_paragraphs:
        para_text =  para['text']

        paragraph_number = para_text.split('-')[0]
        cropped_text = para_text.split('-')[1]
        affected_doc_name = cropped_text.strip()

        result_doc_id = search_affected_name_ES(Country,affected_doc_name)

        if  para_text[-8:] == 'کل مصوبه':
            revoked_size = 'کلی'
            revoked_clauses = 'کل مصوبه'

            total_size_count += 1
        else:
            partial_size_count += 1

            revoked_size = 'جزئی'

            revoked_clauses = re.split("[0-9][0-9]? ?\/[0-9][0-9]? ?\/[0-9][0-9][0-9][0-9]", para_text)[-1].split(
                'کل مصوبه نیز')[0].strip()
            
            if len(revoked_clauses) > 50:
                revoked_clauses = '-'

        if result_doc_id != None:
                
            if result_doc_id not in Revoked_Doc_List:
                Revoked_Doc_List.append(result_doc_id)       
            
                RevokedDocument_obj = RevokedDocument(
                    country_id = Country,
                    revoked_type = revoked_type,
                    src_document_id = para['document_id_id'],
                    dest_document_id = result_doc_id,
                    dest_document_name = affected_doc_name,
                    revoked_sub_type = 'صریح',
                    revoked_size = revoked_size,
                    revoked_clauses = revoked_clauses,
                    src_para_id = para['id']
                )

                Create_List.append(RevokedDocument_obj)
                c += 1

        else:
            Not_Found_Docs_Count += 1

            RevokedDocument_obj = RevokedDocument(
                country_id = Country,
                revoked_type = revoked_type,
                src_document_id = para['document_id_id'],
                dest_document_name = affected_doc_name,
                revoked_sub_type = 'صریح',
                revoked_size = revoked_size,
                revoked_clauses = revoked_clauses,
                src_para_id = para['id']
            )

            Create_List.append(RevokedDocument_obj)


        if Create_List.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(Create_List)
            Create_List = []

    RevokedDocument.objects.bulk_create(Create_List)


    res_para_size = len(result_paragraphs)
    print(f'all para count: {res_para_size}')
    
    print(f'{c}/{res_para_size} created.')
    print(f'{not_found_size}/{res_para_size} not found.')

    print(f'{total_size_count}/{c} total revoked.')
    print(f'{partial_size_count}/{c} partial revoked.')


def mokhber_doc1_revoke_precess(Country,Revoked_Doc_List,Not_Found_Docs_Count):

    mokhber_doc1_res_para = DocumentParagraphs.objects.filter(text__iregex = r'^[1-9]',
        document_id__name = "تصویب نامه تنقیحی هیات وزیران درباره نسخ صریح مصوبات بازه زمانی 1288-11-5 تا 1299-12-29").annotate(
            document_name = F('document_id__name')
        ).values()

    revoked_type = RevokedType.objects.get(name = 'منسوخ')

    Create_List = []
    batch_size = 1000
    res_para_size = len(mokhber_doc1_res_para)
    c = 0
    not_found_size = 0
    for para in mokhber_doc1_res_para:

        para_segments = para['text'].split('-')

        affected_doc_name = para_segments[1].strip()
        result_doc_id = search_affected_name_ES(Country,affected_doc_name)
        
        if result_doc_id != None:

            if result_doc_id not in Revoked_Doc_List:
                Revoked_Doc_List.append(result_doc_id)

                c += 1
                RevokedDocument_obj = RevokedDocument(
                    country_id = Country,
                    revoked_type = revoked_type,
                    src_document_id = para['document_id_id'],
                    dest_document_id = result_doc_id,
                    dest_document_name = affected_doc_name,
                    revoked_sub_type = 'صریح',
                    revoked_size = 'کلی',
                    revoked_clauses = "کل مصوبه",
                    src_para_id = para['id']
                )

                Create_List.append(RevokedDocument_obj)


        else:
            Not_Found_Docs_Count += 1

            RevokedDocument_obj = RevokedDocument(
                country_id = Country,
                revoked_type = revoked_type,
                src_document_id = para['document_id_id'],
                dest_document_name = affected_doc_name,
                revoked_sub_type = 'صریح',
                revoked_size = 'کلی',
                revoked_clauses = "کل مصوبه",
                src_para_id = para['id']
            )

            Create_List.append(RevokedDocument_obj)
            



        if Create_List.__len__() > batch_size:
            RevokedDocument.objects.bulk_create(Create_List)
            Create_List = []

    RevokedDocument.objects.bulk_create(Create_List)
    print(f'{c}/{res_para_size} created.')


def update_document_revoked_type(Country):
    revoked_doc_ids = RevokedDocument.objects.filter(country_id__id = Country.id).values_list('dest_document_id', flat=True)
    
    revoked_docs = RevokedDocument.objects.filter(country_id__id = Country.id).annotate(
        revoked_name = F('revoked_type__name')
    ).values()
    
    Document.objects.filter(country_id__id = Country.id).update(revoked_type_name = 'معتبر')

    revoked_doc_dict = {}

    for doc in revoked_docs:
        revoked_doc_dict[doc['dest_document_id']] = {
            'revoked_name': doc['revoked_name'],
            'revoked_sub_type': doc['revoked_sub_type'],
            'revoked_size': doc['revoked_size'],
            'revoked_clauses': doc['revoked_clauses'],
        }


    batch_size = 1000

    selected_doc_list = Document.objects.filter(id__in = revoked_doc_ids)

    for doc in selected_doc_list:
        doc.revoked_type_name = revoked_doc_dict[doc.id]['revoked_name']
        doc.revoked_sub_type = revoked_doc_dict[doc.id]['revoked_sub_type']
        doc.revoked_size = revoked_doc_dict[doc.id]['revoked_size']
        doc.revoked_clauses = revoked_doc_dict[doc.id]['revoked_clauses']

    Document.objects.bulk_update(
        selected_doc_list,['revoked_type_name','revoked_sub_type', 'revoked_size', 'revoked_clauses'],batch_size)
    
    print('Document Fields updated.')

