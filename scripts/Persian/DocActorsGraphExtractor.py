import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

import numpy as np
from django.db.models import Q, F

from abdal import config
from pathlib import Path

from doc.models import Country, DocumentActor, CUBE_ActorTimeSeries_TableData, CUBE_ActorArea_GraphData
from doc.models import Document
from doc.models import ActorTimeSeries, Actor
from doc.models import DocumentParagraphs, DocumentGeneralDefinition, \
    ActorGraphType, ActorsGraph

from datetime import datetime
import time
from difflib import SequenceMatcher
import math
import pandas as pd
import spacy
import heapq


def apply(folder_name, Country):
    batch_size = 1000
    Create_List = []

    table_rows_count = ActorTimeSeries.objects.filter(country_id__id=Country.id).count()
    result_count = table_rows_count * table_rows_count - table_rows_count

    actors_info = ActorTimeSeries.objects.filter(country_id__id=Country.id)

    corr_graph_type = ActorGraphType.objects.get(name='گراف همبستگی')

    ActorsGraph.objects.filter(country_id=Country, graph_type_id=corr_graph_type).delete()

    role_names = ['همه', 'متولی اجرا', 'همکار', 'دارای صلاحیت اختیاری']

    get_similarity_graph(folder_name, Country)
    get_area_actor_graph(folder_name, Country)

    i = 0
    for row in actors_info:
        src_actor_obj = row.actor_id

        for role_name in role_names:
            src_actor_year_vector = row.time_series_data[role_name]
            src_actor_year_count = pd.Series(list(src_actor_year_vector.values()))

            # ---------------- Selected Actor Vector  --------------------

            other_actors = ActorTimeSeries.objects.filter(
                country_id__id=Country.id).exclude(actor_id__id=src_actor_obj.id)

            for res in other_actors:
                other_actor_obj = res.actor_id

                role_year_vector = res.time_series_data[role_name]
                other_actor_year_count = pd.Series(list(role_year_vector.values()))
                correlation_value = round(src_actor_year_count.corr(other_actor_year_count), 2)

                if not math.isnan(correlation_value):
                    edge_obj = ActorsGraph(
                        country_id=Country,
                        src_actor_id=src_actor_obj,
                        dest_actor_id=other_actor_obj,
                        role_type=role_name,
                        graph_type_id=corr_graph_type,
                        similarity_value=correlation_value

                    )

                    Create_List.append(edge_obj)
                    i += 1
                    print('row count: ' + str(i) + "/" + str(result_count))

        if Create_List.__len__() > batch_size:
            ActorsGraph.objects.bulk_create(Create_List)
            Create_List = []

    ActorsGraph.objects.bulk_create(Create_List)


