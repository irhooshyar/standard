import operator
import re

from doc.models import Document, DocumentWords, DocumentParagraphs, DocumentRegulator
from doc.models import CUBE_Business_Advisor_TableData, Regulator, RegularityArea, CUBE_Business_Advisor_ChartData
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time



from functools import reduce
from django.db.models import Q
import operator

from scripts.Persian import Preprocessing


def apply(folder_name, Country, host_url):
    create_TableData_CUBE(Country, host_url)
    create_ChartData_CUBE(Country, host_url)


def create_TableData_CUBE(Country, host_url):
    start_t = time.time()

    batch_size = 10000
    Create_List = []
    a =True

    CUBE_Business_Advisor_TableData.objects.filter(country_id=Country).delete()


    RegularityArea_list = RegularityArea.objects.all().values('id')
    Regularity_dict = {}
    for item1 in RegularityArea_list:
        Regularity_list = Regulator.objects.filter(area_id__id=item1['id']).values_list('id', flat=True)
        temp_list = list(Regularity_list)
        temp_list.append(0)
        Regularity_dict[item1['id']] = temp_list

    Regularity_dict[0] = list(Regulator.objects.all().values_list('id', flat=True))
    Regularity_dict[0].append(0)
    person_list = ['حقیقی', 'حقوقی']


    for RegularityArea_id, Regulator_list_id in Regularity_dict.items():
        for Regulator_id in Regulator_list_id:
            for person_id in person_list:

                index = 1
                result_list = []

                # Filter by regulator
                if Regulator_id != 0:
                    doc_paragraphs = DocumentRegulator.objects.filter(
                        document_id__country_id__id=Country.id, regulator_id__id=Regulator_id)
                else:
                    # Filter by area
                    if RegularityArea_id != 0:
                        doc_paragraphs = DocumentRegulator.objects.filter(
                            document_id__country_id__id=Country.id, regulator_id__area_id__id=RegularityArea_id)
                    else:
                        # all area
                        doc_paragraphs = DocumentRegulator.objects.filter(
                            document_id__country_id__id=Country.id)

                # Filter by person
                result_doc_ids = []

                if person_id == "حقیقی":
                    words = ['اشخاص حقیقی', 'شخص حقیقی']
                    result_doc_ids = doc_paragraphs. \
                        filter(reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in words))).values('document_id__id').distinct()

                if person_id == "حقوقی":
                    words = ['اشخاص حقوقی', 'شخص حقوقی']
                    result_doc_ids = doc_paragraphs. \
                        filter(reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in words))).values('document_id__id').distinct()

                result_docs = Document.objects.filter(id__in=result_doc_ids)
                result_count = result_docs.count()

                if result_count != 0:
                    for doc in result_docs:

                        doc_id = doc.id
                        country_name = Country.name
                        doc_name = doc.name
                        doc_link = 'http://' + host_url + '/information/?id=' + str(doc_id)
                        doc_tag = '<a class="document_link" ' + 'target="to_blank" href="' + doc_link + '">' + doc_name + "</a>"

                        doc_subject = doc.subject_name
                        subject_weight = doc.subject_weight
                        doc_level = doc.level_name if doc.level_name != None else 'نامشخص'

                        approval_reference = doc.approval_reference_name if doc.approval_reference_name != None else 'نامشخص'

                        approval_date = doc.approval_date if doc.approval_date != None else 'نامشخص'


                        function = "DetailFunction(" + str(doc_id)  + ")"
                        detail_btn = '<button ' \
                                     'type="button" ' \
                                     'class="btn modal_btn" ' \
                                     'data-bs-toggle="modal" ' \
                                     'data-bs-target="#detailModal" ' \
                                     'onclick="' + function + '"' \
                                                              '>' + 'جزئیات' + '</button>'

                        json_value = {"id": index, 'document_id': doc_id, "document_subject": doc_subject,
                                      "country": country_name,
                                      "document_name": doc_name,
                                      "document_tag": doc_tag, "document_approval_reference": approval_reference,
                                      "document_approval_date": approval_date,
                                      "document_subject_weight": subject_weight,
                                      "document_level": doc_level, "detail": detail_btn}

                        result_list.append(json_value)
                        index += 1

                table_data_json = {
                    "data": result_list
                }

                cube_obj = CUBE_Business_Advisor_TableData(
                    country_id=Country,
                    area_id=RegularityArea_id,
                    regulator_id = Regulator_id,
                    person_id = person_id,
                    table_data=table_data_json)

                Create_List.append(cube_obj)

    CUBE_Business_Advisor_TableData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ')')

