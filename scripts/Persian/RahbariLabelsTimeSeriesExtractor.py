import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country
from doc.models import  Document,Rahbari
from doc.models import RahbariLabel,RahbariLabelsTimeSeries,Actor
from doc.models import DocumentParagraphs
from datetime import datetime
import time
from difflib import SequenceMatcher
import math



def apply(folder_name, Country):
    createLabelimeSeries(Country)


def createLabelimeSeries(Country):
    batch_size = 500
    Create_List = []

    RahbariLabelsTimeSeries.objects.all().delete()

    year_list = Rahbari.objects.all().exclude(rahbari_year = "0").values('rahbari_year')
    doc_list = Rahbari.objects.all().exclude(rahbari_year = "0").exclude(labels = "نامشخص").values()


    doc_years = []

    for row in year_list:
        rahbari_year = int(row['rahbari_year'])
        doc_years.append(rahbari_year)
    
    doc_years = sorted(doc_years)

    label_year_dict = {}
    
    for doc in doc_list:
        labels = doc['labels']
        rahbari_year = int(doc['rahbari_year'])

        if labels[-1] == "؛":
            labels = labels[:-1]

        label_list = labels.split("؛")

        if '' in label_list:
            label_list.remove('')

        if ' ' in label_list:
            label_list.remove(' ')

        for label_item in label_list:

            label_item = label_item.strip().replace("؛", "").replace("ائمه جمعه", "ائمه‌ جمعه").replace("ورزش‌کاران", "ورزشکاران")
            label_object = RahbariLabel.objects.get(name = label_item)
            label_name = label_object.name

            if label_name not in label_year_dict:
                label_year_dict[label_name] = dict.fromkeys(doc_years,0)
                

            if rahbari_year not in label_year_dict[label_name]:
                label_year_dict[label_name][rahbari_year] = 1
            else:
                label_year_dict[label_name][rahbari_year] += 1

    print(len(label_year_dict))
    for label_name,year_dict in label_year_dict.items():
        label_object = RahbariLabel.objects.get(name = label_name)

        new_obj = RahbariLabelsTimeSeries(
        rahbari_label = label_object,
        time_series_data = year_dict)
                                
        Create_List.append(new_obj)  
        # print(f"{c}/{res_count}")


    RahbariLabelsTimeSeries.objects.bulk_create(Create_List)


    print('label`s time-series vector created.')