def get_area_actor_graph(folder_name, Country):
    batch_size = 10000
    role_names = ['متولی اجرا', 'همکار', 'دارای صلاحیت اختیاری', 'همه']
    # role_names = ['متولی اجرا']
    if ActorGraphType.objects.filter(name='گراف کلان حوزه ها').count() == 0:
        ActorGraphType.objects.create(name='گراف کلان حوزه ها')
    area_graph_type = ActorGraphType.objects.get(name='گراف کلان حوزه ها')
    CUBE_ActorArea_GraphData.objects.filter(country_id=Country, graph_type_id=area_graph_type).delete()

    for role_name in role_names:
        area_connections_dict = {}
        paragraphs = DocumentActor.objects.filter(document_id__country_id=Country).\
            exclude(actor_id__area__id__isnull=True)
        if role_name != 'همه':
            paragraphs = paragraphs.filter(actor_type_id__name=role_name)
        paragraphs = paragraphs.values('paragraph_id__id', 'paragraph_id__text', 'actor_type_id__name',
                                       'actor_id__name', 'current_actor_form', 'actor_id__area__name', 'actor_id__id',
                                       'actor_id__area__id').order_by('paragraph_id__id')
        same_paragraph_list = []
        count = 0
        total = len(paragraphs)
        for paragraph in paragraphs:
            count += 1
            print(f'{round(count/total,2)}%')
            if len(same_paragraph_list) != 0 and \
                    same_paragraph_list[-1]['paragraph_id__id'] != paragraph['paragraph_id__id']:
                area_connections_dict = create_actor_connections(same_paragraph_list, area_connections_dict)
                same_paragraph_list = []
            same_paragraph_list.append(paragraph)
        area_connections_dict = create_actor_connections(same_paragraph_list, area_connections_dict)

        Create_List = []
        # count = 0
        for key in area_connections_dict.keys():
            # if key != '3#1':
            #     continue
            # count += 1
            key1, key2 = key.split('#')
            # print(f'{key1}-{key2}')
            edge_obj = CUBE_ActorArea_GraphData(
                # id=count,
                country_id=Country,
                src_actor_area_id_id=key1,
                dest_actor_area_id_id=key2,
                role_type=role_name,
                graph_type_id=area_graph_type,
                similarity_value=sum([
                    len(area_connections_dict[key]['actors'][key_]['paragraphs'])
                    for key_ in area_connections_dict[key]['actors'].keys()
                ])/10,
                edge_detail=area_connections_dict[key]
            )
            Create_List.append(edge_obj)
            if Create_List.__len__() > batch_size:
                CUBE_ActorArea_GraphData.objects.bulk_create(Create_List)
                Create_List = []

        print(Create_List)
        CUBE_ActorArea_GraphData.objects.bulk_create(Create_List)
        # print('here4')

    print(f"similarity graph added.")
    return


def get_similarity_graph(folder_name, Country):
    batch_size = 10000
    role_names = ['متولی اجرا', 'همکار', 'دارای صلاحیت اختیاری', 'همه']
    # role_names = [ 'دارای صلاحیت اختیاری']
    similarity_graph_type = ActorGraphType.objects.get(name='گراف کلیدواژگان یکسان')
    ActorsGraph.objects.filter(country_id=Country, graph_type_id=similarity_graph_type).delete()
    nlp = spacy.load('en_core_web_sm')
    # nlp.max_length = 5000000
    not_keyword_list = load_stop_words()
    not_keyword_list.append("")

    all_actors = Actor.objects.all().values('id', 'forms')

    for role_name in role_names:
        actors_dict = {}
        for actor in all_actors:
            actors_dict[actor['id']] = {'forms': actor['forms'].split('/'), 'keywords': {}, 'text': ''}
        # print('here1')
        paragraphs = DocumentActor.objects.filter(document_id__country_id=Country)
        if role_name != 'همه':
            paragraphs = paragraphs.filter(actor_type_id__name=role_name)
        paragraphs = paragraphs.values('paragraph_id__text', 'actor_id__id')
        for paragraph in paragraphs:
            text = paragraph['paragraph_id__text'].replace('.', ' ')
            actor_id = paragraph['actor_id__id']

            # find keywords
            for form in actors_dict[actor_id]['forms']:
                text = text.replace(form, '')
            text_split = text.split(' ')
            for word in text_split:
                word = word.strip()
                if word in not_keyword_list or word == '' or any(char.isdigit() for char in word):
                    continue
                if word not in actors_dict[actor_id]['keywords'].keys():
                    actors_dict[actor_id]['keywords'][word] = 1
                else:
                    actors_dict[actor_id]['keywords'][word] += 1

            # find paragraph vector
            actors_dict[actor_id]['text'] += (" " + text)

        # print('here2')
        # find actor embedding vector
        for key in actors_dict.keys():
            temp = actors_dict[key]['text'].replace("  ", " ").strip()
            if temp == '':
                continue
            if len(temp) > nlp.max_length:
                nlp.max_length = len(temp) + 100
                print(f'changed to {nlp.max_length}')
            actors_dict[key]['vector'] = nlp(temp)

        # print('here3')
        Create_List = []
        done = {}
        for key1 in actors_dict.keys():
            done[key1] = []
            for key2 in actors_dict.keys():
                if key2 == key1 \
                        or 'vector' not in actors_dict[key2].keys() \
                        or 'vector' not in actors_dict[key1].keys() \
                        or (key2 in done.keys() and key1 in done[key2]):
                    continue
                done[key1].append(key2)
                keywords = get_top_common_keywords(actors_dict[key1]['keywords'], actors_dict[key2]['keywords'])
                similarity = actors_dict[key1]['vector'].similarity(actors_dict[key2]['vector'])
                edge_obj = ActorsGraph(
                    country_id=Country,
                    src_actor_id_id=key1,
                    dest_actor_id_id=key2,
                    role_type=role_name,
                    graph_type_id=similarity_graph_type,
                    similarity_value=round(pow(similarity, 100),2),
                    edge_detail={'keywords': keywords}
                )
                Create_List.append(edge_obj)
                if Create_List.__len__() > batch_size:
                    ActorsGraph.objects.bulk_create(Create_List)
                    Create_List = []

        ActorsGraph.objects.bulk_create(Create_List)
        # print('here4')

    print(f"similarity graph added.")
    return


