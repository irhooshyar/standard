import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re
from charset_normalizer import detect

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country, DocumentActor
from doc.models import  Document
from doc.models import ActorType,Actor,ActorCategory,ActorSupervisor
from doc.models import DocumentParagraphs,DocumentGeneralDefinition
from doc.models import CollectiveActor,DocumentCollectiveMembers
from datetime import datetime
import time
import re


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
    DocumentCollectiveMembers.objects.filter(document_id__country_id = Country).delete()

    inParagraph__collective_detection(Country)
    nextParagraph_collective_detection(Country)
    duties_collective_detection(Country)
    # -----------------------------------------------------------------------------------


def nextParagraph_collective_detection(Country):
    start_t = time.time()

    batch_size = 10000
    Create_List = []

    below_member_pattern_keywords = ['اعضاء زیر','اعضای زیر']
    next_paragraph_regex_pattern = r"(^((\d+)|الف|[ا-ی])\s?[ـ-])"
    in_paragraph_regex_pattern = r"(:\s?((\d+)|الف|[ا-ی])\s?[ـ-])"

    paragraphs_window = 15

    documentList = Document.objects.filter(country_id=Country)

    collective_actors = CollectiveActor.objects.all()


    for collective in collective_actors:
        collective_forms = collective.forms.split(',')

        collective_paragraphs = DocumentParagraphs.objects.filter(
            reduce(operator.or_, (Q(text__icontains=kw) for kw in collective_forms)),
            document_id__in = documentList)

        for pattern_kw in below_member_pattern_keywords:

            result_paragraphs = collective_paragraphs.filter(
            text__icontains = pattern_kw)   

            for para in result_paragraphs:
                
                members_json = {}
                member_paragraphs = []
                para_number = para.number
                doc_obj = para.document_id

                para_text = para.text
                matched_pattern_1 = re.search(in_paragraph_regex_pattern, para_text)
                if matched_pattern_1:
                    detected_member = (para_text[matched_pattern_1.end():]).strip().replace('.','')
                    
                    member_id = str(doc_obj.id) + '_' + str(para.id)
                    members_json[member_id] = {'name':detected_member,'form':detected_member}

                next_paragraphs = DocumentParagraphs.objects.filter(
                    document_id = para.document_id.id,
                    number__gt = para_number
                )

                next_paragraphs = next_paragraphs.filter(number__lt = (para_number + paragraphs_window))
                
                for next_para in next_paragraphs:
                    next_para_text = next_para.text
                    matched_pattern = re.search(next_paragraph_regex_pattern, next_para_text)
                    if matched_pattern:
                        detected_member = (next_para_text[matched_pattern.end():]).strip().replace('.','')
                        member_paragraphs.append(next_para_text)
                        member_id = str(doc_obj.id) + '_' + str(next_para.id)
                        # member_id = detected_member
                        members_json[member_id] = {'name':detected_member,'form':detected_member}
                    else:
                        break

                members_count = len(members_json.keys())
                member_paragraphs_text = '\n'.join(member_paragraphs)
                
                DocumentCollectiveMember_obj = DocumentCollectiveMembers(
                        document_id = doc_obj,
                        paragraph_id = para,
                        collective_actor_id = collective,
                        members = members_json,
                        members_count = members_count,
                        has_next_paragraph_members = True,
                        next_paragraphs = member_paragraphs_text
                        )
                Create_List.append(DocumentCollectiveMember_obj)

        if Create_List.__len__() > batch_size:
            DocumentCollectiveMembers.objects.bulk_create(Create_List)
            Create_List = []

    DocumentCollectiveMembers.objects.bulk_create(Create_List)

    end_t = time.time()
    print('Next-Paragraphs Collective actors added (' + str(end_t - start_t) + ')')

