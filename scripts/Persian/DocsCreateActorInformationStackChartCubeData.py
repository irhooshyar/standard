import operator
import re

from doc.models import Document, DocumentWords, DocumentParagraphs, DocumentRegulator, ActorArea, ActorSubArea, DocumentActor, Actor
from doc.models import CUBE_Business_Advisor_TableData, Regulator, RegularityArea, CUBE_Business_Advisor_ChartData ,CUBE_MaxMinEffectActorsInArea_ChartData
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time
from itertools import chain, groupby
from functools import reduce
from django.db.models import Q
import operator

from scripts.Persian import Preprocessing

def apply(folder_name, Country, host_url):
    create_ChartData_CUBE(Country, host_url)

def create_ChartData_CUBE(Country, host_url):
    batch_size = 10000
    Create_List = []

    start_t = time.time()
    CUBE_MaxMinEffectActorsInArea_ChartData.objects.filter(country = Country).delete()

    ActorArea_list = ActorArea.objects.all().values('id')
    ActorSubArea_dict = {}
    temp_list = [0]
    for item1 in ActorArea_list:
        # Regularity_list = ActorSubArea.objects.filter(main_area__id=item1['id']).values_list('id', flat=True)
        # temp_list = list(Regularity_list)
        # temp_list.append(0)
        ActorSubArea_dict[item1['id']] = temp_list

    # ActorSubArea_dict[0] = list(ActorSubArea.objects.all().values_list('id', flat=True))
    # ActorSubArea_dict[0].append(0)

    ActorSubArea_dict[0] = [0]

    for ActorArea_id, ActorSubArea_list_id in ActorSubArea_dict.items():
        for ActorSubArea_id in ActorSubArea_list_id:

            index = 1
            result_list = []

            # Filter by regulator
            if ActorSubArea_id != 0:
                doc_paragraphs = DocumentActor.objects.filter(
                    document_id__country_id__id=Country.id, actor_id__area__id = ActorArea_id)
                    # document_id__country_id__id=Country.id, actor_id__area__id = ActorArea_id, actor_id__sub_area__id = ActorSubArea_id)
            else:
                # Filter by area
                if ActorArea_id != 0:
                    doc_paragraphs = DocumentActor.objects.filter(
                        document_id__country_id__id=Country.id, actor_id__area__id = ActorArea_id)
                else:
                    # all area
                    doc_paragraphs = DocumentActor.objects.filter(document_id__country_id__id = Country.id)

            result = doc_paragraphs
            actors_without_duty_years = {}
            all_actors = []
            actors_information_dict = {}
            actors_chart_data = []
            actors_chart_data_dic = {}
            if ActorArea_id == 0:
                actors = Actor.objects.all().values(
                        'id', 'name').distinct().order_by('name')
            else:
                actors = Actor.objects.filter(area__id =ActorArea_id).values(
                        'id', 'name').distinct().order_by('name')
            for actor in actors:
                all_actors.append(actor['name'])
                actors_without_duty_years[actor['name']] = []

            result_without_year = list(filter(lambda x: x.document_id.approval_date == None,result)) 
            result = filter(lambda x: x.document_id.approval_date != None,result) # just for docs which have date
            
            # start without year
            if len(result_without_year) > 0:
                for res in result_without_year:
                    actor_id = res.actor_id.id
                    actor_name = res.actor_id.name
                    actor_role_name = res.actor_type_id.name
                    actor_paragraph_id = res.paragraph_id.id
                    if actor_id not in actors_information_dict:
                        actors_information_dict[actor_id] = {
                            'actor_name': actor_name,
                            'roles_info': {
                                'متولی اجرا': [],
                                'همکار': [],
                                'دارای صلاحیت اختیاری': []
                            }
                        }
                        actor_roles_info = actors_information_dict[actor_id]['roles_info']
                        actor_roles_info[actor_role_name].append(actor_paragraph_id)
                        actors_information_dict[actor_id]['roles_info'] = actor_roles_info
                    else:
                        actor_roles_info_2 = actors_information_dict[actor_id]['roles_info']
                        if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                            actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                            actors_information_dict[actor_id]['roles_info'] = actor_roles_info_2
                tmp = []
                # Calculate role frequency of actors in a year
                for actor_id in actors_information_dict:
                    actor_name = actors_information_dict[actor_id]['actor_name']
                    motevali_count = len(actors_information_dict[actor_id]['roles_info']['متولی اجرا'])
                    hamkar_count = len(actors_information_dict[actor_id]['roles_info']['همکار'])
                    salahiat_count = len(actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری'])
                    frequency = motevali_count + hamkar_count + salahiat_count
                    actor_paragraph__motevali_ids = actors_information_dict[actor_id]['roles_info']['متولی اجرا']
                    actor_paragraph_hamkar_ids = actors_information_dict[actor_id]['roles_info']['همکار']
                    actor_paragraph_salahiat_ids = actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری']
                    column_data = [actor_name, motevali_count, hamkar_count, salahiat_count , frequency,
                                    actor_paragraph__motevali_ids, actor_paragraph_hamkar_ids, actor_paragraph_salahiat_ids]   
                    # column_data = [actor_name, motevali_count, hamkar_count, salahiat_count , frequency]
                    tmp.append(column_data)
                max_year = max(tmp, key=lambda x: x[4])
                min_year = min(tmp, key=lambda x: x[4])
                # max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4] , "نامشخص"] # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year
                max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4] , "نامشخص", max_year[5], max_year[6], max_year[7]] # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year
                min_year_data = [min_year[0], min_year[1], min_year[2], min_year[3], min_year[4] , "نامشخص", min_year[5], min_year[6], min_year[7]]
                # actors_chart_data.append(max_year_data) # if it is not good use dictionary {}
                # actors_chart_data.append(min_year_data)
                if (max_year == min_year):
                    min_year_data = ["ندارد", 0, 0, 0, 0 , "نامشخص", None, None, None]

                actors_chart_data_dic["نامشخص"] = [max_year_data,min_year_data]
                actors_chart_data.append(["نامشخص", max_year_data[4],max_year_data[0], min_year_data[4], min_year_data[0]]) # year , max_frequency , max_actor , min_frequency , min_actor
            ### end without year
            
            key = lambda x: int(x.document_id.approval_date[0:4]) # or communicated_date[0:4]
            result_per_year = groupby(sorted(result,key=key), key=key)

            for year, year_result in result_per_year:
                tmp_actors = all_actors
                actors_information_dict = {}
                year_result = list(year_result)
                for res in year_result:
                    actor_id = res.actor_id.id
                    actor_name = res.actor_id.name
                    try:
                        tmp_actors.remove(actor_name)
                    except ValueError:
                        pass
                    actor_role_name = res.actor_type_id.name
                    actor_paragraph_id = res.paragraph_id.id

                    if actor_id not in actors_information_dict:
                        actors_information_dict[actor_id] = {
                            'actor_name': actor_name,
                            'roles_info': {
                                'متولی اجرا': [],
                                'همکار': [],
                                'دارای صلاحیت اختیاری': []
                            }
                        }
                        actor_roles_info = actors_information_dict[actor_id]['roles_info']
                        actor_roles_info[actor_role_name].append(actor_paragraph_id)
                        actors_information_dict[actor_id]['roles_info'] = actor_roles_info

                    else:
                        actor_roles_info_2 = actors_information_dict[actor_id]['roles_info']
                        if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                            actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                            actors_information_dict[actor_id]['roles_info'] = actor_roles_info_2

                tmp = []
                # Calculate role frequency of actors in a year
                for actor_id in actors_information_dict:
                    actor_name = actors_information_dict[actor_id]['actor_name']
                    motevali_count = len(actors_information_dict[actor_id]['roles_info']['متولی اجرا'])
                    hamkar_count = len(actors_information_dict[actor_id]['roles_info']['همکار'])
                    salahiat_count = len(actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری'])
                    frequency = motevali_count + hamkar_count + salahiat_count
                    actor_paragraph__motevali_ids = actors_information_dict[actor_id]['roles_info']['متولی اجرا']
                    actor_paragraph_hamkar_ids = actors_information_dict[actor_id]['roles_info']['همکار']
                    actor_paragraph_salahiat_ids = actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری']
                    column_data = [actor_name, motevali_count, hamkar_count, salahiat_count , frequency,
                                    actor_paragraph__motevali_ids, actor_paragraph_hamkar_ids, actor_paragraph_salahiat_ids]   
                    # column_data = [actor_name, motevali_count, hamkar_count, salahiat_count , frequency]
                    tmp.append(column_data)
                
                max_year = max(tmp, key=lambda x: x[4])
                min_year = min(tmp, key=lambda x: x[4])
                # max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4] , year] # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year
                max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4] , year, max_year[5], max_year[6], max_year[7]] # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year, actor_paragraph__motevali_ids, actor_paragraph_hamkar_ids, actor_paragraph_salahiat_ids
                min_year_data = [min_year[0], min_year[1], min_year[2], min_year[3], min_year[4] , year, min_year[5], min_year[6], min_year[7]]
                # actors_chart_data.append(max_year_data) # if it is not good use dictionary {}
                # actors_chart_data.append(min_year_data)
                if (max_year == min_year):
                    min_year_data = ["ندارد", 0, 0, 0, 0 , "نامشخص", None, None, None]
                
                actors_chart_data_dic[year] = [max_year_data,min_year_data]
                actors_chart_data.append([year, max_year_data[4],max_year_data[0], min_year_data[4], min_year_data[0]]) # year , max_frequency , max_actor , min_frequency , min_actor
                for a in tmp_actors:
                    actors_without_duty_years[a].append(year)

            chart_data_json = {
                    "actors_chart_data": actors_chart_data,
                    "actors_chart_data_dic": actors_chart_data_dic,
                    "actors_without_duty_years": actors_without_duty_years
                }

            cube_obj = CUBE_MaxMinEffectActorsInArea_ChartData(
                    country = Country,
                    area_id = ActorArea_id,
                    sub_area_id = ActorSubArea_id,
                    chart_data = chart_data_json)

            Create_List.append(cube_obj)

            if Create_List.__len__() > batch_size:
                    CUBE_MaxMinEffectActorsInArea_ChartData.objects.bulk_create(Create_List)
                    Create_List = []



    CUBE_MaxMinEffectActorsInArea_ChartData.objects.bulk_create(Create_List)
    
    end_t = time.time()
    print('CUBE_StackChartData added (' + str(end_t - start_t) + ').')
