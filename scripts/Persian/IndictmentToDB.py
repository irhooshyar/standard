import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re
import pandas as pd
from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import ApprovalReference, Country, DocumentActor,Type
from doc.models import  Document,Indictment
from datetime import datetime
import time
from difflib import SequenceMatcher


def DataFrame2Dict(df, key_field, values_field):
    result_dict = {}
    for index, row in df.iterrows():
        data_list = {}
        for field in values_field:
            data_list[field] = row[field]
        result_dict[row[key_field]] = data_list

    return result_dict

def standardFileName(name):

    if type(name) != float:
        name = name.replace(".", "")
        name = arabicCharConvert(name)
        name = persianNumConvert(name)
        name = name.strip()

        while "  " in name:
            name = name.replace("  "," ")

    return name

def persianNumConvert(text):
    persian_num_dict = {"۱": "1" ,"۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹":"9" , "۰": "0" }
    for key, value in persian_num_dict.items():
        text = text.replace(key, value)
    return text

def arabicCharConvert(text):
    arabic_char_dict = {"ى": "ی" ,"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ":" ", "\n\n":"\n", "\n ":"\n" , }
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)

    return text

def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text

def numbers_preprocessing(text):
  persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
  arabicNumbers  = ['٠','١', '٢', '٣','٤', '٥', '٦','٧', '٨', '٩']
  for c in persianNumbers:
    text = text.replace(c, str(ord(c)-1776))
  for c in arabicNumbers:
    text = text.replace(c, str(ord(c)-1632))
  return text

def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)
    text = numbers_preprocessing(text)

    return text



def apply(folder_name, Country):

    # edit_file_names(Country)

    update_approval_reference(Country)

    # indictment_to_db(Country)
    # print('Indictment inserted to DB.')

def edit_file_names(Country):
    batch_size = 1000
    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation.xlsx'))

    df = pd.read_excel(excelFile)
    nan_count = df['title'].isna().sum()
    print(f'{nan_count} is nan.')

    df.dropna(subset=['title'],inplace=True)

    df['title'] = df['title'].apply(lambda x: standardFileName(x))

    title_list = df['title'].unique()

    selected_ara = Document.objects.filter(
        country_id=Country,
        name__in = title_list)
    
    dataframe_dictionary = DataFrame2Dict(df, "title", 
    ["id"])


    for doc in selected_ara:
        doc.file_name = dataframe_dictionary[doc.name]['id']

    Document.objects.bulk_update(
        selected_ara,['file_name'],batch_size)



def update_approval_reference(Country):
    batch_size = 1000

    approval_ref_obj = ApprovalReference.objects.get(name = 'دیوان عدالت اداری')
    type_obj = Type.objects.get(name = 'رأی')
    
    print(approval_ref_obj)
    print(type_obj)

    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation.xlsx'))

    df = pd.read_excel(excelFile)
    nan_count = df['title'].isna().sum()
    print(f'{nan_count} is nan.')

    df.dropna(subset=['title'],inplace=True)

    df['title'] = df['title'].apply(lambda x: standardFileName(x))

    title_list = df['title'].unique()

    selected_ara = Document.objects.filter(
        country_id=Country,
        name__in = title_list)

    for doc in selected_ara:
        doc.type_name = 'رای'


    Document.objects.bulk_update(
        selected_ara,[
        'type_name'],batch_size)


def indictment_to_db(Country):

    Indictment.objects.all().delete()

    batch_size = 1000

    Create_List = []

    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation.xlsx'))

    df = pd.read_excel(excelFile)
    nan_count = df['title'].isna().sum()

    df.dropna(subset=['title'],inplace=True)
    
    print(f'{nan_count} is nan.')

    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df['effected_legislation'] = df['effected_legislation'].apply(lambda x: standardFileName(x))

    dataframe_dictionary = DataFrame2Dict(df, "title", 
    ["number", "categories","conclusion","effected_legislation"])


    title_list = df['title'].unique()

    selected_ara = Document.objects.filter(
        country_id=Country,
        name__in = title_list)

    ara_count = selected_ara.count()
    print(f'Count= {ara_count}')

    for doc in selected_ara:
        doc_name = doc.name
        indictment_number = dataframe_dictionary[doc_name]['number']
        categories = dataframe_dictionary[doc_name]['categories']
        conclusion = dataframe_dictionary[doc_name]['conclusion']
        affected_document_name = dataframe_dictionary[doc_name]['effected_legislation']

        new_indictment_obj = Indictment(document_id = doc,
            indictment_number = indictment_number,
            categories = categories,
            conclusion = conclusion,
            affected_document_name = affected_document_name)
        
        Create_List.append(new_indictment_obj)  

        if Create_List.__len__() > batch_size:
            Indictment.objects.bulk_create(Create_List)
            Create_List = []

    Indictment.objects.bulk_create(Create_List)


def get_null_title(Country):

    all_result = Indictment.objects.all().values('document_id__name')

    batch_size = 1000

    Create_List = []

    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation.xlsx'))

    df = pd.read_excel(excelFile)
    nan_count = df['title'].isna().sum()

    df.dropna(subset=['title'],inplace=True)
    
    print(f'{nan_count} is nan.')

    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df['effected_legislation'] = df['effected_legislation'].apply(lambda x: standardFileName(x))

    dataframe_dictionary = DataFrame2Dict(df, "title", 
    ["number", "categories","conclusion","effected_legislation"])


    title_list = df['title'].unique()

    selected_ara = Document.objects.filter(
        country_id=Country,
        name__in = title_list)

    ara_count = selected_ara.count()
    print(f'Count= {ara_count}')

    for doc in selected_ara:
        doc_name = doc.name
        indictment_number = dataframe_dictionary[doc_name]['number']
        categories = dataframe_dictionary[doc_name]['categories']
        conclusion = dataframe_dictionary[doc_name]['conclusion']
        affected_document_name = dataframe_dictionary[doc_name]['effected_legislation']

        new_indictment_obj = Indictment(document_id = doc,
            indictment_number = indictment_number,
            categories = categories,
            conclusion = conclusion,
            affected_document_name = affected_document_name)
        
        Create_List.append(new_indictment_obj)  

        if Create_List.__len__() > batch_size:
            Indictment.objects.bulk_create(Create_List)
            Create_List = []

    Indictment.objects.bulk_create(Create_List)
