
import operator
import re

from doc.models import  Document,DocumentWords,DocumentParagraphs,DocumentActor
from doc.models import CUBE_Template_FullData,CUBE_Template_ChartData,CUBE_Template_TableData
from django.db.models import Count, Q,F
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


def GetExistedKeywords_ByDocumentId(document_id , kw_template):
    result_keywords = []

    for kw, kw_tmp in kw_template.items():
        
        kw_flag = DocumentParagraphs.objects.filter(
            document_id__id = document_id,
            text__icontains = kw_tmp
        ).exists()

        if kw_flag and kw not in result_keywords:
            result_keywords.append(kw)

    result_keywords = ','.join(result_keywords)

    return result_keywords





def apply(folder_name, Country,host_url):

    create_FullData_CUBE(Country)

    create_ChartData_CUBE(Country)

    create_TableData_CUBE(Country,host_url)

   


def create_FullData_CUBE(Country):


    start_t = time.time()

    CUBE_Template_FullData.objects.filter(country_id=Country).delete()

    keywords_template = {
        'سکو' : ' ' + 'سکو' + ' ', # space + kw + space
        'سامانه': ' ' + 'سامانه', # space + kw
        'درگاه': ' ' + 'درگاه' # space + kw
    }

    Create_List = []
    batch_size = 10000
    
    document_list = Document.objects.filter(country_id = Country).values('id')
    
    result_doc_ids = DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains = kw) for kw in keywords_template.values())),
        document_id__in = document_list
    ).values('document_id').distinct()

    result_docs = Document.objects.filter(id__in = result_doc_ids)

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


        doc_kw_list = GetExistedKeywords_ByDocumentId(doc.id,keywords_template)
        doc_kw_count = len(doc_kw_list)

        # motevalian = doc.motevalian
        # hamkaran =  doc.hamkaran
        # salahiat =  doc.salahiat

        motevalian = GetKeywordsActors_ByRole(doc_id,'متولی اجرا',keywords_template)
        hamkaran =  GetKeywordsActors_ByRole(doc_id,'همکار',keywords_template)
        salahiat =  GetKeywordsActors_ByRole(doc_id,'دارای صلاحیت اختیاری',keywords_template)

        CUBE_Template_FullData_Obj = CUBE_Template_FullData(country_id = Country,
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
        communicated_date = communicated_date,
        motevalian = motevalian,
        hamkaran = hamkaran,
        salahiat = salahiat)

        Create_List.append(CUBE_Template_FullData_Obj)

        if Create_List.__len__() > batch_size:
            CUBE_Template_FullData.objects.bulk_create(Create_List)
            Create_List = []
            
    CUBE_Template_FullData.objects.bulk_create(Create_List)
    end_t = time.time()
    print('CUBE_FullData added (' + str(end_t - start_t) + ')')

def create_ChartData_CUBE(Country):

    batch_size = 10000
    Create_List = []

    start_t = time.time()
    CUBE_Template_ChartData.objects.filter(country_id=Country).delete()

    country_subjects = Document.objects.filter(country_id = Country).values('subject_name').distinct()
    
    subject_list = ['همه']
    for subject in country_subjects:

        subject_name = subject['subject_name']

        if subject_name != None:
            subject_list.append(subject_name)


    for subject in subject_list:
        if subject == 'همه':
            doc_list = CUBE_Template_FullData.objects.filter(country_id = Country)
        else:
            doc_list = CUBE_Template_FullData.objects.filter(
                country_id = Country,
                subject_name = subject)

        subject_data = {}
        approval_references_data = {}
        level_data = {}
        approval_year_data = {}
        type_data = {}

        actors_data = {}

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

            #-------------------- Actors chart data ---------------------------

            if doc.motevalian != None:
                doc_motevalian = doc.motevalian.split(',')

                for motevali in doc_motevalian:
                    if motevali not in actors_data:
                        actors_data[motevali] = {
                            'motevali':1,
                            'hamkar':0,
                            'salahiat':0
                        }
                    else:
                        actors_data[motevali]['motevali'] += 1


            if doc.hamkaran != None:
                doc_hamkaran = doc.hamkaran.split(',')

                for hamkar in doc_hamkaran:
                    if hamkar not in actors_data:
                        actors_data[hamkar] = {
                            'motevali':0,
                            'hamkar':1,
                            'salahiat':0
                        }
                    else:
                        actors_data[hamkar]['hamkar'] += 1

            if doc.salahiat != None:
                doc_salahiat = doc.salahiat.split(',')
                    
                for salahiat in doc_salahiat:
                    if salahiat not in actors_data:
                        actors_data[salahiat] = {
                            'motevali':0,
                            'hamkar':0,
                            'salahiat':1
                        }
                    else:
                        actors_data[salahiat]['salahiat'] += 1
        
       # ---------------------------------------------------
        subject_chart_data = []
        approval_reference_chart_data = []
        level_chart_data = []
        approval_year_chart_data = []
        type_chart_data = []

        actors_chart_data = []


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

        for actor_name,role_info in actors_data.items():
            motevali_count = role_info['motevali']
            hamkar_count = role_info['hamkar']
            salahiat_count = role_info['salahiat']

            column = [actor_name,motevali_count,hamkar_count,salahiat_count]
            actors_chart_data.append(column)

        subject_chart_data_json = {"data":subject_chart_data}
        level_chart_data_json = {"data":level_chart_data}
        type_chart_data_json = {"data":type_chart_data}
        approval_reference_chart_data_json = {"data":approval_reference_chart_data}
        approval_year_chart_data_json = {"data":approval_year_chart_data}
        actors_chart_data_json = {"data":actors_chart_data}

        cube_obj = CUBE_Template_ChartData(
            country_id = Country,
            subject_name = subject,
            subject_chart_data = subject_chart_data_json,
            level_chart_data = level_chart_data_json,
            type_chart_data = type_chart_data_json,
            approval_reference_chart_data = approval_reference_chart_data_json,
            approval_year_chart_data = approval_year_chart_data_json,
            actors_chart_data = actors_chart_data_json,
        )

        Create_List.append(cube_obj)

        if Create_List.__len__() > batch_size:
            CUBE_Template_ChartData.objects.bulk_create(Create_List)
            Create_List = []

    CUBE_Template_ChartData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_ChartData added (' + str(end_t - start_t) + ').')

