
import operator
import re
from unittest import result

from doc.models import  Document,DocumentKeywords,DocumentParagraphs
from doc.models import CUBE_Votes_FullData,CUBE_Votes_ChartData,CUBE_Votes_TableData
from django.db.models import Count, Q,F
import json
from abdal import config
from pathlib import Path
import time

from functools import reduce
from django.db.models import Q
import operator

from scripts.Persian import Preprocessing

def apply(folder_name, Country,host_url):
    create_FullData_CUBE(Country)
    create_ChartData_CUBE(Country)
    create_TableData_CUBE(Country, host_url)

def create_FullData_CUBE(Country):


    start_t = time.time()

    CUBE_Votes_FullData.objects.filter(country_id=Country).delete()


    Create_List = []
    batch_size = 10000
    
    result_docs = Document.objects.filter(
        country_id=Country, type_name='رای').order_by('name')

    for doc in result_docs:
        doc_id = doc.id
        doc_name = doc.name

        subject_id = doc.subject_id
        subject_name = doc.subject_name if subject_id !=None else 'نامشخص'

        level_id = doc.level_id
        level_name = doc.level_name if level_id !=None else 'نامشخص'


        type_id = doc.type_id
        type_name = doc.type_name if type_id !=None else 'نامشخص'

        approval_reference_id = doc.approval_reference_id
        approval_reference_name = doc.approval_reference_name if approval_reference_id !=None else 'نامشخص'

        approval_date = doc.approval_date if doc.approval_date !=None else 'نامشخص'

        communicated_date = doc.communicated_date if doc.communicated_date !=None else 'نامشخص'

        document_keywords = DocumentKeywords.objects.filter(document_id=doc_id).values(
            'keyword_id__word').annotate(keyword = F('keyword_id__word')).order_by('keyword').distinct()

        doc_kw_list = [kw['keyword'] for kw in document_keywords]
        doc_kw_count = len(doc_kw_list)

        doc_kw_list = ','.join(doc_kw_list)

        CUBE_Votes_FullData_obj = CUBE_Votes_FullData(country_id = Country,
        document_id = doc,
        document_name = doc_name,
        keyword_list = doc_kw_list,
        keyword_count = doc_kw_count,
        subject_id = subject_id,
        subject_name = subject_name,
        type_id = type_id,
        type_name = type_name,
        level_id = level_id,
        level_name = level_name,
        approval_reference_id = approval_reference_id,
        approval_reference_name = approval_reference_name,
        approval_date = approval_date,
        communicated_date = communicated_date)

        Create_List.append(CUBE_Votes_FullData_obj)

        if Create_List.__len__() > batch_size:
            CUBE_Votes_FullData.objects.bulk_create(Create_List)
            Create_List = []
            
    CUBE_Votes_FullData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_FullData added (' + str(end_t - start_t) + ')')

