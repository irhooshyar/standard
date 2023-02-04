import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country, DocumentActor
from doc.models import  Document
from doc.models import ActorType,Actor,ActorCategory,ActorSupervisor
from doc.models import DocumentParagraphs,DocumentGeneralDefinition
from datetime import datetime
import math
from itertools import chain
import time
import threading
from difflib import SequenceMatcher


def Docs_Text_Extractor(documents_list, Docs_Text_Dict):
    for document in documents_list:
        document_id = document.id
        document_paragraph_list = DocumentParagraphs.objects.filter(document_id=document).values("document_id", "text", "id").order_by("number")
        document_text = {}
        for paragraph in document_paragraph_list:
            document_text[paragraph["id"]] = paragraph["text"]
        Docs_Text_Dict[document_id] = document_text


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
    documentList = Document.objects.filter(country_id=Country)
    # DocumentActor.objects.filter(document_id__country_id = Country).delete()
    # ActorSupervisor.objects.filter(document_id__country_id = Country).delete()

    # ----------  Documents-Actors to DB  ---------------------
    # actorsList = Actor.objects.all()
    # actorsDict = {}
    # for actor in actorsList:
    #     actorsDict[actor.name] = {
    #         'id' : actor.id,
    #         'forms': actor.forms.split('/')
    #     }

    # Ejaze_Salahiat(documentList, actorsList, actorsDict)
    # Base_Motevali_Insert(documentList, actorsList, actorsDict)
    # Eghdam_Motevali_Insert(documentList,actorsList, actorsDict)
    # Salahiat_Insert(documentList, actorsList, actorsDict)
    # Hamkar_Insert(documentList, actorsList, actorsDict)
    # Supervisors_Insert(documentList, actorsList, actorsDict)
    update_Document_Fields(Country)


def Base_Motevali_Insert(documentList,actorsList,actorsDict):
    start_t = time.time()
    print('Base-Motevali started.')
    motevalianPatternKeywordsList = []

    motevalianPatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'motevalianPatternKeywords.txt'))

    # motevalian pattern keywords
    with open(motevalianPatternKeywordsFile, encoding="utf-8") as f:
        
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            motevalianPatternKeywordsList.append(line)

    f.close()

    # --------------------------------------------------------
    
    actor_type_name = 'متولی اجرا'
    actor_type_id = ActorType.objects.get(name=actor_type_name)

    all_motevalianPatternKeywords = actor_type_id.pattern_keywords.split('/')

    plural_motevali_pattern_keywords = ['مکلفند','مکلف‌اند','موظفند','موظف‌اند']
    exeption_word = 'به استثنای'
    actor_categories = ActorCategory.objects.exclude(name = 'سایر').values('name').distinct()
    category_name_list = []
    for category in actor_categories:
        category_name_list.append(category['name'])
    
    exeption_patterns = [(exeption_word + ' ' + category_name) for category_name in category_name_list]


    motevali_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in motevalianPatternKeywordsList)),
    document_id__in = documentList)

    motevali_paragraphs_dict = {}
    for para_obj in motevali_paragraphs:
        motevali_paragraphs_dict[para_obj.id] = {
        'doc_id':para_obj.document_id.id,
        'text':para_obj.text}

    Thread_Count = config.Thread_Count
    motevali_paragraphs_dict_slices = Slice_Dict(motevali_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in motevali_paragraphs_dict_slices:
        thread = threading.Thread(target=Base_Motevali_Extractor, args=(S,motevalianPatternKeywordsList,actor_type_id,
        actorsList,actorsDict,Result_Create_List,thread_number,plural_motevali_pattern_keywords,exeption_patterns))
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
        DocumentActor.objects.bulk_create(sub_list)
    # ----------------------------------------
    end_t = time.time()
    print('Base-Motevalian added (' + str(end_t - start_t) + ').')
   
def Base_Motevali_Extractor(motevali_paragraphs_dict,motevalianPatternKeywordsList,\
    actor_type_id,actorsList,actorsDict,Result_Create_List,thread_number,\
    plural_motevali_pattern_keywords,exeption_patterns):
    # --------------------------------------------------------
    Create_List = []

    for para_id,para_info in motevali_paragraphs_dict.items():

        paragraph_text =  para_info['text']
        
        for pattern_keyword in motevalianPatternKeywordsList:
            
            for actor_id in actorsList:

                acotr_forms_list = actorsDict[actor_id.name]['forms']

                for actor_form in acotr_forms_list:

                        forms =  [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران', actor_form + ' کشور',
                        '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')', '(' + actor_form + ' ایران' + ')', '(' +actor_form + ' کشور' + ')']
                        
                        forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )', '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']

                        motevali_patterns = [(form + ' ' + pattern_keyword) for form in forms]

                        if any(m_pattern in paragraph_text for m_pattern in motevali_patterns):

                            if not (pattern_keyword in plural_motevali_pattern_keywords \
                                and any(exeption_form in paragraph_text for exeption_form in exeption_patterns)):
                             
                                doc_actor = DocumentActor(document_id_id = para_info['doc_id'],actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id_id= para_id,
                                    current_actor_form = actor_form)
                                    
                                Create_List.append(doc_actor)  

    Result_Create_List[thread_number] = Create_List


