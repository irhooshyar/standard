import operator
import re

from doc.models import Document, DocumentWords, DocumentParagraphs, DocumentRegulator
from doc.models import Document, DocumentWords, SubjectArea,SubjectSubArea,DocumentSubjectSubArea
from doc.models import CUBE_DocumentSubjectArea_TableData,RevokedDocument
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time
import math


from functools import reduce
from django.db.models import Q
import operator

from scripts.Persian import Preprocessing


def apply(folder_name, Country, host_url):
    create_TableData_CUBE(Country, host_url)



def create_TableData_CUBE(Country, host_url):
    start_t = time.time()

    batch_size = 10000
    Create_List = []

    CUBE_DocumentSubjectArea_TableData.objects.filter(country_id=Country).delete()


    SubjectArea_Dict = {}

    SubjectSubArea_list = SubjectSubArea.objects.all()


    for sub_area in SubjectSubArea_list:

        sub_area_id = sub_area.id
        subject_area_id = sub_area.subject_area_id.id
        
        if subject_area_id not in SubjectArea_Dict:
            SubjectArea_Dict[subject_area_id] = [0,sub_area_id]

        else:
            SubjectArea_Dict[subject_area_id].append(sub_area_id)

    subject_area_count = 0
    all_area_count = len(SubjectArea_Dict.keys())

    for subject_area_id, sub_subject_list in SubjectArea_Dict.items():

        for sub_subject_id in sub_subject_list:
            if sub_subject_id == 0:

                doc_list = Document.objects.filter(
                country_id=Country,
                # type_id__name = 'قانون',
                subject_area_id=subject_area_id).order_by("-subject_sub_area_weight")

            else:
                doc_list = Document.objects.filter(
                country_id=Country,
                # type_id__name = 'قانون',
                subject_sub_area_id=sub_subject_id).order_by("-subject_sub_area_weight")

            index = 1
            result_list = []

            for doc in doc_list:

                doc_id = doc.id
                doc_name = doc.name
                doc_link = 'http://'+host_url+'/information/?id=' + str(doc_id)
                doc_tag = '<a class="document_link" ' +'target="blank" href="' + doc_link + '">' + doc_name +"</a>"

                doc_subject_area_name = doc.subject_area_name
                doc_subject_sub_area_name = doc.subject_sub_area_name
                
                doc_subject_sub_area_weight = doc.subject_sub_area_weight

                doc_revoked_type_name =  doc.revoked_type_name

                revoked_size = "کل مصوبه"

                try:
                    revoked_size = RevokedDocument.objects.get(dest_document__id = doc_id).revoked_size
                except:
                    revoked_size = "کل مصوبه"

                revoked_sub_type = 'نامشخص'
                try:
                    revoked_sub_type = RevokedDocument.objects.get(dest_document__id = doc_id).revoked_sub_type
                except:
                    revoked_sub_type = 'نامشخص'

                approval_date = doc.approval_date if doc.approval_date != None else 'نامشخص'
                
                revoked_msg = doc_revoked_type_name + "( "+ revoked_size + ")"

                function = "DetailFunction(" + str(doc_id) + ")"
                detail_btn = '<button ' \
                    'type="button" ' \
                    'class="btn modal_btn" ' \
                    'data-bs-toggle="modal" ' \
                    'data-bs-target="#detailModal" ' \
                    'onclick="' + function + '"' \
                    '>' + 'جزئیات' + '</button>'

                json_value = {"id": index,
                            "doc_subject_area_name": doc_subject_area_name,
                            "doc_subject_sub_area_name":doc_subject_sub_area_name,
                            "revoked_msg":revoked_msg,
                            "document_id":doc_id,
                            "document_name": doc_name,
                            "document_tag":doc_tag,
                            "document_approval_date": approval_date,
                            "doc_subject_sub_area_weight": doc_subject_sub_area_weight,
                            "revoked_type_name": doc_revoked_type_name,
                            "revoked_size": revoked_size,
                            "revoked_sub_type": revoked_sub_type,
                            "detail": detail_btn}

                result_list.append(json_value)
                index +=1

            table_data_json = result_list

            cube_obj = CUBE_DocumentSubjectArea_TableData(
                                                country_id=Country,
                                                subject_area_id=subject_area_id,
                                                subject_sub_area_id=sub_subject_id,
                                                table_data=table_data_json)

            Create_List.append(cube_obj)
            subject_area_count += 1
            print(f'{subject_area_count}/{all_area_count}')




    batch_size = 1000
    slice_count = math.ceil(Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Create_List.__len__())
        sub_list = Create_List[start_idx:end_idx]
        CUBE_DocumentSubjectArea_TableData.objects.bulk_create(sub_list)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ')')
