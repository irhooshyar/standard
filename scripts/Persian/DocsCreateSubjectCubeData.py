
import operator
import re

from doc.models import  Document,DocumentWords,DocumentParagraphs
from doc.models import CUBE_Subject_TableData,Subject
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time

import math



def apply(folder_name, Country,host_url):

    create_TableData_CUBE(Country,host_url)

   

def create_TableData_CUBE(Country,host_url):
    start_t = time.time()

    Create_List = []

    CUBE_Subject_TableData.objects.filter(country_id=Country).delete()

    subject_list = Document.objects.filter(country_id=Country).exclude(subject_id=None).values('subject_id_id', "subject_name").distinct()

    for subject in subject_list:

        sub_id = subject["subject_id_id"]
        sub_name = subject["subject_name"]

        index = 1
        result_list = []
        doc_list = Document.objects.filter(country_id=Country, subject_id=sub_id).order_by("-subject_weight")
        for doc in doc_list:

            doc_id = doc.id
            doc_name = doc.name
            doc_link = 'http://'+host_url+'/information/?id=' + str(doc_id)
            doc_tag = '<a class="document_link" ' +'target="blank" href="' + doc_link + '">' + doc_name +"</a>"

            doc_subject = doc.subject_name
            subject_weight = doc.subject_weight
            doc_level = doc.level_name if doc.level_name !=None else 'نامشخص'
 
            approval_reference = doc.approval_reference_name if doc.approval_reference_name !=None else 'نامشخص'

            approval_date = doc.approval_date if doc.approval_date != None else 'نامشخص'

            function = "DetailFunction(" + str(doc_id) + ")"
            detail_btn = '<button ' \
                'type="button" ' \
                'class="btn modal_btn" ' \
                'data-bs-toggle="modal" ' \
                'data-bs-target="#detailModal" ' \
                'onclick="' + function + '"' \
                '>' + 'جزئیات' + '</button>'

            json_value = {"id": index,
                          "document_subject": doc_subject,
                          "document_id":doc_id,
                          "document_name": doc_name,
                          "document_tag":doc_tag,
                          "document_approval_reference": approval_reference,
                          "document_approval_date": approval_date,
                          "document_subject_weight": subject_weight,
                          "document_level":doc_level,
                          "detail": detail_btn}

            result_list.append(json_value)
            index +=1

        table_data_json = {
            "data": result_list
        }

        cube_obj = CUBE_Subject_TableData(
                                            country_id=Country,
                                            subject_id_id=sub_id,
                                            subject_name=sub_name,
                                            table_data=table_data_json)

        Create_List.append(cube_obj)

    batch_size = 1000
    slice_count = math.ceil(Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Create_List.__len__())
        sub_list = Create_List[start_idx:end_idx]
        CUBE_Subject_TableData.objects.bulk_create(sub_list)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ')')