def Eghdam_Motevali_Insert(documentList,actorsList,actorsDict):
    start_t = time.time()
    print('Eghdam-Motevali started.')

    motevalianPatternKeywordsList = []

    motevalianPatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'motevalianPatternKeywords.txt'))

    # motevalian pattern keywords
    with open(motevalianPatternKeywordsFile, encoding="utf-8") as f:
        
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            motevalianPatternKeywordsList.append(line)

    f.close()

    # --------------------------------------------------------
    
    actor_type_name = 'متولی اجرا'
    actor_type_id = ActorType.objects.get(name=actor_type_name)

    all_motevalianPatternKeywords = actor_type_id.pattern_keywords.split('/')

    eghdam_keywords = ['اقدام کند','اقدام‌کند','اقدام نماید','اقدام‌نماید']
    non_eghdam_keywords = list(set(
        set(all_motevalianPatternKeywords) - set(eghdam_keywords)
    ))
    motevali_paragraphs2 = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in eghdam_keywords)),
    document_id__in = documentList)

    motevali_paragraphs_dict = {}
    for para_obj in motevali_paragraphs2:
        motevali_paragraphs_dict[para_obj.id] = {
        'doc_id':para_obj.document_id.id,
        'text':para_obj.text}

    Thread_Count = config.Thread_Count
    motevali_paragraphs_dict_slices = Slice_Dict(motevali_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in motevali_paragraphs_dict_slices:
        thread = threading.Thread(target=Eghdam_Motevali_Extractor, args=(S,eghdam_keywords,non_eghdam_keywords,\
                                actor_type_id,actorsList,actorsDict,Result_Create_List,thread_number))
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
        DocumentActor.objects.bulk_create(sub_list)
    # ----------------------------------------
    end_t = time.time()
    print('Eghdam-Motevalian added (' + str(end_t - start_t) + ').')
   
def Eghdam_Motevali_Extractor(motevali_paragraphs_dict,eghdam_keywords,non_eghdam_keywords,\
    actor_type_id,actorsList,actorsDict,Result_Create_List,thread_number):
    # --------------------------------------------------------
    Create_List = []

    for para_id,para_info in motevali_paragraphs_dict.items():

        paragraph_text =  para_info['text']
        sentences = paragraph_text.split('.')                  
        for sentence in sentences:
            if any(e_keyword in sentence for e_keyword in eghdam_keywords)  and  all(non_eghdam not in sentence[0:40] for non_eghdam in non_eghdam_keywords):
                
                for actor_id in actorsList:

                    acotr_forms_list = actorsDict[actor_id.name]['forms']

                    for actor_form in acotr_forms_list:

                        forms =  [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران', actor_form + ' کشور',
                        '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')', '(' + actor_form + ' ایران' + ')', '(' +actor_form + ' کشور' + ')']
                        
                        forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )', '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']


                        if any((a_form + ' ') in sentence[0:40] for a_form in forms):
                            doc_actor = DocumentActor(document_id_id=para_info['doc_id'], actor_id=actor_id,
                                actor_type_id=actor_type_id, paragraph_id_id=para_id,
                                current_actor_form=actor_form)

                            Create_List.append(doc_actor)           

    Result_Create_List[thread_number] = Create_List



