
import operator

from doc.models import  Document,DocumentWords, CUBE_SubjectStatistics_FullData,CUBE_SubjectStatistics_ChartData
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time

from functools import reduce
from django.db.models import Q
import operator

from scripts.Persian import Preprocessing


def arabic_preprocessing(text):
    text = text.lstrip().rstrip().strip()
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def apply(folder_name, Country):


    start_t = time.time()

    CUBE_SubjectStatistics_FullData.objects.filter(country_id=Country).delete()


    tabs_info = {
        'Budget_Info':{
            'tab_name':'قوانین بودجه',
            'tab_keywords':['قانون بودجه']
        },
        'Barname_Info':{
            'tab_name':'برنامه توسعه',
            'tab_keywords':['برنامه پنجساله','برنامه پنج‌ساله','برنامه پنج ساله',
            'برنامه چهارم توسعه','برنامه سوم توسعه'
            ,'برنامه دوم توسعه','برنامه اول توسعه',
            'برنامه ششم توسعه','برنامه اول توسعه']
        }
    }

    Create_List = []
    batch_size = 10000
    
    result_docs = Document.objects.filter(country_id = Country)
    

    for key,value in tabs_info.items():
        result_docs = Document.objects.filter(country_id = Country)
        
        tab_name = key
        document_tab_type = value['tab_name']
        keyword_list = value['tab_keywords']
        
        # preprocess search text
        # keyword_list = [arabic_preprocessing(kw) for kw in keyword_list]

        result_docs = result_docs.filter(reduce(operator.or_, (Q(name__icontains = kw) for kw in keyword_list)))


        for doc in result_docs:

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


            CUBE_SubjectStatistics_FullData_Obj = CUBE_SubjectStatistics_FullData(country_id = Country,
            document_id = doc,
            document_name = doc_name,
            document_tab_type = document_tab_type,
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

            Create_List.append(CUBE_SubjectStatistics_FullData_Obj)

        if Create_List.__len__() > batch_size:
            CUBE_SubjectStatistics_FullData.objects.bulk_create(Create_List)
            Create_List = []
            
    CUBE_SubjectStatistics_FullData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('Budget & Barname added (' + str(end_t - start_t) + ').')

# ----------------------   Create Chart Data  -------------------------------------------
    Create_List = []
    start_t = time.time()
    CUBE_SubjectStatistics_ChartData.objects.filter(country_id=Country).delete()

    for key,value in tabs_info.items():

        document_tab_type = value['tab_name']

        doc_list = CUBE_SubjectStatistics_FullData.objects.filter(
        country_id=Country,
        document_tab_type = document_tab_type)

        subject_data = {}
        approval_references_data = {}
        level_data = {}
        approval_year_data = {}
        type_data = {}

        for doc in doc_list:
            # Generate chart Data

            subject_name = doc.subject_name

            approval_reference_name = doc.approval_reference_name

            level_name = doc.level_name

            type_name = doc.type_name

            doc_approval_year = doc.approval_date


            if doc.approval_date != 'نامشخص':
                doc_approval_year = doc.approval_date[0:4]
            

            if subject_name not in subject_data:
                subject_data[subject_name] = 1
            else:
                subject_data[subject_name]+= 1

            if approval_reference_name not in approval_references_data:
                approval_references_data[approval_reference_name] =1
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


        subject_chart_data = []
        approval_reference_chart_data = []
        level_chart_data = []
        approval_year_chart_data = []
        type_chart_data = []


        for key,value in subject_data.items():
            subject_chart_data.append([key,value])

        for key,value in approval_references_data.items():
            approval_reference_chart_data.append([key,value])

        for key,value in level_data.items():
            level_chart_data.append([key,value])

        for key,value in approval_year_data.items():
            approval_year_chart_data.append([key,value])

        for key,value in type_data.items():
            type_chart_data.append([key,value])


        subject_chart_data_json = {"data":subject_chart_data}
        level_chart_data_json = {"data":level_chart_data}
        type_chart_data_json = {"data":type_chart_data}
        approval_reference_chart_data_json = {"data":approval_reference_chart_data}
        approval_year_chart_data_json = {"data":approval_year_chart_data}

        cube_obj = CUBE_SubjectStatistics_ChartData(
            country_id = Country,
            document_tab_type = document_tab_type,
            subject_chart_data = subject_chart_data_json,
            level_chart_data = level_chart_data_json,
            type_chart_data = type_chart_data_json,
            approval_reference_chart_data = approval_reference_chart_data_json,
            approval_year_chart_data = approval_year_chart_data_json
        )

        Create_List.append(cube_obj)

    CUBE_SubjectStatistics_ChartData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('Chart Data added (' + str(end_t - start_t) + ').')