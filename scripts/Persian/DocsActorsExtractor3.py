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
import time
from difflib import SequenceMatcher

def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)

    return text


def apply(folder_name, Country):
    batch_size = 1000
    documentList = Document.objects.filter(country_id=Country)
    DocumentActor.objects.filter(document_id__country_id = Country).delete()
    ActorSupervisor.objects.filter(document_id__country_id = Country).delete()

    # ----------  Documents-Actors to DB  ---------------------


    actorsList = Actor.objects.all()
    actorsDict = {}
    for actor in actorsList:
        actorsDict[actor.name] = actor.forms.split('/')

    Motevali_Insert(Country,documentList,actorsList,actorsDict,batch_size)
    Salahiat_Insert(Country,documentList,actorsList,actorsDict,batch_size)
    Hamkar_Insert(Country,documentList,actorsList,actorsDict,batch_size)
    Supervisors_Insert(Country,batch_size)
     
   
    # ----------------------------------------
    update_Document_Fields(Country)
   
   
   
def Motevali_Insert(Country,documentList,actorsList,actorsDict,batch_size):
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
    start_t = time.time()
    Create_List = []
    

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


    for paragraph in motevali_paragraphs:
        paragraph_text =  paragraph.text
        
        for pattern_keyword in motevalianPatternKeywordsList:
            
            for actor_id in actorsList:

                acotr_forms_list = actorsDict[actor_id.name]

                for actor_form in acotr_forms_list:

                        forms =  [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران', actor_form + ' کشور',
                        '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')', '(' + actor_form + ' ایران' + ')', '(' +actor_form + ' کشور' + ')']
                        
                        forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )', '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']

                        motevali_patterns = [(form + ' ' + pattern_keyword) for form in forms]

                        if any(m_pattern in paragraph_text for m_pattern in motevali_patterns):

                            if not (pattern_keyword in plural_motevali_pattern_keywords \
                                and any(exeption_form in paragraph_text for exeption_form in exeption_patterns)):
                             
                                doc_actor = DocumentActor(document_id = paragraph.document_id,actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id = paragraph,
                                    current_actor_form = actor_form)
                                    
                                Create_List.append(doc_actor)  

        if Create_List.__len__() > batch_size:
            DocumentActor.objects.bulk_create(Create_List)
            Create_List = []

    DocumentActor.objects.bulk_create(Create_List)

    # ************************************************************
    Create_List = []
    eghdam_keywords = ['اقدام کند','اقدام‌کند','اقدام نماید','اقدام‌نماید']
    non_eghdam_keywords = list(set(
        set(all_motevalianPatternKeywords) - set(eghdam_keywords)
    ))


    motevali_paragraphs2 = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in eghdam_keywords)),
    document_id__in = documentList)


    for paragraph in motevali_paragraphs2:
        paragraph_text =  paragraph.text
        sentences = paragraph.text.split('.')                  
        for sentence in sentences:
            if any(e_keyword in sentence for e_keyword in eghdam_keywords)  and  all(non_eghdam not in sentence[0:40] for non_eghdam in non_eghdam_keywords):
                
                for actor_id in actorsList:

                    acotr_forms_list = actorsDict[actor_id.name]

                    for actor_form in acotr_forms_list:

                        forms =  [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران', actor_form + ' کشور',
                        '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')', '(' + actor_form + ' ایران' + ')', '(' +actor_form + ' کشور' + ')']
                        
                        forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )', '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']


                        if any((a_form + ' ') in sentence[0:40] for a_form in forms):
                            doc_actor = DocumentActor(document_id=paragraph.document_id, actor_id=actor_id,
                                actor_type_id=actor_type_id, paragraph_id=paragraph,
                                current_actor_form=actor_form)

                            Create_List.append(doc_actor)           


        if Create_List.__len__() > batch_size:
            DocumentActor.objects.bulk_create(Create_List)
            Create_List = []

    DocumentActor.objects.bulk_create(Create_List)
    # ************************************************************


    end_t = time.time()
    print('Motevalian added (' + str(end_t - start_t) + ').')


def Salahiat_Insert(Country,documentList,actorsList,actorsDict,batch_size):

    start_t = time.time()    
    actor_type_name = 'دارای صلاحیت اختیاری'
    actor_type_id = ActorType.objects.get(name=actor_type_name)
    Create_List = []

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


    for paragraph in salahiat_paragraphs:
        paragraph_text =  paragraph.text
        
        for pattern_keyword in salahiatPatternKeywordsList:
            
            for actor_id in actorsList:

                acotr_forms_list = actorsDict[actor_id.name]

                for actor_form in acotr_forms_list:


                        forms =  [actor_form, actor_form + ' جمهوری اسلامی ایران', actor_form + ' ایران', actor_form + ' کشور',
                        '(' + actor_form + ')', '(' + actor_form + ' جمهوری اسلامی ایران' + ')', '(' + actor_form + ' ایران' + ')', '(' +actor_form + ' کشور' + ')']
                        
                        forms += ['( ' + actor_form + ' )', '( ' + actor_form + ' جمهوری اسلامی ایران' + ' )', '( ' + actor_form + ' ایران' + ' )', '( ' + actor_form + ' کشور' + ' )']


                        salahiat_patterns = [(form + ' ' + pattern_keyword) for form in forms]

                        if any(m_pattern in paragraph_text for m_pattern in salahiat_patterns):
                            doc_actor = DocumentActor(document_id = paragraph.document_id,actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id = paragraph,
                                current_actor_form = actor_form)
                                
                            Create_List.append(doc_actor)  

        if Create_List.__len__() > batch_size:
            DocumentActor.objects.bulk_create(Create_List)
            Create_List = []
            
    DocumentActor.objects.bulk_create(Create_List)
    end_t = time.time()        
    print('Salahiat added (' + str(end_t - start_t) + ').')