def Salahiat_Insert(documentList,actorsList,actorsDict):
    start_t = time.time()    
    print('Salahiat started.')

    actor_type_name = 'دارای صلاحیت اختیاری'
    actor_type_id = ActorType.objects.get(name=actor_type_name)

    salahiatPatternKeywordsList = []

    salahiatPatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'salahiatPatternKeywords.txt'))

    # salahiat pattern keywords
    with open(salahiatPatternKeywordsFile, encoding="utf-8") as f:
        
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            salahiatPatternKeywordsList.append(line)

    f.close()

    salahiat_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in salahiatPatternKeywordsList)),
    document_id__in = documentList)

    salahiat_paragraphs_dict = {}
    for para_obj in salahiat_paragraphs:
        salahiat_paragraphs_dict[para_obj.id] = {
        'doc_id':para_obj.document_id.id,
        'text':para_obj.text}

    Thread_Count = config.Thread_Count
    salahiat_paragraphs_dict_slices = Slice_Dict(salahiat_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in salahiat_paragraphs_dict_slices:
        thread = threading.Thread(target=Salahiat_Extractor, args=(S,salahiatPatternKeywordsList,\
                            actor_type_id,actorsList,actorsDict,Result_Create_List,thread_number))
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
        DocumentActor.objects.bulk_create(sub_list)
    # ----------------------------------------
    end_t = time.time()
    print('Salahiat added (' + str(end_t - start_t) + ').')
   
def Salahiat_Extractor(salahiat_paragraphs_dict,salahiatPatternKeywordsList,\
    actor_type_id,actorsList,actorsDict,Result_Create_List,thread_number):
    # --------------------------------------------------------
    Create_List = []

    for para_id,para_info in salahiat_paragraphs_dict.items():

        paragraph_text =  para_info['text']
        
        for pattern_keyword in salahiatPatternKeywordsList:
            
            for actor_id in actorsList:

                acotr_forms_list = actorsDict[actor_id.name]['forms']

                for actor_form in acotr_forms_list:


                        forms =  [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران', actor_form + ' کشور',
                        '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')', '(' + actor_form + ' ایران' + ')', '(' +actor_form + ' کشور' + ')']
                        
                        forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )', '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']


                        salahiat_patterns = [(form + ' ' + pattern_keyword) for form in forms]

                        if any(m_pattern in paragraph_text for m_pattern in salahiat_patterns):
                            doc_actor = DocumentActor(document_id_id = para_info['doc_id'],actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id_id = para_id,
                                current_actor_form = actor_form)
                                
                            Create_List.append(doc_actor)  

    Result_Create_List[thread_number] = Create_List

def Ejaze_Salahiat(documentList,actorsList,actorsDict):
    start_t = time.time()
    print('Ejaze Salahiat started.')

    actor_type_name = 'دارای صلاحیت اختیاری'
    actor_type_id = ActorType.objects.get(name=actor_type_name)

    pattern_1 = 'اجازه داده می‌شود'
    pattern_2 = 'اجازه داده می شود'
    pattern_3 = 'اجازه داده  میشود'

    salahiatPatternKeywordsList = [pattern_1, pattern_2, pattern_3]
    stopWordPatternKeyword = 'به'

    ejaze_salahiat_paragraphs = DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains=kw) for kw in salahiatPatternKeywordsList)),
        document_id__in=documentList)

    salahiat_paragraphs_dict = {}
    for para_obj in ejaze_salahiat_paragraphs:
        salahiat_paragraphs_dict[para_obj.id] = {
            'doc_id': para_obj.document_id.id,
            'text': para_obj.text}

    Create_List = []

    for para_id, para_info in salahiat_paragraphs_dict.items():

        paragraph_text = para_info['text']

        for pattern_keyword in salahiatPatternKeywordsList:

            for actor_id in actorsList:

                acotr_forms_list = actorsDict[actor_id.name]['forms']

                for actor_form in acotr_forms_list:

                    forms = [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران',
                             actor_form + ' کشور',
                             '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')',
                             '(' + actor_form + ' ایران' + ')', '(' + actor_form + ' کشور' + ')']

                    forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )',
                              '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']

                    salahiat_patterns = [stopWordPatternKeyword + ' ' + form + ' ' + pattern_keyword for form in forms]

                    if any(m_pattern in paragraph_text for m_pattern in salahiat_patterns):
                        doc_actor = DocumentActor(document_id_id=para_info['doc_id'], actor_id=actor_id,
                                                  actor_type_id=actor_type_id, paragraph_id_id=para_id,
                                                  current_actor_form=actor_form)

                        Create_List.append(doc_actor)

    DocumentActor.objects.bulk_create(Create_List)
    end_t = time.time()
    print('Salahiat added (' + str(end_t - start_t) + ').')




