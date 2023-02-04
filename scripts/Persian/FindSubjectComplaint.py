import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path
import string
from doc.models import Country, Judgment, JudgmentJudge
from doc.models import  Document
from doc.models import DocumentParagraphs
from datetime import datetime
from abdal import es_config
import time
from elasticsearch import Elasticsearch
from scripts.Persian.Preprocessing import standardIndexName

es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)



def apply(folder_name, Country):
    find_subject_complaint(Country)
    find_judge(Country)

def find_subject_complaint(Country):
    doc_list = Judgment.objects.all()
    complaint_text =''

    for doc in doc_list:
        complaint_text =''
        doc_id = doc.document_id_id
        text = 'موضوع شکایت و خواسته:'
        
        Paragraphs = DocumentParagraphs.objects.filter(document_id_id=doc_id, text__icontains=text).values_list('text', flat=True)

        for para in Paragraphs:
            start_index = para.find(text) + len(text)
            stop_index = para.find('.' , start_index)
            complaint_text = para[start_index:stop_index].strip()

            if len(complaint_text) > 300:
                complaint_text = ' '.join(complaint_text.split(' ')[:10])

            break
        doc.subject_complaint = complaint_text

    Judgment.objects.bulk_update(doc_list,['subject_complaint']) 

judge_name_dict = {
    'حکمتعلی مظفری': 'حکمتعلی مظفری',
    'محمد مصدقی': 'محمد مصدقی',
    'محمدکاظم بهرامی': 'محمد کاظم بهرامی',
    'محمد کاظم بهرامی': 'محمد کاظم بهرامی',
    'رهبرپور': 'رهبرپور',
    'علی رازینی': 'علی رازینی',
    'قربانعلی دری نجف آبادی': 'قربانعلی دری نجف آبادی',
    'محمد رضا عباسی فردوسی': 'محمد رضا عباسی فردوسی',
    'مقدسی‎فرد': 'مقدسی فرد',
    'محمد رضا عباسی‌فرد': 'محمدرضا عباسی فرد',
    'مرتضی علی اشراقی': 'مرتضی علی اشراقی',
    'محمدجعفر منتظری': 'محمد جعفر منتظری',
    'محمد جعفر منتظری': 'محمد جعفر منتظری',
    'علی مبشری': 'علی مبشری',
    'مبشری': 'علی مبشری',
    'قدیانی': 'قدیانی',
    'رهبر پور': 'رهبرپور',
    'مقدسی‎ فرد': 'مقدسی فرد',
    'سیدابوالفضل موسوی تبریزی': 'سید ابوالفضل موسوی تبریزی',
    'سید ابوالفضل موسوی تبریزی': 'سید ابوالفضل موسوی تبریزی',
    'اسماعیل فردوسی‌پور': 'اسماعیل فردوسی پور',
    'اسماعیل فردوسی پور': 'اسماعیل فردوسی پور',
    'محمدرضا عباسی‌فرد': 'محمدرضا عباسی فرد',
    'محمدرضا عباسی فرد': 'محمدرضا عباسی فرد',
    'محمدعلی فیض': 'محمدعلی فیض',
    'محمد علی فیض': 'محمدعلی فیض',
    'غلامرضا رضوانی': 'غلامرضا رضوانی',
    'محمد امامی کاشانی': 'محمد امامی کاشانی'
}

def find_judge(Country):
    JudgmentJudgeObjects = JudgmentJudge.objects.all()
    JudgmentJudgeDict = {judge.name: judge for judge in JudgmentJudgeObjects}

    doc_list = Judgment.objects.filter(document_id__country_id=Country)
    judge_text = ''

    local_index = standardIndexName(Country,Judgment.__name__)

    for doc in doc_list:

        response = client.get(index=local_index, id=doc.document_id_id,
            _source_includes = ['document_id','name','attachment.content']
            )
        judge_text = response['_source']['attachment']['content']

        judge_paragraphs = judge_text.split('\n')

        pattern_all = ['رئیس هیأت عمومی دیوان عدالت اداری', 'رئیس هیات عمومی دیوان عدالت اداری','رییس هیات عمومی دیوان عدالت اداری', 'معاون هیأت عمومی دیوان عدالت اداری', 'معاون قضایی دیوان عدالت اداری','معاون قضائی دیوان عدالت اداری' , 'هیأت عمومی دیوان عدالت اداری','اداری']
        pattern_text = ['رئیس هیأت عمومی دیوان عدالت اداری', 'رئیس هیات عمومی دیوان عدالت اداری', 'رییس هیات عمومی دیوان عدالت اداری','معاون هیأت عمومی دیوان عدالت اداری', 'معاون قضایی دیوان عدالت اداری' , 'معاون قضائی دیوان عدالت اداری']
        pattern2 = 'هیأت عمومی دیوان عدالت اداری'
        index = -1
        index2 = -1
        judge_person = ''

        for para in judge_paragraphs:
            for pattern in pattern_text:
                if pattern == para.strip():
                    index = judge_paragraphs.index(para)
            if pattern2 == para.strip():
                    index2 = judge_paragraphs.index(para)

        if index != -1:
            for pattern in pattern_text:          
                if judge_paragraphs[index-1] == pattern:
                    if len(judge_paragraphs[index-2])<40:
                        judge_person = judge_paragraphs[index-2]
                
            if len(judge_paragraphs[index-1])<40:
                judge_person = judge_paragraphs[index-1]

            if index+1 < len(judge_paragraphs) and len(judge_paragraphs[index+1])<40:
                judge_person = judge_paragraphs[index+1]

        elif index2 != -1 and judge_person == '':
            if len(judge_paragraphs[index-1])<40:
                judge_person = judge_paragraphs[index-1]

            if index+1 < len(judge_paragraphs) and len(judge_paragraphs[index+1])<40:
                judge_person = judge_paragraphs[index+1]
        else:
            for pattern in pattern_text:
                if pattern in judge_paragraphs[-1] and judge_person == '':
                    start_index = judge_paragraphs[-1].find(pattern) + len(pattern)
                    if len(judge_paragraphs[-1][start_index:])<40:
                        judge_person = judge_paragraphs[-1][start_index:]

            if pattern2 in judge_paragraphs[-1] and judge_person == '':
                    start_index = judge_paragraphs[-1].find(pattern) + len(pattern)
                    if len(judge_paragraphs[-1][start_index:])<40:
                        judge_person = judge_paragraphs[-1][start_index:]

                    
        for pattern in pattern_all:
            if pattern in judge_person:
                judge_person = judge_person.replace(pattern,'').strip()

        judge_person = judge_person.translate(str.maketrans('', '', string.punctuation)).strip()

        black_list = ['اداری', 'بسم الله الرحمن الرحیم', 'مقدمه', 'عمومی دیوان عدالت اداری', 'رأی هیأت عمومی', 'دیوان عدالت اداری', 'مومی دیوان عدالت', 'ومی دیوان عدالت', 'رئیس هیات عمومی دیوان عدالت','عمومی دیوان عدالت', 'دیوان عدالت']
        if judge_person != '' and all(black_kw not in judge_person  for black_kw in black_list):
            judge_person = judge_person.replace('ـ','').replace('‌‌',' ').strip()
            judge_person = judge_name_dict.get(judge_person)
            doc.judge_name = JudgmentJudgeDict.get(judge_person)
        else:
            doc.judge_name = None

    Judgment.objects.bulk_update(doc_list,['judge_name']) 