def inParagraph__collective_detection(Country):
    documentList = Document.objects.filter(country_id=Country)

    pattern_keyword_list = ['متشکل از','مرکب از','متشکل‌از','مرکب‌از']
    start_t = time.time()

    batch_size = 10000
    Create_List = []


    CollectiveActor_dict = {}
    collective_list = CollectiveActor.objects.all().distinct()

    for collective in collective_list:
        CollectiveActor_dict[collective.name] = collective.forms.split(',')

    for Collective in CollectiveActor_dict:

        collective_actor_obj = CollectiveActor.objects.get(name = Collective)
        collective_forms = CollectiveActor_dict[Collective]

        collective_patterns = []

        for clc_form in collective_forms:

            if clc_form == 'کمیته':
                collective_patterns = [(clc_form + ' ای' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]
                collective_patterns += [(clc_form + 'ای' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]
                collective_patterns += [(clc_form + '‌' + 'ای' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]
            else:
                collective_patterns += [(clc_form + 'ی' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]


        result_paragraphs = DocumentParagraphs.objects.filter(
            reduce(operator.or_, (Q(text__icontains=kw) for kw in collective_patterns)),
            document_id__in = documentList)
        

        for para_obj in result_paragraphs:
            paragraph_text = para_obj.text
            doc_obj = para_obj.document_id
            members_json = {}

            detected_members = getActorsInText(paragraph_text,collective_patterns)
            members_count = len(detected_members)
            for member in detected_members:
                member_id = int(member.id)
                member_name = member.name
                members_json[member_id] = {'name':member_name,'form':member_name}

            
            DocumentCollectiveMember_obj = DocumentCollectiveMembers(
                document_id = doc_obj,
                paragraph_id = para_obj,
                collective_actor_id = collective_actor_obj,
                members = members_json,
                members_count = members_count
                )
            Create_List.append(DocumentCollectiveMember_obj)

        if Create_List.__len__() > batch_size:
            DocumentCollectiveMembers.objects.bulk_create(Create_List)
            Create_List = []

    DocumentCollectiveMembers.objects.bulk_create(Create_List)

    end_t = time.time()
    print('In-Paragraph Collective actors added (' + str(end_t - start_t) + ')')

    # -------------------------------
    updata_member_form(Country,pattern_keyword_list)

def updata_member_form (Country,pattern_keyword_list):
    batch_size = 10000
    start_t = time.time()

    result = DocumentCollectiveMembers.objects.filter(document_id__country_id = Country)

    all_actors = Actor.objects.all()
    actors_dict = {}

    for actor in all_actors:
        actors_dict[actor.name] = actor.forms.split('/')

    for res in result:
        members_info = res.members
        
        for member_id in members_info:
            member_name = members_info[member_id]['name']
            actor_forms = actors_dict[member_name]
            paragraph_text = res.paragraph_id.text
            substring = ''

            for c_pattern in pattern_keyword_list:
                if c_pattern in paragraph_text:
                    start_index = paragraph_text.find(c_pattern)
                    cropped_text = paragraph_text[start_index:len(paragraph_text)+1]
                    end_index = cropped_text.find('.')
                    
                    
                    if end_index == -1:
                        end_index = len(cropped_text)

                    end_index += 1

                    # substring = cropped_text[start_index:end_index]
                    substring = cropped_text[0:end_index]
                    break
            
            for form in actor_forms:
                form_without_prefix = form.replace('وزارت ','').replace('سازمان ','').replace('کمیسیون ','')
                
                if form in substring:
                    res.members[member_id]['form'] = form
                    break
                elif form_without_prefix in substring:
                    res.members[member_id]['form'] = form_without_prefix
                    break

    DocumentCollectiveMembers.objects.bulk_update(
        result,['members'],batch_size) 

    end_t = time.time()        
    print('Member forms updated (' + str(end_t - start_t) + ').')


def getActorsInText(paragraph_text,collective_patterns):
    actors_list = Actor.objects.all().exclude(
        actor_category_id__name = 'کنشگران جمعی').exclude(name = 'قوه مجریه').values('id','name','forms')

    detected_actors = []

    for c_pattern in collective_patterns:
        if c_pattern in paragraph_text:

            start_index = paragraph_text.find(c_pattern)
            cropped_text = paragraph_text[start_index:len(paragraph_text)+1]
            end_index = cropped_text.find('.')
            
            
            if end_index == -1:
                end_index = len(cropped_text)

            end_index += 1

            # substring = cropped_text[start_index:end_index]
            substring = cropped_text[0:end_index]
            
            for actor in actors_list:
                actor_forms_list = actor['forms'].split('/')
                actor_form_patterns = []

                actor_form_patterns += actor_forms_list


                actor_form_patterns += [actor_form.replace('وزارت','').replace('سازمان','').replace('کمیسیون','')
                for actor_form in actor_forms_list if (actor['name'] != 'وزارت کشور') and (actor['name'] != 'وزارت اطلاعات')\
                    and (actor['name'] != 'سازمان فناوری اطلاعات')]

                # actor_form_patterns += [actor_form.replace('جمهوری اسلامی ایران','').replace('کشور','').replace('ایران','')
                
                # for actor_form in actor_forms_list if (actor['name'] != 'وزارت کشور' and actor['name'] != 'وزارت نیرو' \
                #     and actor['name'] != 'وزیر کشور' and actor['name'] != 'وزیر نیرو')]


                # actor_form_patterns += [actor_form.replace('وزارت','').replace('سازمان','').replace('جمهوری اسلامی ایران','').replace('کشور','').replace('ایران','')
                #  for actor_form in actor_forms_list if (actor['name'] != 'وزارت کشور')]


                if any(actor_form_pattern in substring for actor_form_pattern in actor_form_patterns):
                    if actor['name'] not in detected_actors:
                        detected_actors.append(actor['name'])

            for actor in detected_actors:
                vezarat = actor.replace('وزیر','وزارت')
                if 'وزیر' in actor and vezarat in detected_actors:
                    detected_actors.remove(vezarat)
            
            if 'ارتباطات و فناوری اطلاعات' in substring and 'سازمان فناوری اطلاعات ایران' in detected_actors:
                detected_actors.remove('سازمان فناوری اطلاعات ایران')
            
            if 'کمیسیون' not in substring and 'سازمان تنظیم مقررات و ارتباطات رادیویی' in detected_actors:
                detected_actors.remove('کمیسیون تنظیم مقررات و ارتباطات رادیویی')


            if 'سازمان' not in substring and 'کمیسیون برنامه و بودجه مجلس' in detected_actors :
                detected_actors.remove('سازمان برنامه و بودجه')

            if ('نیروهای' in substring or 'نیروی' in substring or 'نیرو‌های' in substring) \
                and 'وزارت نیرو' in detected_actors:
                detected_actors.remove('وزارت نیرو')


            if 'اتاق بازرگانی' in substring and 'وزارت بازرگانی' in detected_actors:
                detected_actors.remove('وزارت بازرگانی')
                detected_actors.append('اتاق بازرگانی، صنایع، معادن و کشاورزی')


            if ('اتاق­ بازرگانی، صنایع، معادن و کشاورزی ایران' in substring and 'وزارت بازرگانی' in detected_actors):
                detected_actors.remove('وزارت بازرگانی')
                detected_actors.append('اتاق بازرگانی، صنایع، معادن و کشاورزی')


    detected_actor_objects = []

    for actor_name in detected_actors:
        actor_obj = Actor.objects.get(name=actor_name)

        detected_actor_objects.append(actor_obj)


    return detected_actor_objects


def duties_collective_detection(Country):
    paragraphs_window = 15
    collectives = DocumentCollectiveMembers.objects.filter(document_id__country_id = Country)
    paragraphs_all = DocumentParagraphs.objects.filter(
        document_id__country_id=Country,
    )
    for collective in collectives:
        current_text = collective.paragraph_id.text + '\n'
        current_text += collective.next_paragraphs if collective.has_next_paragraph_members else ''
        paragraphs = paragraphs_all.filter(number__lt=(collective.paragraph_id.number + paragraphs_window),
                                           number__gte=collective.paragraph_id.number,
                                           document_id=collective.document_id.id,)

        current_text,duties = getDuties(paragraphs,current_text,collective.collective_actor_id.forms.split(','))
        if current_text != collective.paragraph_id.text + '\n':
            collective.next_paragraphs = current_text[len(collective.paragraph_id.text + '\n'):]
            collective.has_next_paragraph_members = True
        collective.obligation = duties
        collective.save()

def getDuties(paragraphs,current_text,collective_forms):
    found_paragraphs = []
    duties = ''
    # result = getDuties1('')
    # found_paragraphs_,duties_ = getDuties2(paragraphs)
    # found_paragraphs += found_paragraphs_
    duties += getDuties2(current_text,collective_forms)
    duties += getDuties4(current_text)
    duties += getDuties3(current_text,collective_forms)

    for found_paragraph in found_paragraphs:
        if found_paragraph.text not in current_text:
            current_text += found_paragraph.text
    return current_text,duties


def getDuties1(text:str):
    # pattern = 'برعهده'
    return ''


def getDuties3(text:str,collective_forms:list):
    pattern = 'به منظور'
    pattern_index = text.find(pattern)
    if pattern_index == -1:
        return ''
    form_indices = []
    for collective_form in collective_forms:
        index = text.find(collective_form,pattern_index)
        if index != -1:
            form_indices.append(index)
    if len(form_indices) == 0:
        return ''
    return text[pattern_index + len(pattern):min(form_indices)].replace('،','') + '\n'

def getDuties4(text: str):
    pattern_start = 'نسبت به'
    pattern_start_index = text.find(pattern_start)
    if pattern_start_index == -1:
        return ''
    pattern_end = 'اقدام'
    pattern_end_index = text.find(pattern_end,pattern_start_index)
    if pattern_end_index == -1:
        return ''
    return text[pattern_start_index + len(pattern_start):pattern_end_index] + '\n'


def getDuties2(text:str,collective_forms:list):
    patterns = [
        'موظف است',
        'مکلف است',
        'مکلف‌اند',
        'موظف‌اند',
        'موظفند',
        'مکلفند',
        'موظف به',
        'مکلف به',

        'مختار است',
        'اختیار دارد',
        'می‌تواند',
        'می تواند',
        'میتواند',
        'مجاز است'
    ]
    form_indices = []
    for collective_form in collective_forms:
        index = text.find(collective_form)
        if index != -1:
            form_indices.append(index)
    if len(form_indices) == 0:
        return ''
    collective_index = min(form_indices)
    for pattern in patterns:
        index = text.find(pattern,collective_index)
        if index != -1:
            return text[index + len(pattern):text.find('.',index)] + '\n'
    return ''

