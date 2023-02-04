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



def apply(folder_name, Country):

    documentList = Document.objects.filter(country_id=Country)

    # Remove DocumentRegulator for input country
    DocumentRegulator.objects.filter(document_id__country_id = Country).delete()

    # ----------  Regulators to DB  ---------------------
    regulatorsList = Regulator.objects.all()
    Create_List = []
    batch_size = 1000

    # Tool = مجوز
    tool = RegularityTools.objects.get(name = 'مجوز')

    pattern_keyword_1 = 'مجوز از '
    pattern_keyword_2 = 'مجوز از'
    pattern_keyword_3 = 'با مجوز '
    pattern_keyword_4 = 'مجوز رسمی '
    pattern_keyword_5 = 'مجوز رسمی از '

    pattern_keywords_list = [pattern_keyword_1,pattern_keyword_2,pattern_keyword_3,pattern_keyword_4,pattern_keyword_5]
    
    mojavez_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in pattern_keywords_list)),
    document_id__in = documentList)

    for paragraph in mojavez_paragraphs:
        paragraph_text =  paragraph.text

        for regulator in regulatorsList:

            patterns = [(pattern_keyword + regulator.name) for pattern_keyword in pattern_keywords_list]
            
            if any(pattern in paragraph_text for pattern in patterns):
                doc_regulator =  DocumentRegulator(document_id = paragraph.document_id,regulator_id = regulator ,tool_id = tool, paragraph_id = paragraph)
                Create_List.append(doc_regulator)


        if Create_List.__len__() > batch_size:
            DocumentRegulator.objects.bulk_create(Create_List)
            Create_List = []

    DocumentRegulator.objects.bulk_create(Create_List)

    print('Mojavez tool added.')

    # ----------------------------------------------------------------------------
    # Tool = اذن
    tool = RegularityTools.objects.get(name = 'اذن')
    Create_List = []
    pattern_keyword_1 = 'اذن'
    regulator = Regulator.objects.get(name = 'ولی فقیه')
    regulator_name = regulator.name
    
    pattern = pattern_keyword_1 + ' ' + regulator_name

    ezn_paragraphs = DocumentParagraphs.objects.filter(text__icontains = pattern,
    document_id__in = documentList)

    for paragraph in ezn_paragraphs:
        doc_regulator =  DocumentRegulator(document_id = paragraph.document_id,regulator_id = regulator ,tool_id = tool, paragraph_id = paragraph)
        Create_List.append(doc_regulator)


    DocumentRegulator.objects.bulk_create(Create_List)   
    print('Ezn tool added.')

    # ----------------------------------------------------------------------------
    # Tool = Other tools except (مجوز و اذن)
    Create_List = []
    others_tools = RegularityTools.objects.exclude(name__in = ['مجوز', 'اذن'])
  
    other_tools_name_list = [(' ' + tool.name + ' ') for tool in others_tools]

    other_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in other_tools_name_list)),
    document_id__in = documentList)

    for paragraph in other_paragraphs:
        paragraph_text = paragraph.text
        for tool in others_tools:
            if (' ' + tool.name + ' ') in paragraph_text:
                doc_regulator =  DocumentRegulator(document_id = paragraph.document_id ,tool_id = tool, paragraph_id = paragraph)
                Create_List.append(doc_regulator)

        if Create_List.__len__() > batch_size:
            DocumentRegulator.objects.bulk_create(Create_List)
            Create_List = []

    DocumentRegulator.objects.bulk_create(Create_List)


    print('Other tools added.')

    print('Regulators completed.')