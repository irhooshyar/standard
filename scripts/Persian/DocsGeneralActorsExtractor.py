import operator
import json
from functools import reduce
from os import name
from pickle import FALSE
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
    # سـازمان
    # دبیر خانه
    # کار گروه
    # postfix_keywords = ['مورداشاره','مذکور','یادشده']

    # ---------------- Motevalian & Salahiat ---------------------------

    print('General actors started:')

    DocumentActor.objects.filter(document_id__country_id = Country,
            ref_to_general_definition = True).delete()

    DocumentActor.objects.filter(document_id__country_id = Country,
            ref_to_paragraph = True).delete()

    documentList = Document.objects.filter(country_id=Country)


    actor_roles = {
        'متولی اجرا':[],
        'دارای صلاحیت اختیاری':[]
    }
    
    actor_roles['متولی اجرا'] = ['مکلف است','مکلف به','موظف است','موظف به']
    
    actor_roles['دارای صلاحیت اختیاری'] = ActorType.objects.get(
        name = 'دارای صلاحیت اختیاری').pattern_keywords.split('/')

    def_pattern_keywords = ['نامیده','خوانده می‌شود']
        
    Create_List = []
    batch_size = 10000

  

    for role_name,role_keywords in actor_roles.items():

        start_t = time.time()
        Create_List = []

        actor_role_obj = ActorType.objects.get(name = role_name)


        general_actor_patterns = []

        documentList = Document.objects.filter(country_id=Country)

        category_list = ActorCategory.objects.all().exclude(
            name = 'سایر').exclude(name = 'اشخاص').exclude(name = 'کنشگران جمعی')

    
        for category in category_list:
            category_name = category.name
            

            for pattern_kw in role_keywords:
                actor_pattern = category.name + ' ' + pattern_kw
                general_actor_patterns.append(actor_pattern)

            general_actors_paragraphs = DocumentParagraphs.objects.filter(
                reduce(operator.or_, (Q(text__icontains = pattern) for pattern in general_actor_patterns)),
            document_id__in = documentList)

            for paragraph in general_actors_paragraphs:

                try: # extract from General Definition
                    general_def_obj = DocumentGeneralDefinition.objects.get(
                        document_id = paragraph.document_id,
                        keyword = category_name)

                    ref_actor = general_def_obj.text


                    ref_actor = ref_actor.strip()

                    if ref_actor[-1] == '.':
                        ref_actor = ref_actor[:-1]

                    ref_actor = ref_actor.replace(' جمهوری اسلامی ایران','').replace(' ایران','').replace(' کشور','')

                    res_count = Actor.objects.filter(actor_category_id = category,
                        forms__icontains = ref_actor).count()
                    
                    if res_count == 0:
                        pass

                    else:
                        pass

                    actor_obj = Actor.objects.get(
                        actor_category_id = category,forms__icontains = ref_actor)


                    doc_actor_obj = DocumentActor(
                        document_id = paragraph.document_id,
                        actor_id = actor_obj,
                        actor_type_id = actor_role_obj,
                        paragraph_id = paragraph,
                        current_actor_form = category_name,
                        ref_to_general_definition = True,
                        general_definition_id = general_def_obj
                    )
                    Create_List.append(doc_actor_obj)

                except:
                    # extract from paragraph
                    
                    category_forms = [
                        category_name,
                        '“' + category_name + '”',
                        '"' + category_name + '"',
                        '«' + category_name + '»'
                        '(' + category_name + ')',
                    ]

                    category_paterns = []

                    for category_form in category_forms:
                        for def_kw in def_pattern_keywords:
                            category_paterns.append(category_form + '‌' + def_kw)
                            category_paterns.append(category_form + ' ' + def_kw)

                    res_paragraph = DocumentParagraphs.objects.filter(
                        reduce(operator.or_, (Q(text__icontains = pattern) for pattern in category_paterns)),
                            document_id = paragraph.document_id).order_by('number').first()
                    
                    # print(len(res_paragraph))
                    
                    if res_paragraph != None:
                        paragraph_text = res_paragraph.text
                        actor_obj = get_actor_in_text(paragraph_text,category_name,def_pattern_keywords)

                        if actor_obj != None:
                                # print(actor_obj.name)
                                doc_actor_obj = DocumentActor(
                                document_id = paragraph.document_id,
                                actor_id = actor_obj,
                                actor_type_id = actor_role_obj,
                                paragraph_id = paragraph,
                                current_actor_form = category_name,
                                ref_to_paragraph = True,
                                ref_paragraph_id = res_paragraph
                                
                            )
                                Create_List.append(doc_actor_obj)
                                # print(paragraph.document_id.name)


            general_actor_patterns = []

            if Create_List.__len__() > batch_size:
                DocumentActor.objects.bulk_create(Create_List)
                Create_List = []
                
        DocumentActor.objects.bulk_create(Create_List)

        end_t = time.time()

        if role_name == 'متولی اجرا':
            print('Motevalian added (' + str(end_t - start_t) + ').')
        else:
            print('Salahiat added (' + str(end_t - start_t) + ').')

    update_Document_Fields(Country)
# ------------------------------ Save to files ---------------------------------------



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


def get_actor_in_text(paragraph_text,category_name,def_pattern_keywords):
    end_index = len(paragraph_text)

    for kw in def_pattern_keywords:
        if kw in paragraph_text:
            end_index = paragraph_text.find(kw)
            break
    

    sub_string = paragraph_text[:end_index]

    category_actors = Actor.objects.filter(actor_category_id__name = category_name)

    for actor in category_actors:
        actor_forms = actor.forms.split('/')

        if any(form in sub_string for form in actor_forms):
            return actor    

    return None




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



# Un-used..temporary
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
