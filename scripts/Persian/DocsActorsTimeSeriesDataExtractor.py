import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country, DocumentActor,CUBE_ActorTimeSeries_TableData
from doc.models import  Document
from doc.models import ActorTimeSeries,Actor
from doc.models import DocumentParagraphs,DocumentGeneralDefinition
from datetime import datetime
import time
from difflib import SequenceMatcher
import math



def apply(folder_name, Country):
    createActorTimeSeries(Country)
    # create_CUBE_ActorTimeSeries_TableData(Country)


def createActorTimeSeries(Country):
    batch_size = 1000
    Create_List = []

    documentList = Document.objects.filter(country_id=Country)

    ActorTimeSeries.objects.filter(country_id = Country).delete()

    doc_dates = DocumentActor.objects.filter(
        document_id__id__in = documentList).annotate(
        approval_date = F('document_id__approval_date')).exclude(
            approval_date__isnull = True).values(
        'approval_date').distinct()

    doc_years = []

    for date in doc_dates:
        date_str = date['approval_date']
        year = int(date_str[:4])
        if year not in doc_years:
            doc_years.append(year)
    
    doc_years = sorted(doc_years)


    # ----------  Documents-Actors to DB  ---------------------
    country_actors = DocumentActor.objects.filter(
        document_id__id__in = documentList).values('actor_id').distinct()

    print(len(country_actors))
    actorsList = Actor.objects.filter(id__in = country_actors)

    actor_year_dict = {}
    role_names = ['متولی اجرا','همکار','دارای صلاحیت اختیاری','همه']
    
    res_count = len(actorsList)
    c = 0
    for actor in actorsList:
        c+= 1
        time_series_json = {'همه':{},'متولی اجرا':{},'همکار':{},'دارای صلاحیت اختیاری':{}}
        
        for role_name in role_names:
            actor_year_dict = dict.fromkeys(doc_years,0)

            actor_dates = DocumentActor.objects.filter(
                document_id__id__in =documentList,
                actor_id__id = actor.id)

            if role_name == 'همه':
                actor_dates = actor_dates.annotate(
                    approval_date = F('document_id__approval_date')).exclude(
                    approval_date__isnull = True).values(
                    'approval_date')
            else:

                actor_dates = actor_dates.filter(
                actor_type_id__name = role_name
                ).annotate(
                approval_date = F('document_id__approval_date')).exclude(
                approval_date__isnull = True).values(
                'approval_date')

            for date in actor_dates:
                year = int(date['approval_date'][:4])

                if year not in actor_year_dict:
                    actor_year_dict[year] = 1
                else:
                    actor_year_dict[year] += 1


            time_series_json[role_name] = actor_year_dict

        actor_vector = ActorTimeSeries(country_id = Country,actor_id = actor,
        time_series_data = time_series_json)
                                
        Create_List.append(actor_vector)  
        print(f"{c}/{res_count}")

        if Create_List.__len__() > batch_size:
            ActorTimeSeries.objects.bulk_create(Create_List)
            Create_List = []

    ActorTimeSeries.objects.bulk_create(Create_List)
    

    initial_time_series_json = {'ARIMA': {
        'همه': {
            'RMSE': 'نامشخص',
            'Prediction': {},
            'Test': {},
            'BestParameters':()
        },
        'متولی اجرا': {
            'RMSE': 'نامشخص',
            'Prediction': {},
            'Test': {},
            'BestParameters':()
        },
        'همکار': {
            'RMSE': 'نامشخص',
            'Prediction': {},
            'Test': {},
            'BestParameters':()
        },
        'دارای صلاحیت اختیاری': {
            'RMSE': 'نامشخص',
            'Prediction': {},
            'Test': {},
            'BestParameters':()
        }
    }
    }

    ActorTimeSeries.objects.filter(country_id__id = Country.id).update(time_series_prediction_data = initial_time_series_json)


    print('Actor`s time-series vector created.')

def create_CUBE_ActorTimeSeries_TableData(Country):
    CUBE_ActorTimeSeries_TableData.objects.filter(country_id__id = Country.id).delete()

    similarity_result = {}
    table_result = []
    Create_List = []
    role_names = ['همه','متولی اجرا','همکار','دارای صلاحیت اختیاری']



    all_actors_with_time_series = ActorTimeSeries.objects.filter(
        country_id__id = Country.id).values('actor_id').distinct()


    for actor in all_actors_with_time_series:
        selected_actor_ID = actor['actor_id']
        
        selected_actor = ActorTimeSeries.objects.get(
            country_id__id = Country.id,
            actor_id__id = selected_actor_ID)

        # ---------------- Selected Actor Vector  --------------------
        for role_name in role_names:
            selected_actor_year_vector = selected_actor.time_series_data[role_name]

            selected_vector_temp = 0
            selected_vector_size = 0

            for year,count in selected_actor_year_vector.items():
                selected_vector_temp += pow(count,2)

            selected_vector_size = math.sqrt(selected_vector_temp)   

            # ---------------- Selected Actor Vector  --------------------

            other_actors = ActorTimeSeries.objects.filter(
                country_id = Country).exclude(actor_id__id = selected_actor_ID)
            

            for res in other_actors:
                actor_ID = res.actor_id.id
                actor_Name = res.actor_id.name

                role_year_vector = res.time_series_data[role_name]

                dot_product = 0
                vector_temp = 0
                vector_size = 0

                for year,count in role_year_vector.items():
                    dot_product += count*selected_actor_year_vector[year]
                    vector_temp += pow(count,2)

                vector_size = math.sqrt(vector_temp)
                
                divided_value = vector_size*selected_vector_size
                divided_result = divided_value if divided_value !=0 else  -1

                cosine_similarity_value = round(dot_product/(divided_result),2)

                if actor_ID not in similarity_result:
                    similarity_result[actor_ID] = {
                        "actor_name":actor_Name,
                        role_name:cosine_similarity_value
                    } 
                else:
                    similarity_result[actor_ID][role_name] = cosine_similarity_value
            
        i = 1
        print(similarity_result.items().__len__())

        for actor_id,actor_info in similarity_result.items():
            if any(actor_info[key] > 0 for key in actor_info if key!='actor_name'):

                function = "DetailFunction(" + str(Country.id) + ",'" + str(actor_id) + "')"
                detail_btn = '<button ' \
                            'type="button" ' \
                            'class="btn modal_btn" ' \
                            'data-bs-toggle="modal" ' \
                            'data-bs-target="#myModal" ' \
                            'onclick="' + function + '"' \
                                                    '>' + 'جزئیات' + '</button>'

                row = {
                    "id":i,
                    "actor_id" : actor_id,
                    "actor_name" : actor_info["actor_name"],
                    "motevali_sim":actor_info["متولی اجرا"],
                    "hamkar_sim":actor_info["همکار"],
                    "salahiat_sim":actor_info["دارای صلاحیت اختیاری"],
                    "total_sim":actor_info["همه"],
                    "detail":detail_btn
                }

                table_result.append(row)
                i+=1
                

        sorted_table_result = sorted(table_result, key=lambda d: d['total_sim'],reverse=True)
        
        cube_obj = CUBE_ActorTimeSeries_TableData(
            country_id = Country,
            actor_id_id = selected_actor_ID,
            table_data = sorted_table_result
        )

        Create_List.append(cube_obj)
        print(len(Create_List))

    CUBE_ActorTimeSeries_TableData.objects.bulk_create(Create_List)
    print('CUBE_ActorTimeSeries TableData created.')