def Hamkar_Insert(documentList,actorsList,actorsDict):
    start_t = time.time()
    print('Hamkar started.')


    hamkaranPatternKeywordsList = []

    hamkaranPatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'hamkaranPatternKeywords.txt'))


    # hamkaran pattern keywords
    with open(hamkaranPatternKeywordsFile, encoding="utf-8") as f:
        
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            hamkaranPatternKeywordsList.append(line)

    f.close()

 
    hamkaran_punctuations = ['،', ')', ':']
    window_length = 100

    actor_type_name = 'همکار'
    actor_type_id = ActorType.objects.get(name=actor_type_name)


    hamkaran_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in hamkaranPatternKeywordsList)),
    document_id__in = documentList)


    hamkaran_paragraphs_dict = {}
    for para_obj in hamkaran_paragraphs:
        hamkaran_paragraphs_dict[para_obj.id] = {
        'doc_id':para_obj.document_id.id,
        'text':para_obj.text}

    Thread_Count = config.Thread_Count
    hamkaran_paragraphs_dict_slices = Slice_Dict(hamkaran_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in hamkaran_paragraphs_dict_slices:
        thread = threading.Thread(target=Hamkar_Extractor, args=(S,hamkaranPatternKeywordsList,\
                        actor_type_id,actorsList,actorsDict,window_length,hamkaran_punctuations\
                        ,Result_Create_List,thread_number))

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
        DocumentActor.objects.bulk_create(sub_list)
    # ----------------------------------------
    end_t = time.time()
    print('Hamkar added (' + str(end_t - start_t) + ').')

def Hamkar_Extractor(hamkar_paragraphs_dict,hamkaranPatternKeywordsList,\
    actor_type_id,actorsList,actorsDict,window_length,hamkaran_punctuations\
        ,Result_Create_List,thread_number):

    Create_List = []

    temp = 1
    for para_id,para_info in hamkar_paragraphs_dict.items():

        paragraph_text = para_info['text']

        for pattern_keyword in hamkaranPatternKeywordsList:

            indices = [m.start() for m in re.finditer(pattern_keyword, paragraph_text )]
                
            for index in indices:
                start_index = index + len(pattern_keyword)
                end_index = (start_index + window_length)
                sub_string = paragraph_text[start_index:end_index]
                    
                for actor_id in actorsList:

                    acotr_forms_list = actorsDict[actor_id.name]['forms']
                    
                    for actor_form in acotr_forms_list:
                            actor_forms = [
                                (' ' + actor_form + ' '),
                                ('(' + actor_form + ')'),

                                (' ' + actor_form + ' جمهوری اسلامی ایران' + ' '),
                                ('(' + actor_form + ' جمهوری اسلامی ایران' + ')'),

                                (' ' + actor_form + ' ایران' + ' '),
                                ('(' + actor_form + ' ایران' + ')'),

                                (' ' + actor_form + ' کشور' + ' '),
                                ('(' + actor_form + ' کشور' + ')')
                            ]

                            if any(ac_form in sub_string for ac_form in actor_forms):
                               
                                doc_actor = DocumentActor(document_id_id =para_info['doc_id'],actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id_id = para_id,
                                current_actor_form = actor_form)

                                Create_List.append(doc_actor)

                            for symbol in hamkaran_punctuations:


                                actor_forms2 = [
                                (' ' + actor_form + symbol),

                                (' ' + actor_form + ' جمهوری اسلامی ایران' + symbol),

                                (' ' + actor_form + ' ایران' + symbol),

                                (' ' + actor_form + ' کشور' + symbol)
                                ]

                                if any(ac_form in sub_string for ac_form in actor_forms2):
                                   
                                    doc_actor = DocumentActor(document_id_id = para_info['doc_id'],actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id_id = para_id,
                                    current_actor_form = actor_form)

                                    Create_List.append(doc_actor)

                            actor_without_affix = actor_form.replace('وزارت ', '').replace('سازمان ', '')

                            if (actor_without_affix != 'اطلاعات' and actor_without_affix != 'فناوری اطلاعات' and actor_without_affix != 'کشور' and  actor_form not in sub_string ):
                                    

                                actor_forms3 = [
                                (' ' + actor_without_affix + ' '),
                                ('(' + actor_without_affix + ')'),

                                (' ' + actor_without_affix + ' جمهوری اسلامی ایران' + ' '),
                                ('(' + actor_without_affix + ' جمهوری اسلامی ایران' + ')'),

                                (' ' + actor_without_affix + ' ایران' + ' '),
                                ('(' + actor_without_affix + ' ایران' + ')'),

                                (' ' + actor_without_affix + ' کشور' + ' '),
                                ('(' + actor_without_affix + ' کشور' + ')')
                                ]

                                if any(ac_form in sub_string for ac_form in actor_forms3):
                                  
                                    doc_actor = DocumentActor(document_id_id = para_info['doc_id'],actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id_id = para_id,
                                    current_actor_form = actor_form)

                                    Create_List.append(doc_actor)

                                for symbol in hamkaran_punctuations:

                                    actor_forms4 = [
                                    (' ' + actor_without_affix + symbol),

                                    (' ' + actor_without_affix + ' جمهوری اسلامی ایران' + symbol),

                                    (' ' + actor_without_affix + ' ایران' + symbol),

                                    (' ' + actor_without_affix + ' کشور' + symbol)
                                    ]

                                    if any(ac_form in sub_string for ac_form in actor_forms4):
                                       
                                        doc_actor = DocumentActor(document_id_id = para_info['doc_id'],actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id_id = para_id,
                                        current_actor_form = actor_form)

                                        Create_List.append(doc_actor)

            
    Result_Create_List[thread_number] = Create_List


def Supervisors_Insert(documentList,actorsList,actorsDict):
    start_t = time.time()
    print('Supervisors started.')

    motevalianPatternKeywordsList = []

    motevalianPatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'motevalianPatternKeywords.txt'))

    # motevalian pattern keywords
    with open(motevalianPatternKeywordsFile, encoding="utf-8") as f:
        
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            motevalianPatternKeywordsList.append(line)

    f.close()


    window_length = 83
    actor_type_name = 'متولی اجرا'
    actor_type_id = ActorType.objects.get(name=actor_type_name)

    supervisor_keywords = ['اعلام','ارائه','اقدام']
    supervisor_verbs  = [
    'کند','کنند','نماید','نمایند','دهد','دهند'
    ,'شود','می شود','می‌شود','میشود'
    ]

    supervisor_patterns = []

    for sup_kw in supervisor_keywords:
        for sup_vb in supervisor_verbs:
            pt_1 = (sup_kw + ' ' + sup_vb)
            pt_2 = (sup_kw + '‌' + sup_vb)
        
            supervisor_patterns.append(pt_1)
            supervisor_patterns.append(pt_2)

    
    motevalin_paragraphs = DocumentActor.objects.filter(
    reduce(operator.or_, (Q(paragraph_id__text__icontains = kw) for kw in supervisor_patterns)),
    document_id__in = documentList,
    actor_type_id = actor_type_id)

    actor_categories = ActorCategory.objects.exclude(name = 'سایر').exclude(name = 'اشخاص').values('name').distinct()
    category_name_list = []


    for category in actor_categories:
        category_name_list.append(category['name'])


    motevali_paragraphs_dict = {}
    for res in motevalin_paragraphs:
        motevali_paragraphs_dict[res.id] = {
        'document_id':res.document_id.id,
        'paragraph_id':res.paragraph_id.id,
        'paragraph_text':res.paragraph_id.text,
        'source_actor_id' : res.actor_id.id,
        'soucre_current_form' : res.current_actor_form
        }

    Thread_Count = config.Thread_Count
    motevali_paragraphs_dict_slices = Slice_Dict(motevali_paragraphs_dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count
   

    thread_obj = []
    thread_number = 0
    for S in motevali_paragraphs_dict_slices:
        thread = threading.Thread(target=Supervisors_Extractor, args=(S,motevalianPatternKeywordsList,\
        category_name_list,window_length,actorsList,actorsDict,Result_Create_List,thread_number))
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
        ActorSupervisor.objects.bulk_create(sub_list)
    # ----------------------------------------
    end_t = time.time()
    print('Supervisors added (' + str(end_t - start_t) + ').')

def Supervisors_Extractor(motevali_paragraphs_dict,motevalianPatternKeywordsList,\
    category_name_list,window_length,actorsList,actorsDict,Result_Create_List,thread_number):

    Create_List = []
    unique_paragraphs_id = []
    temp = 1
    for row_id,row_info in motevali_paragraphs_dict.items():

        # print(temp/motevali_paragraphs_dict.keys().__len__())
        # temp +=1

        paragraph_id = row_info['paragraph_id']
        paragraph_text = row_info['paragraph_text']
        document_id = row_info['document_id']
        source_actor_id =row_info['source_actor_id']
        soucre_current_form = row_info['soucre_current_form']

        if paragraph_id not in unique_paragraphs_id:
            unique_paragraphs_id.append(paragraph_id)
            
            sentences = paragraph_text.split('.')

            for sentence in sentences:
                for category_name in category_name_list:
                    supevisor_pattern = 'به ' + category_name
                    motevali_patterns = [(soucre_current_form + ' ' + pattern_keyword) for pattern_keyword in motevalianPatternKeywordsList]
                    motevali_patterns += [( '(' + soucre_current_form + ')' + ' ' + pattern_keyword) for pattern_keyword in motevalianPatternKeywordsList]
                    motevali_patterns += [( '( ' + soucre_current_form + ' )' + ' ' + pattern_keyword) for pattern_keyword in motevalianPatternKeywordsList]

                    for m_pattern in motevali_patterns:
                        m_pattern_index = sentence.find(m_pattern)
                        supevisor_pattern_index = sentence.find(supevisor_pattern)
                        if m_pattern in sentence and supevisor_pattern in sentence and supevisor_pattern_index > m_pattern_index:
                            supervisor_index = sentence.find(supevisor_pattern)
                            end_index = supervisor_index + window_length

                            substring = sentence[supervisor_index:end_index]
                            actor_supervisors_list =  getActorsInText(substring,actorsList)

                            for supervisor in actor_supervisors_list:
                                supervisor_name = supervisor[0]
                                supervisor_form = supervisor[1]
                                supervisor_actor_obj_id = actorsDict[supervisor_name]['id']
                                
                                if (supervisor_form != soucre_current_form):
                                    
                                    actor_supervisor_obj = ActorSupervisor(document_id_id = document_id,
                                    paragraph_id_id = paragraph_id,source_actor_id_id = source_actor_id,
                                    supervisor_actor_id_id =supervisor_actor_obj_id,
                                    source_actor_form = soucre_current_form,
                                    supervisor_actor_form = supervisor_form )

                                    Create_List.append(actor_supervisor_obj)
      

    Result_Create_List[thread_number] = Create_List



def update_Document_Fields(Country):
    batch_size = 10000
    start_t = time.time()
    print('Update document fields started.')
    doc_actors = DocumentActor.objects.filter(
        document_id__country_id = Country).values('document_id').distinct()


    doc_list = Document.objects.filter(id__in = doc_actors)

    for doc in doc_list:
        doc_id = doc.id
        doc_motevalian = GetDocumentActors_ByRole(doc_id,'متولی اجرا')
        doc_hamkaran = GetDocumentActors_ByRole(doc_id,'همکار')
        doc_salahiat = GetDocumentActors_ByRole(doc_id,'دارای صلاحیت اختیاری')

    
        doc.motevalian = doc_motevalian
        doc.hamkaran = doc_hamkaran
        doc.salahiat = doc_salahiat


        doc.actors_chart_data = Get_doc_ActorsChartData(doc_id)

    Document.objects.bulk_update(
        doc_list,['motevalian','hamkaran','salahiat','actors_chart_data'],batch_size) 

    end_t = time.time()        
    print('Document actor fields updated (' + str(end_t - start_t) + ').')

    # ---------- Update chart actors -------------------------------------

def Get_doc_ActorsChartData(doc_id):

    doc_motevalian = DocumentActor.objects.filter(
        document_id__id = doc_id,
        actor_type_id__name = 'متولی اجرا'
    ).annotate(name = F('actor_id__name')).values('name')


    doc_hamkaran = DocumentActor.objects.filter(
        document_id__id = doc_id,
        actor_type_id__name = 'همکار'
    ).annotate(name = F('actor_id__name')).values('name')


    doc_salahiat = DocumentActor.objects.filter(
        document_id__id = doc_id,
        actor_type_id__name = 'دارای صلاحیت اختیاری'
    ).annotate(name = F('actor_id__name')).values('name')


    # actos chart data
    actors_data = {}
    actors_chart_data = []

    if doc_motevalian != None:

        for motevali in doc_motevalian:
            motevali_name = motevali['name']

            if motevali_name not in actors_data:
                actors_data[motevali_name] = {
                    'motevali':1,
                    'hamkar':0,
                    'salahiat':0
                }
            else:
                actors_data[motevali_name]['motevali'] += 1


    if doc_hamkaran != None:

        for hamkar in doc_hamkaran:
            hamkar_name = hamkar['name']

            if hamkar_name not in actors_data:
                actors_data[hamkar_name] = {
                    'motevali':0,
                    'hamkar':1,
                    'salahiat':0
                }
            else:
                actors_data[hamkar_name]['hamkar'] += 1

    if doc_salahiat != None:
            
        for salahiat in doc_salahiat:
            salahiat_name = salahiat['name']

            if salahiat_name not in actors_data:
                actors_data[salahiat_name] = {
                    'motevali':0,
                    'hamkar':0,
                    'salahiat':1
                }
            else:
                actors_data[salahiat_name]['salahiat'] += 1


    for actor_name,role_info in actors_data.items():
            motevali_count = role_info['motevali']
            hamkar_count = role_info['hamkar']
            salahiat_count = role_info['salahiat']

            column = [actor_name,motevali_count,hamkar_count,salahiat_count]
            actors_chart_data.append(column)

    actors_chart_data_json = {"data":actors_chart_data}
    
    return actors_chart_data_json

def GetDocumentActors_ByRole(doc_id,actor_role):
    actor_list = []

    document_actors = DocumentActor.objects.filter(document_id_id=doc_id,
                                                   actor_type_id__name=actor_role).annotate(
        actor_name=F('actor_id__name')).values('actor_name').distinct()

    # fill actor list
    actor_list = [actor['actor_name'] for actor in document_actors]


    actor_list = ','.join(actor_list)
    
    if actor_list == '':
        return None
    else:
        return actor_list


def getActorsInText(substring,actorsList):
    detected_actors = []
    for actor in actorsList:
        actor_forms_list = actor.forms.split('/')
        for actor_form in actor_forms_list:
            if actor_form in substring and [actor.name,actor_form] not in detected_actors:
                detected_actors.append([actor.name,actor_form])

    return detected_actors



# UN-USED Methods
def get_most_similar_actor(ref_actor):
    actor_list = Actor.objects.all()
    max_sim = -1
    similar_actor = None

    for actor in actor_list:
        sim_value = similar(ref_actor,actor.name)
        if sim_value > max_sim:
            max_sim = sim_value
            similar_actor = actor.name
    
    return similar_actor

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
# similar("Apple","Appel")
