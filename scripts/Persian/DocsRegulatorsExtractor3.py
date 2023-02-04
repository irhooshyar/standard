import json
from os import name
import re

from abdal import config
from pathlib import Path

from django.db.models import Q
from functools import reduce
import operator

from doc.models import  Document
from doc.models import DocumentParagraphs
from doc.models import RegularityTools,RegularityArea,Regulator,DocumentRegulator
import math
from itertools import chain
import time
import threading


def Slice_Dict(paragraphs_dict, n):
    results = []

    paragraphs_dict_keys = list(paragraphs_dict.keys())
    step = math.ceil(paragraphs_dict.keys().__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, paragraphs_dict_keys.__len__())
        res = {}
        for j in range(start_idx, end_idx):
            key = paragraphs_dict_keys[j]
            res[key] = paragraphs_dict[key]
        results.append(res)

    return results


def apply(folder_name, Country):
    DocumentRegulator.objects.filter(document_id__country_id = Country).delete()

    documentList = Document.objects.filter(country_id=Country)

    Mojavez_Regulator_Insert(documentList)
    # ----------------------------------------------------------------------------
    Ezn_Regulator_Insert(documentList)
    # ----------------------------------------------------------------------------
    Other_Paragraphs_Insert(documentList)

    print('Regulators completed.')



def Mojavez_Regulator_Insert(documentList):
    regulatorsList = Regulator.objects.all()
    batch_size = 1000

    # Tool = مجوز
    tool_obj = RegularityTools.objects.get(name = 'مجوز')

    pattern_keyword_1 = 'مجوز از '
    pattern_keyword_2 = 'مجوز از'
    pattern_keyword_3 = 'با مجوز '
    pattern_keyword_4 = 'مجوز رسمی '
    pattern_keyword_5 = 'مجوز رسمی از '

    pattern_keywords_list = [pattern_keyword_1,pattern_keyword_2,pattern_keyword_3,pattern_keyword_4,pattern_keyword_5]
    
    mojavez_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in pattern_keywords_list)),
    document_id__in = documentList)


    mojavez_paragraphs_dict = {}
    for para_obj in mojavez_paragraphs:
        mojavez_paragraphs_dict[para_obj.id] = {
        'document_id':para_obj.document_id.id,
        'text':para_obj.text}


    Thread_Count = config.Thread_Count
    motevali_paragraphs_dict_slices = Slice_Dict(mojavez_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in motevali_paragraphs_dict_slices:
        thread = threading.Thread(target= Mojavez_Regulator_Extractor, args=(S,regulatorsList,tool_obj,
                        pattern_keywords_list,Result_Create_List,thread_number))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))
    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentRegulator.objects.bulk_create(sub_list)

    print('Mojavez tool added.')

def Mojavez_Regulator_Extractor(mojavez_paragraphs_dict,regulatorsList,tool_obj,
                        pattern_keywords_list,Result_Create_List,thread_number):

    Create_List = []

    for paragraph_id,paragraph_info in mojavez_paragraphs_dict.items():

        paragraph_text =  paragraph_info['text']
        document_id =  paragraph_info['document_id']

        for regulator in regulatorsList:

            patterns = [(pattern_keyword + regulator.name) for pattern_keyword in pattern_keywords_list]
            
            if any(pattern in paragraph_text for pattern in patterns):
                doc_regulator =  DocumentRegulator(document_id_id = document_id,regulator_id = regulator ,tool_id = tool_obj, paragraph_id_id = paragraph_id)
                Create_List.append(doc_regulator)


    Result_Create_List[thread_number] = Create_List

# -------------------------------------------------------

def Ezn_Regulator_Insert(documentList):
    # Tool = اذن
    tool_obj = RegularityTools.objects.get(name = 'اذن')
    pattern_keyword_1 = 'اذن'
    regulator_obj = Regulator.objects.get(name = 'ولی فقیه')
    regulator_name = regulator_obj.name
    
    pattern = pattern_keyword_1 + ' ' + regulator_name

    ezn_paragraphs = DocumentParagraphs.objects.filter(text__icontains = pattern,
    document_id__in = documentList)

    ezn_paragraphs_dict = {}
    for para_obj in ezn_paragraphs:
        ezn_paragraphs_dict[para_obj.id] = {
        'document_id':para_obj.document_id.id,
        'text':para_obj.text}


    Thread_Count = config.Thread_Count
    ezn_paragraphs_dict_slices = Slice_Dict(ezn_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in ezn_paragraphs_dict_slices:
        thread = threading.Thread(target= Ezn_Regulator_Extractor, args=(S,regulator_obj,tool_obj,Result_Create_List,thread_number))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))
    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentRegulator.objects.bulk_create(sub_list)

    print('Ezn tool added.')

def Ezn_Regulator_Extractor(ezn_paragraphs_dict,regulator_obj,tool_obj,Result_Create_List,thread_number):

    Create_List = []

    for paragraph_id,paragraph_info in ezn_paragraphs_dict.items():
        doc_regulator =  DocumentRegulator(document_id_id = paragraph_info['document_id'],
        regulator_id = regulator_obj ,tool_id = tool_obj, paragraph_id_id = paragraph_id)
        Create_List.append(doc_regulator)



    Result_Create_List[thread_number] = Create_List


def Other_Paragraphs_Insert(documentList):
    # Tool = Other tools except (مجوز و اذن)
    others_tools = RegularityTools.objects.exclude(name__in = ['مجوز', 'اذن'])
  
    other_tools_name_list = [(' ' + tool.name + ' ') for tool in others_tools]

    other_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in other_tools_name_list)),
    document_id__in = documentList)


    other_paragraphs_dict = {}
    for para_obj in other_paragraphs:
        other_paragraphs_dict[para_obj.id] = {
        'document_id':para_obj.document_id.id,
        'text':para_obj.text}


    Thread_Count = config.Thread_Count
    ezn_paragraphs_dict_slices = Slice_Dict(other_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in ezn_paragraphs_dict_slices:
        thread = threading.Thread(target= Other_Paragraphs_Extractor, 
            args=(S,others_tools,Result_Create_List,thread_number))

        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))
    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentRegulator.objects.bulk_create(sub_list)


    print('Other tools added.')

def Other_Paragraphs_Extractor(other_paragraphs_dict,others_tools,Result_Create_List,thread_number):
    Create_List = []

    for paragraph_id,paragraph_info in other_paragraphs_dict.items():
        paragraph_text = paragraph_info['text']

        for tool in others_tools:
            if (' ' + tool.name + ' ') in paragraph_text:
                doc_regulator =  DocumentRegulator(document_id_id = paragraph_info['document_id'] ,tool_id = tool, paragraph_id_id = paragraph_id)
                Create_List.append(doc_regulator)

    Result_Create_List[thread_number] = Create_List