def create_ChartData_CUBE(Country, host_url):
    batch_size = 10000
    Create_List = []

    start_t = time.time()
    CUBE_Business_Advisor_ChartData.objects.filter(country_id=Country).delete()

    RegularityArea_list = RegularityArea.objects.all().values('id')
    Regularity_dict = {}
    for item1 in RegularityArea_list:
        Regularity_list = Regulator.objects.filter(area_id__id=item1['id']).values_list('id', flat=True)
        temp_list = list(Regularity_list)
        temp_list.append(0)
        Regularity_dict[item1['id']] = temp_list

    Regularity_dict[0] = list(Regulator.objects.all().values_list('id', flat=True))
    Regularity_dict[0].append(0)
    person_list = ['حقیقی', 'حقوقی']


    for RegularityArea_id, Regulator_list_id in Regularity_dict.items():
        for Regulator_id in Regulator_list_id:
            for person_id in person_list:

                doc_list = CUBE_Business_Advisor_TableData.objects.filter(
                    country_id=Country,
                    area_id=RegularityArea_id,
                    regulator_id=Regulator_id,
                    person_id=person_id).values("table_data")

                subject_data = {}
                approval_references_data = {}
                level_data = {}
                approval_year_data = {}

                for doc_dict in doc_list:
                    for doc in doc_dict['table_data']['data']:
                        # Generate chart Data

                        subject_name = doc["document_subject"]
                        approval_reference_name = doc["document_approval_reference"]
                        level_name = doc['document_level']
                        doc_approval_year = doc['document_approval_date']


                        if doc_approval_year != 'نامشخص':
                            doc_approval_year = doc['document_approval_date'][0:4]

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

                        if doc_approval_year not in approval_year_data:
                            approval_year_data[doc_approval_year] = 1
                        else:
                            approval_year_data[doc_approval_year] += 1


                # ---------------------------------------------------
                subject_chart_data = []
                approval_reference_chart_data = []
                level_chart_data = []
                approval_year_chart_data = []


                for key,value in subject_data.items():
                    subject_chart_data.append([key,value])

                for key,value in approval_references_data.items():
                    approval_reference_chart_data.append([key,value])

                for key,value in level_data.items():
                    level_chart_data.append([key,value])

                for key,value in approval_year_data.items():
                    approval_year_chart_data.append([key,value])


                subject_chart_data_json = {"data":subject_chart_data}
                level_chart_data_json = {"data":level_chart_data}
                approval_reference_chart_data_json = {"data":approval_reference_chart_data}
                approval_year_chart_data_json = {"data":approval_year_chart_data}

                cube_obj = CUBE_Business_Advisor_ChartData(
                    country_id = Country,
                    area_id=RegularityArea_id,
                    regulator_id=Regulator_id,
                    person_id=person_id,
                    subject_chart_data = subject_chart_data_json,
                    level_chart_data = level_chart_data_json,
                    approval_reference_chart_data = approval_reference_chart_data_json,
                    approval_year_chart_data = approval_year_chart_data_json,
                )

                Create_List.append(cube_obj)

                if Create_List.__len__() > batch_size:
                    CUBE_Business_Advisor_ChartData.objects.bulk_create(Create_List)
                    Create_List = []

    CUBE_Business_Advisor_ChartData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_ChartData added (' + str(end_t - start_t) + ').')







































