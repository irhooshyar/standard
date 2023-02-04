import operator
import re

from doc.models import Document, DocumentWords, DocumentParagraphs
from doc.models import CUBE_CollectiveActor_TableData, CollectiveActor,Actor
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time

from functools import reduce
from django.db.models import Q
import operator

from scripts.Persian import Preprocessing


def GetExistedKeywords_ByDocumentId(document_id, kw_list):
    result_keywords = []

    for kw in kw_list:

        kw_flag = DocumentParagraphs.objects.filter(
            document_id__id=document_id,
            text__icontains=kw['name']
        ).exists()

        if kw_flag and kw['name'] not in result_keywords:
            result_keywords.append(kw['name'])

    result_keywords = ','.join(result_keywords)

    return result_keywords


def apply(folder_name, Country, host_url):
    create_TableData_CUBE(Country, host_url)


def create_TableData_CUBE(Country, host_url):
    pattern_keyword_list = ['متشکل از','مرکب از','متشکل‌از','مرکب‌از']
    start_t = time.time()

    batch_size = 10000
    Create_List = []

    CUBE_CollectiveActor_TableData.objects.filter(country_id=Country).delete()

    CollectiveActor_list = []
    temp_list = CollectiveActor.objects.all().values('name')
    for item in temp_list:
        CollectiveActor_list.append(item['name'])


    for Collective in CollectiveActor_list:

        index = 1
        temp_id = 0
        result_list = []
        doc_list = DocumentParagraphs.objects.filter(document_id__country_id=Country)


        if Collective == 'همه':
            doc_list = doc_list.filter(
                reduce(operator.or_, (Q(text__icontains=kw['name']) for kw in temp_list))).values('document_id').distinct()

        else:
            collective_patterns = [(Collective + 'ی' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]
        
            if Collective == 'کمیته':
                collective_patterns = [(Collective + ' ای' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]
                collective_patterns += [(Collective + 'ای' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]
                collective_patterns += [(Collective + '‌' + 'ای' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]


            doc_list = doc_list.filter(reduce(operator.or_, (Q(text__icontains=kw) for kw in collective_patterns))).values('document_id').distinct()

        result_doc_list = Document.objects.filter(id__in=doc_list)

        for doc in result_doc_list:

            doc_id = doc.id
            doc_name = doc.name
            doc_link = 'http://'+host_url+'/information/?id=' + str(doc_id)
            doc_tag = '<a class="document_link" ' + 'target="to_blank" href="' + doc_link + '">' + doc_name + "</a>"

            doc_subject = doc.subject_name
            subject_weight = doc.subject_weight
            doc_level = doc.level_name if doc.level_name != None else 'نامشخص'

            approval_reference = doc.approval_reference_name if doc.approval_reference_name != None else 'نامشخص'

            approval_date = doc.approval_date if doc.approval_date != None else 'نامشخص'
            
            collective_members = ''
            member_count = 0

            if Collective == 'همه':
                collective_members = '-'
            else:
                collective_actor_name = [Collective]
                if (Collective not in ['هیئت','هیات']):
                    collective_members = GetCollectiveMembers(doc_id,collective_patterns)
                    member_count = len(collective_members)
                    collective_members = '<br>'.join(collective_members)


            function = "DetailFunction(" + str(doc_id) + ",'" + Collective + "')"
            detail_btn = '<button ' \
                         'type="button" ' \
                         'class="btn modal_btn" ' \
                         'data-bs-toggle="modal" ' \
                         'data-bs-target="#myModal" ' \
                         'onclick="' + function + '"' \
                                                  '>' + 'جزئیات' + '</button>'

            function = "GraphFunction(" + str(doc_id) + ")"
            graph_btn = '<button ' \
                         'type="button" ' \
                         'class="btn modal_btn" ' \
                         'data-bs-toggle="modal" ' \
                         'data-bs-target="#myGraph" ' \
                         'onclick="' + function + '"' \
                                                  '>' + 'گراف' + '</button>'

            json_value = {"id": index, 'document_id':doc_id,"document_subject": doc_subject, "document_name": doc_name,
                          "document_tag": doc_tag, "document_approval_reference": approval_reference,
                          "document_approval_date": approval_date, "document_subject_weight": subject_weight,
                          "document_level": doc_level, "document_collective_actor": collective_actor_name,
                          "collective_members": collective_members,
                          'member_count': member_count, "detail": detail_btn, "graph":graph_btn}

            result_list.append(json_value)
            index += 1

        table_data_json = {
            "data": result_list
        }


        cube_obj = CUBE_CollectiveActor_TableData(
            country_id=Country,
            CollectiveActor_name=Collective,
            table_data=table_data_json)

        Create_List.append(cube_obj)
        temp_id += 1

    CUBE_CollectiveActor_TableData.objects.bulk_create(Create_List)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ')')


def GetCollectiveMembers(doc_id,collective_patterns):
    collective_members = []
    


    res_paragraph = DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains=kw) for kw in collective_patterns)),
        document_id__id = doc_id,
        ).order_by('number').first()
    
    if res_paragraph != None:
        paragraph_text = res_paragraph.text
        detected_actors = getActorsInText(paragraph_text,collective_patterns)

        for actor in detected_actors:
            collective_members.append(actor)
                
    return collective_members


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
                for actor_form in actor_forms_list if (actor['name'] != 'وزارت کشور')]

                actor_form_patterns += [actor_form.replace('جمهوری اسلامی ایران','').replace('کشور','').replace('ایران','')
                for actor_form in actor_forms_list if (actor['name'] != 'وزارت کشور' and actor['name'] != 'وزارت نیرو' \
                    and actor['name'] != 'وزیر کشور' and actor['name'] != 'وزیر نیرو')]


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
                detected_actors.remove('سازمان برنامه و بودجه کشور')

            if ('نیروهای' in substring or 'نیروی' in substring) and 'وزارت نیرو' in detected_actors:
                detected_actors.remove('وزارت نیرو')


            if 'اتاق بازرگانی' in substring and 'وزارت بازرگانی' in detected_actors:
                detected_actors.remove('وزارت بازرگانی')
                detected_actors.append('اتاق­ بازرگانی، صنایع، معادن و کشاورزی ایران')


            if ('اتاق­ بازرگانی، صنایع، معادن و کشاورزی ایران' in substring and 'وزارت بازرگانی' in detected_actors):
                detected_actors.remove('وزارت بازرگانی')
                detected_actors.append('اتاق­ بازرگانی، صنایع، معادن و کشاورزی ایران')



    return detected_actors