def get_top_common_keywords(actor1, actor2):
    top = 10
    keywords = {}
    for key in actor1.keys():
        if key in actor2.keys():
            keywords[key] = min(actor1[key], actor2[key])
    top_keys = heapq.nlargest(top, keywords, key=keywords.get)
    return {key: f'{actor1[key]} , {actor2[key]}' for key in top_keys}


def load_stop_words():
    stop_words = []
    stop_words_file = str(Path(config.PERSIAN_PATH, 'stopwords.txt'))
    with open(stop_words_file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            stop_words.append(line)
    f.close()
    return stop_words


def create_actor_connections(actors: list, actors_connections_dict: dict):
    for index1 in range(len(actors)):
        for index2 in range(len(actors)):
            if index2 <= index1 or actors[index1]['actor_type_id__name'] != actors[index2]['actor_type_id__name'] \
                    or actors[index1]['actor_id__area__id'] == actors[index2]['actor_id__area__id']:
                continue
            all_keys = actors_connections_dict.keys()
            first_key = index1
            second_key = index2
            key = str(actors[first_key]['actor_id__area__id']) + "#" + str(actors[second_key]['actor_id__area__id'])
            if key not in all_keys:
                first_key = index2
                second_key = index1
                key = str(actors[first_key]['actor_id__area__id']) + "#" + str(actors[second_key]['actor_id__area__id'])
            if key not in all_keys:
                actors_connections_dict[key] = {
                    'src': actors[first_key]['actor_id__area__name'],
                    'dest': actors[second_key]['actor_id__area__name'],
                    'actors': {}
                }
            actors_key = str(actors[first_key]['actor_id__id']) + "#" + str(actors[second_key]['actor_id__id'])
            if actors_key not in actors_connections_dict[key]['actors']:
                actors_connections_dict[key]['actors'][actors_key] = {
                    'col1': actors[first_key]['actor_id__name'],
                    'col2': actors[second_key]['actor_id__name'],
                    'paragraphs': [], 'forms': []
                }
            actors_connections_dict[key]['actors'][actors_key]['paragraphs'] = \
                append_if_not_exist(actors_connections_dict[key]['actors'][actors_key]['paragraphs'],
                                    actors[first_key]['paragraph_id__text'])
            actors_connections_dict[key]['actors'][actors_key]['forms'] = \
                append_if_not_exist(actors_connections_dict[key]['actors'][actors_key]['forms'],
                                    actors[first_key]['current_actor_form'])
            actors_connections_dict[key]['actors'][actors_key]['forms'] = \
                append_if_not_exist(actors_connections_dict[key]['actors'][actors_key]['forms'],
                                    actors[second_key]['current_actor_form'])
    return actors_connections_dict


def append_if_not_exist(list_: list, item):
    if item not in list_:
        list_.append(item)
    return list_