def Hamkar_Insert(Country,documentList,actorsList,actorsDict,batch_size):
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

    start_t = time.time()    
    Create_List = []

    actor_type_name = 'همکار'
    actor_type_id = ActorType.objects.get(name=actor_type_name)


    hamkaran_paragraphs = DocumentParagraphs.objects.filter(reduce(operator.or_, (Q(text__icontains = kw) for kw in hamkaranPatternKeywordsList)),
    document_id__in = documentList)


    for paragraph in hamkaran_paragraphs:
        paragraph_text = paragraph.text

        for pattern_keyword in hamkaranPatternKeywordsList:

            indices = [m.start() for m in re.finditer(pattern_keyword, paragraph_text )]
                
            for index in indices:
                start_index = index + len(pattern_keyword)
                end_index = (start_index + window_length)
                sub_string = paragraph_text[start_index:end_index]
                    
                for actor_id in actorsList:

                    acotr_forms_list = actorsDict[actor_id.name]
                    
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
                               
                                doc_actor = DocumentActor(document_id = paragraph.document_id,actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id = paragraph,
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
                                   
                                    doc_actor = DocumentActor(document_id = paragraph.document_id,actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id = paragraph,
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
                                  
                                    doc_actor = DocumentActor(document_id = paragraph.document_id,actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id = paragraph,
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
                                       
                                        doc_actor = DocumentActor(document_id = paragraph.document_id,actor_id = actor_id,actor_type_id = actor_type_id,paragraph_id = paragraph,
                                        current_actor_form = actor_form)

                                        Create_List.append(doc_actor)

        if Create_List.__len__() > batch_size:
            DocumentActor.objects.bulk_create(Create_List)
            Create_List = []
            
    DocumentActor.objects.bulk_create(Create_List)

    end_t = time.time()        
    print('Hamkaran added (' + str(end_t - start_t) + ').')


def Supervisors_Insert(Country,batch_size):

    start_t = time.time()

    motevalianPatternKeywordsList = []

    motevalianPatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'motevalianPatternKeywords.txt'))

    # motevalian pattern keywords
    with open(motevalianPatternKeywordsFile, encoding="utf-8") as f:
        
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            motevalianPatternKeywordsList.append(line)

    f.close()


    Create_List = []
    window_length = 83
    actor_type_name = 'متولی اجرا'
    actor_type_id = ActorType.objects.get(name=actor_type_name)

    motevalin_paragraphs = DocumentActor.objects.filter(document_id__country_id = Country,
    actor_type_id = actor_type_id)

    actor_categories = ActorCategory.objects.exclude(name = 'سایر').exclude(name = 'اشخاص').values('name').distinct()
    category_name_list = []

    unique_paragraphs_id = []

    for category in actor_categories:
        category_name_list.append(category['name'])

    for motevali_info in motevalin_paragraphs:
        paragraph_id = motevali_info.paragraph_id
        paragraph_text = motevali_info.paragraph_id.text
        document_id = motevali_info.document_id
        source_actor_id = motevali_info.actor_id
        soucre_current_form = motevali_info.current_actor_form

        if paragraph_id.id not in unique_paragraphs_id:
            unique_paragraphs_id.append(paragraph_id.id)
            
            sentences = paragraph_text.split('.')

            for sentence in sentences:
                for category_name in category_name_list:
                    supevisor_pattern = 'به ' + category_name
                    motevali_patterns = [(soucre_current_form + ' ' + pattern_keyword) for pattern_keyword in motevalianPatternKeywordsList]
                    motevali_patterns += [( '(' + soucre_current_form + ')' + ' ' + pattern_keyword) for pattern_keyword in motevalianPatternKeywordsList]
                    motevali_patterns += [( '( ' + soucre_current_form + ' )' + ' ' + pattern_keyword) for pattern_keyword in motevalianPatternKeywordsList]

                    for m_pattern in motevali_patterns:
                        
                        if m_pattern in sentence and supevisor_pattern in sentence:
                            supervisor_index = sentence.find(supevisor_pattern)
                            end_index = supervisor_index + window_length

                            substring = sentence[supervisor_index:end_index]
                            actor_supervisors_list =  getActorsInText(substring)

                            for supervisor in actor_supervisors_list:
                                supervisor_name = supervisor[0]
                                supervisor_form = supervisor[1]
                                supervisor_actor_obj = Actor.objects.get(name = supervisor_name)
                                
                                if (supervisor_form != soucre_current_form):
                                    
                                    actor_supervisor_obj = ActorSupervisor(document_id = document_id,
                                    paragraph_id = paragraph_id,source_actor_id = source_actor_id,
                                    supervisor_actor_id =supervisor_actor_obj,
                                    source_actor_form = soucre_current_form,
                                    supervisor_actor_form = supervisor_form )

                                    Create_List.append(actor_supervisor_obj)
      

        if Create_List.__len__() > batch_size:
            ActorSupervisor.objects.bulk_create(Create_List)
            Create_List = []
            
    ActorSupervisor.objects.bulk_create(Create_List)

    end_t = time.time()        
    print('Supervisors added (' + str(end_t - start_t) + ').')



def update_Document_Fields(Country):
    batch_size = 10000
    start_t = time.time()

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


def getActorsInText(substring):
    actors_list = Actor.objects.all().values('id','name','forms')
    detected_actors = []
    for actor in actors_list:
        actor_forms_list = actor['forms'].split('/')
        for actor_form in actor_forms_list:
            if actor_form in substring and [actor['name'],actor_form] not in detected_actors:
                detected_actors.append([actor['name'],actor_form])

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