def create_ChartData_CUBE(Country):

    batch_size = 10000
    Create_List = []

    start_t = time.time()
    CUBE_Votes_ChartData.objects.filter(country_id=Country).delete()

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}
    keywords_data = {}

    doc_list = CUBE_Votes_FullData.objects.filter(country_id = Country)

    for doc in doc_list:
        # Generate chart Data
        subject_name = doc.subject_name

        approval_reference_name = doc.approval_reference_name

        level_name = doc.level_name

        type_name = doc.type_name

        doc_approval_year = doc.approval_date

        if doc_approval_year != 'نامشخص':
            doc_approval_year = doc.approval_date[0:4]
            

        if subject_name not in subject_data:
            subject_data[subject_name] = 1
        else:
            subject_data[subject_name] += 1

        if approval_reference_name not in approval_references_data:
            approval_references_data[approval_reference_name] = 1
        else:
            approval_references_data[approval_reference_name] += 1

        if level_name not in level_data:
            level_data[level_name] = 1
        else:
            level_data[level_name] += 1

        if type_name not in type_data:
            type_data[type_name] = 1
        else:
            type_data[type_name] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = 1
        else:
            approval_year_data[doc_approval_year] += 1

        doc_kw_list = doc.keyword_list.split(',')
        
        for kw in doc_kw_list:
            if kw != '':
                if kw not in keywords_data:
                    keywords_data[kw] = 1
                else:
                    keywords_data[kw] += 1



    subject_chart_data = []
    approval_reference_chart_data = []
    level_chart_data = []
    approval_year_chart_data = []
    type_chart_data = []
    keywords_chart_data = []


    for key,value in subject_data.items():
            subject_chart_data.append([key,value])

    for key,value in approval_references_data.items():
            approval_reference_chart_data.append([key,value])

    for key,value in level_data.items():
            level_chart_data.append([key,value])

    for key,value in approval_year_data.items():
            if key != "نامشخص" and "/" not in key:
                approval_year_chart_data.append([int(key),value])
            else:
                approval_year_chart_data.append([0, value])

    for key,value in type_data.items():
            type_chart_data.append([key,value])


    for key,value in keywords_data.items():
        keywords_chart_data.append([key,value])

    approval_year_chart_data = list(sorted(approval_year_chart_data, key=lambda x: x[0]))


    for i in range(approval_year_chart_data.__len__()):
        temp = list(approval_year_chart_data[i])
        if temp[0] == 0:
            temp[0] = "نامشخص"

    subject_chart_data_json = {"data":subject_chart_data}
    level_chart_data_json = {"data":level_chart_data}
    type_chart_data_json = {"data":type_chart_data}
    approval_reference_chart_data_json = {"data":approval_reference_chart_data}
    approval_year_chart_data_json = {"data":approval_year_chart_data}
    keywords_chart_data_json = {"data":keywords_chart_data}

    cube_obj = CUBE_Votes_ChartData(
        country_id = Country,
        subject_chart_data = subject_chart_data_json,
        level_chart_data = level_chart_data_json,
        type_chart_data = type_chart_data_json,
        approval_reference_chart_data = approval_reference_chart_data_json,
        approval_year_chart_data = approval_year_chart_data_json,
        keywords_chart_data = keywords_chart_data_json
        )

    Create_List.append(cube_obj)

    if Create_List.__len__() > batch_size:
        CUBE_Votes_ChartData.objects.bulk_create(Create_List)
        Create_List = []

    CUBE_Votes_ChartData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_ChartData added (' + str(end_t - start_t) + ').')

def create_TableData_CUBE(Country,host_url):
    start_t = time.time()

    batch_size = 10000
    result_list = []
    Create_List = []

    CUBE_Votes_TableData.objects.filter(country_id=Country).delete()
    doc_list = CUBE_Votes_FullData.objects.filter(country_id = Country).order_by('-keyword_count')

    index = 1
    
    for doc in doc_list:

        doc_id = doc.document_id.id
        doc_name = doc.document_name
        doc_link = 'http://'+host_url+'/information/?id=' + str(doc_id)
        doc_tag = '<a class="document_link" ' +'target="to_blank" href="' + doc_link + '">' + doc_name +"</a>"

        doc_subject = doc.subject_name
        doc_level = doc.level_name
        doc_type = doc.type_name

        approval_reference = doc.approval_reference_name

        approval_date = doc.approval_date


        keyword_list = doc.keyword_list.replace(',',' - ')
        keywords_count = doc.keyword_count
        
        function = "SelectDocumentFunction(this)"

        checkbox_btn = '<input ' \
              'type="checkbox" ' \
              'value="' + str(doc_id) + '" ' \
                                    'class="doc_checkbox form-check-input d-inline-block" ' \
                                    'onchange="' + function + '"' \
                                                              '>' + '</input>'

        json_value = {"id": index, "document_subject": doc_subject,"document_id":doc_id, "document_name": doc_name,"document_tag":doc_tag, "document_approval_reference": approval_reference,
                "document_approval_date": approval_date,"document_level":doc_level,"document_type":doc_type, "document_keywords" : keyword_list,"keywords_count":keywords_count , "checkbox": checkbox_btn}

        result_list.append(json_value)
        index +=1

    table_data_json = {
        "data":result_list
    }

    cube_obj = CUBE_Votes_TableData(
                country_id = Country,
                table_data = table_data_json)

    Create_List.append(cube_obj)
        
        
    CUBE_Votes_TableData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ').')