def create_TableData_CUBE(Country,host_url):
    start_t = time.time()

    batch_size = 10000


    CUBE_Template_TableData.objects.filter(country_id=Country).delete()

    country_subjects = Document.objects.filter(country_id = Country).values('subject_name').distinct()
    
    subject_list = ['همه']
    for subject in country_subjects:

        subject_name = subject['subject_name']

        if subject_name != None:
            subject_list.append(subject_name)

    Create_List = []
    for subject in subject_list:

        if subject == 'همه':
            doc_list = CUBE_Template_FullData.objects.filter(
                country_id = Country).order_by('-keyword_count')
        else:
            doc_list = CUBE_Template_FullData.objects.filter(
                country_id = Country,
                subject_name = subject).order_by('-keyword_count')


        index = 1
        result_list = []
        for doc in doc_list:

            doc_id = doc.document_id.id
            doc_name = doc.document_name
            doc_link = 'http://'+host_url+'/information/?id=' + str(doc_id)
            doc_tag = '<a class="document_link" ' +'target="blank" href="' + doc_link + '">' + doc_name +"</a>"

            doc_subject = doc.subject_name

            approval_reference = doc.approval_reference_name

            approval_date = doc.approval_date


            keyword_list = doc.keyword_list.replace(',',' - ')
            keywords_count = doc.keyword_count
            function = "DetailFunction(" + str(doc_id) + ")"
            detail_btn = '<button ' \
                'type="button" ' \
                'class="btn modal_btn" ' \
                'data-bs-toggle="modal" ' \
                'data-bs-target="#detailModal" ' \
                'onclick="' + function + '"' \
                                        '>' + 'جزئیات' + '</button>'

            json_value = {"id": index, "document_subject": doc_subject,"document_id":doc_id, "document_name": doc_name,"document_tag":doc_tag, "document_approval_reference": approval_reference,
                "document_approval_date": approval_date, "document_keywords" : keyword_list,"keywords_count":keywords_count , "detail": detail_btn}

            result_list.append(json_value)
            index +=1

        table_data_json = {
            "data":result_list
        }

        cube_obj = CUBE_Template_TableData(
                country_id = Country,
                subject_name = subject,
                table_data = table_data_json)

        Create_List.append(cube_obj)
        
        
    CUBE_Template_TableData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ').')


def GetKeywordsActors_ByRole(doc_id,actor_role,keywords_template):
    actor_list = []

    document_actors = DocumentActor.objects.filter(
        reduce(operator.or_, (Q(paragraph_id__text__icontains = kw) for kw in keywords_template.values())),
        document_id_id=doc_id,
        actor_type_id__name=actor_role).annotate(
        actor_name=F('actor_id__name')).values('actor_name').distinct()

    # fill actor list
    actor_list = [actor['actor_name'] for actor in document_actors]


    actor_list = ','.join(actor_list)
    
    if actor_list == '':
        return None
    else:
        return actor_list

