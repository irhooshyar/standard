import math
import re
import threading
from itertools import chain
from elasticsearch import Elasticsearch
from abdal import es_config
from abdal.config import Thread_Count as thread_Count
from doc.models import ExecutiveRegulations, DocumentParagraphs, Document, Actor
from es_scripts.util.ESQueryBuilder import regex
from es_scripts.util.Clause import get_clause_by_paragraph, get_paragraphs_by_clause, get_document_paragraphs
from es_scripts.util.search import search_size_all
from scripts.Persian.Preprocessing import standardIndexName
import time

# پیش از انتقال به الستیک :
# 2750 سند که در متن آن ها ایین نامه اجرایی این بند آمده است
# زمان اجرا حدود 2 ساعت
# پس از انتقال به الستیک :
# 10621 سند که در متن آن ها ایین نامه اجرایی این بند آمده است
# زمان اجرا حدود 1/2 ساعت


pishnevis = {('پیش', 'نویس', 0), 'پیشنویس'}
aiinname = {('ایین', 'نامه', 0), 'اییننامه'}
bakhshname = {('بخش', 'نامه', 0), 'بخشنامه'}
shivename = {('شیوه', 'نامه', 0)}
dastoorolamal = {'دستورالعمل'}
asasname = {('اساس', 'نامه', 0), 'اساسنامه'}
mosavabe = {'مصوبه'}
laiehe = {'لایحه', 'لوایح'}
tarh = {'طرح'}

all_accepted_doc_types = aiinname.union(bakhshname, shivename, dastoorolamal, asasname, mosavabe, laiehe, tarh)

MAX_D = 50


def get_patterns():
    return [
        get_paragraphs_algorithm6(),
        get_paragraphs_algorithm1(),
        get_paragraphs_algorithm7(),
        get_paragraphs_algorithm8(),
        get_paragraphs_algorithm9(),
        get_paragraphs_algorithm10(),
        get_paragraphs_algorithm11(),
        get_paragraphs_algorithm3(),
        get_paragraphs_algorithm5()
    ]


def get_paragraphs_algorithm1():
    # ...آیین نامه اجرایی این...
    # detect 1022 paragraphs on ایران کامل
    # detect 1682 paragraphs on ایران کامل with es
    sub_pattern1 = 'این'
    sub_pattern2 = 'اجرایی'
    return all_accepted_doc_types, sub_pattern2, sub_pattern1, 0


def get_paragraphs_algorithm3():
    # ...آیین نامه...به تصویب...خواهد رسید/میرسد...
    # detect 1161 paragraphs on ایران کامل
    # detect 2041 paragraphs on ایران کامل with es
    sub_pattern1 = 'به'
    sub_pattern2 = 'تصویب'
    sub_pattern3 = {('می', 'رسد', 0), 'میرسد', 'برساند', ('خواهد', 'رسید', 0)}
    return ((all_accepted_doc_types, sub_pattern1, MAX_D), sub_pattern2, 0), sub_pattern3, MAX_D


def get_paragraphs_algorithm5():
    # ...آیین نامه...تهیه/تدوین/ارایه...میشود/نماید/گردد/کند...
    # detect 3105 paragraphs on ایران کامل
    # detect 5182 paragraphs on ایران کامل with es
    sub_pattern1 = {'تهیه', 'تدوین', 'ارایه'}
    sub_pattern2 = {'کند', 'نماید', 'گردد', ('خواهد', 'شد', 0), ('می', 'شود', 0), 'میشود'}
    return (all_accepted_doc_types, sub_pattern1, MAX_D), sub_pattern2, MAX_D


def get_paragraphs_algorithm6():
    # ...پیش نویس آیین نامه...
    # detect 71 paragraphs on ایران کامل
    # detect 109 paragraphs on ایران کامل with es
    return pishnevis, all_accepted_doc_types, 0


def get_paragraphs_algorithm7():
    # ...اطلس ملی...
    # detect 4 paragraphs on ایران کامل
    # detect 4 paragraphs on ایران کامل with es
    return 'اطلس', 'ملی', 0


def get_paragraphs_algorithm8():
    # ...تهیه و تدوین سند...
    # detect 5 paragraphs on ایران کامل
    # detect 6 paragraphs on ایران کامل with es
    return 'تهیه', 'و', 'تدوین', 'سند', 0


def get_paragraphs_algorithm9():
    # ...تهیه و تدوین ... برنامه ملی...
    # detect 2 paragraphs on ایران کامل
    # detect 0 paragraphs on ایران کامل with es
    keyword1 = ('تهیه', 'و', 'تدوین', 0)
    keyword2 = ('برنامه', 'ملی', 0)
    return keyword1, keyword2, MAX_D


def get_paragraphs_algorithm10():
    # ...ضوابط فنی ... دستورالعمل...
    # detect 4 paragraphs on ایران کامل
    # detect 8 paragraphs on ایران کامل with es
    keyword1 = ('ضوابط', 'فنی', 0)
    keyword2 = 'دستورالعمل'
    return keyword1, keyword2, MAX_D


def get_paragraphs_algorithm11():
    # ...تهیه...آیین نامه...
    # detect 1820 paragraphs on ایران کامل
    # detect 3206 paragraphs on ایران کامل with es
    sub_pattern1 = ['تهیه', 'تدوین', 'ارایه']
    return sub_pattern1, all_accepted_doc_types.union(pishnevis), 3


def get_disallowed_doc_type():
    return [
        'مصوبه',
        'رای',
        'تصویب نامه',
        'تصویبنامه',
        'تصویب­نامه',
        'تصویب‌نامه',
        'شماره',
        'اصلاح',
        'ابطال',
        'موافقت',
        'نقل',
        'پروگرام',
        'تصمیمات',
        'تصمیم',
        'لغو',
        'منتفی بودن',
        'تصویب',
        'تاییدیه',
        'تایید',
    ]


es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)
bucket_size = es_config.BUCKET_SIZE
search_result_size = es_config.SEARCH_RESULT_SIZE


def Slice_Dict(list_, n):
    results = []
    size = len(list_)
    step = math.ceil(size / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, size)
        results.append(list_[start_idx:end_idx])
    return results


def apply(country):
    start_t = time.time()

    ExecutiveRegulations.objects.filter(country_id=country).delete()

    # get paragraphs containing pattern
    index_name = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    query = {
        'bool': {
            'must_not': [
                {'match_phrase_prefix': {'document_name': word}} for word in get_disallowed_doc_type()
            ],
            'should': [
                regex(pattern, 'attachment.content') for pattern in get_patterns()
            ],
            # "minimum_should_match": 1,
            # 'must': [
            #     {
            #         "term": {
            #             "paragraph_id": 715907
            #         }
            #     }
            # ]
        }
    }

    response = search_size_all(client, index=index_name,
                               _source_includes=['paragraph_id', 'attachment.content', 'document_name', 'document_id'],
                               request_timeout=40,
                               query=query,
                               highlight={
                                   "order": "score",
                                   "fields": {
                                       "attachment.content":
                                           {
                                               "pre_tags": ["<em>"],
                                               "post_tags": ["</em>"],
                                               "number_of_fragments": 0
                                           }
                                   }
                               }
                               )

    total = response['hits']['total']['value']
    print(f'found {total} paras.')

    docs = Document.objects.filter(country_id=country).values('id', 'approval_date')
    doc_to_approval_date_dict = {doc['id']: doc['approval_date'] for doc in docs}

    # thread_Count = 1

    result_create_list = [None] * thread_Count
    thread_obj = []
    thread_number = 0
    sliced_Files = Slice_Dict(response['hits']['hits'], thread_Count)
    for S in sliced_Files:
        thread = threading.Thread(target=extract_executive,
                                  args=(
                                      result_create_list, S, doc_to_approval_date_dict, country, thread_number))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    result_create_list = list(chain.from_iterable(result_create_list))
    ExecutiveRegulations.objects.bulk_create(result_create_list)

    end_t = time.time()
    print('Complete paragraphs added (' + str(end_t - start_t) + ').')


def extract_executive(result_create_list, paras_containing_pattern, doc_to_approval_date_dict, country, thread_number):
    create_list = []
    total = len(paras_containing_pattern)
    for count, para in enumerate(paras_containing_pattern):
        if thread_number == 0:
            print(f'{round((count / total)*100,2)}%')

        highlight = para["highlight"]["attachment.content"][0]
        pattern_starts = [m.start() for m in re.finditer('<em>', highlight)]
        pattern_stops = [m.start() for m in re.finditer('</em>', highlight)]
        pattern = "#".join(
            [
                highlight[pattern_starts[index]: pattern_stops[index]] for index in range(len(pattern_starts))
            ]
        )
        pattern = pattern.replace('<em>', "").replace("</em>", '')

        clauses = get_clause_by_paragraph(para['_source']['paragraph_id'], para['_source']['document_id'], country)
        clause_info = ' از '.join([c[0] + " " + str(c[1]) for c in clauses])

        actors_info = get_para_actors_info(
            para["highlight"]["attachment.content"][0].replace('<em>', "").replace("</em>", '')
        )

        [has_executive, executive_doc_obj] = get_para_executive_info(para['_source']['document_name'],
                                                                     para['_source']['document_id'],
                                                                     para['_source']['paragraph_id'], country)

        try:
            [deadline_date, new_date] = get_para_deadline_info(
                para["highlight"]["attachment.content"][0].replace('<em>', "").replace("</em>", ''),
                doc_to_approval_date_dict[para['_source']['document_id']]
            )
            deadline_status = None

            if not has_executive and deadline_date is not None:
                deadline_status = 'منقضی شده'

            if executive_doc_obj is not None and new_date is not None:
                document = Document.objects.get(id=executive_doc_obj.id)
                approval_date = document.approval_date

                if approval_date != None:
                    year_1 = int(new_date[0:4])
                    year_2 = int(approval_date[0:4])
                    mouth_1 = int(new_date[5:7])
                    mouth_2 = int(approval_date[5:7])
                    day_1 = int(new_date[8:10])
                    day_2 = int(approval_date[8:10])

                    if year_2 < year_1:
                        deadline_status = 'نگارش شده'
                    elif year_1 == year_2:
                        if mouth_2 < mouth_1:
                            deadline_status = 'نگارش شده'
                        elif mouth_2 == mouth_1:
                            if day_2 <= day_1:
                                deadline_status = 'نگارش شده'
                            else:
                                deadline_status = 'منقضی شده'
                        else:
                            deadline_status = 'منقضی شده'
                    else:
                        deadline_status = 'منقضی شده'
        except:
            # print(f"error on para {original_para['id']}(id)")
            deadline_date = None
            deadline_status = None

        exe_reg_obj = ExecutiveRegulations(
            found_pattern=pattern,
            country_id=country,
            paragraph_id_id=para['_source']['paragraph_id'],
            document_id_id=para['_source']['document_id'],
            clause_info=clause_info,
            actors_info=actors_info,
            document_clause_id=None,
            has_executive=has_executive,
            executive_regulation_doc_id=executive_doc_obj,
            deadline_date=deadline_date,
            deadline_status=deadline_status,
        )
        create_list.append(exe_reg_obj)

    result_create_list[thread_number] = create_list


def get_para_actors_info(paragraph_text):
    result_actors_info = {}
    json_result = {
        "actors_info": {}
    }

    start_kw_list = ['توسط', 'پیشنهاد', 'هماهنگی']
    end_kw_list = ['تصویب', 'تهیه']

    category_kw_list = ['وزارت', 'سازمان', 'شرکت',
                        'وزیر', 'دفتر', 'بنیاد', 'شورا', 'ستاد']

    sentence_list = paragraph_text.split('.')

    for sentence in sentence_list:

        start_index = -1
        end_index = -1

        for kw in start_kw_list:
            if kw in sentence:
                start_index = sentence.find(kw)
                break

        for kw in end_kw_list:
            if kw in sentence:
                end_index = sentence.find(kw)
                break

        if start_index != -1 and end_index != -1:

            cropped_text = sentence[start_index:end_index]

            for category in category_kw_list:
                if category in cropped_text:
                    catetory_actors = Actor.objects.filter(
                        actor_category_id__name=category)

                    for actor in catetory_actors:
                        actor_forms = actor.forms.split('/')
                        for actor_form in actor_forms:
                            actor_form_patterns = [actor_form]

                            if (actor.name != 'وزارت کشور' and actor.name != 'وزارت نیرو') \
                                    and (actor.name != 'وزارت اطلاعات') \
                                    and (actor.name != 'سازمان فناوری اطلاعات'):
                                actor_form_patterns += [actor_form.replace(
                                    'سازمان ', '').replace('وزارت ', '')]

                            actor_form_patterns = list(
                                set(actor_form_patterns))

                            if any(actor_form_pt in cropped_text for actor_form_pt in actor_form_patterns):
                                result_actors_info[actor.name] = actor_form
                                break

            other_actors = Actor.objects.filter(actor_category_id__name='سایر')

            for actor in other_actors:
                actor_forms = actor.forms.split('/')
                for actor_form in actor_forms:
                    actor_form_patterns = [actor_form]

                    if any(actor_form_pt in cropped_text for actor_form_pt in actor_form_patterns):
                        result_actors_info[actor.name] = actor_form
                        break

            vezarats_forms = ['وزارتخانه‌های', 'وزارتخانههای',
                              'وزارت‌خانه‌های', 'وزارت خانه های']

            if any(vezarat_form in cropped_text for vezarat_form in vezarats_forms) and '، کشور' in cropped_text:
                result_actors_info['وزارت کشور'] = 'کشور'

            # print(result_actors_info)
            json_result = {
                "actors_info": result_actors_info
            }

    return json_result


def executive_query(disallowed_executive_type, doc_name):
    must_not = [{"match_phrase_prefix": {"name": item}} for item in disallowed_executive_type]
    must_not.append({"term": {"name.keyword": doc_name}})
    query = {
        'bool': {
            "must_not": must_not,
            'must': [{"match_phrase": {"name": {"query": doc_name, "slop": 0}}}]
        }
    }
    return query


def get_para_executive_info(law_document_name: str, doc_id: int, paragraph_id: int, country):
    executive_doc_obj = None
    has_executive = False
    law_document_name = law_document_name
    disallowed_executive_type = [
        'قانون الحاق',
        'اصلاح'
    ]

    index_name = standardIndexName(country, Document.__name__)
    query = executive_query(disallowed_executive_type, law_document_name)

    response = search_size_all(client, index=index_name,
                               _source_includes=['name', 'document_id'],
                               request_timeout=40,
                               query=query,
                               highlight={
                                   "order": "score",
                                   "fields": {
                                       "name":
                                           {
                                               "pre_tags": ["<em>"],
                                               "post_tags": ["</em>"],
                                               "number_of_fragments": 0
                                           }
                                   }
                               }
                               )
    doc_paragraphs = get_document_paragraphs(doc_id, country)
    for doc in response['hits']['hits']:
        highlight = doc["highlight"]["name"][0]
        pattern_starts = [m.start() for m in re.finditer('<em>', highlight)]
        pattern_stops = [m.start() for m in re.finditer('</em>', highlight)]
        patterns = [highlight[pattern_starts[index]: pattern_stops[index] + 5] for index in range(len(pattern_starts))]
        for pattern in patterns:
            highlight = highlight.replace(pattern, " ")
        highlight = highlight.replace("  ", " ").strip()
        paragraphs = get_paragraphs_by_clause(highlight, doc_paragraphs, country)
        if paragraph_id in [para['_source']['paragraph_id'] for para in paragraphs]:
            has_executive = True
            executive_doc_obj = doc["_source"]["document_id"]
            break
    return [has_executive, executive_doc_obj]


def get_clause_list_regex(clauses: list):
    regex = r''
    clauses.reverse()
    for clause in clauses:
        regex += rf'{clause[0]}.+{clause[1] if clause[1] is not None else ""}.+'
    return regex


def get_para_deadline_info(para_text, date):
    deadline_date = None
    new_date = None

    deadline_pattern_keywords = ['ظرف', 'ظرف مدت', 'ظرف مهلت', 'طی', 'طی مدت', 'طی مهلت', 'حداکثر', 'فواصل زمانی', 'تا',
                                 'در مدت']
    time_categories = ['روز', 'هفته', 'ماه', 'سال']
    numbers_dict = {
        "یک": {
            'value': 1,
        },
        "دو": {
            'value': 2,
        },
        "سه": {
            'value': 3,
        },
        "چهار": {
            'value': 4,
        },
        "پنج": {
            'value': 5,
        },
        "شش": {
            'value': 6,
        },
        "هفت": {
            'value': 7,
        },
        "هشت": {
            'value': 8,
        },
        "نه": {
            'value': 9,
        },
        "ده": {
            'value': 10,
        }
    }

    for deadline_keyword in deadline_pattern_keywords:
        for nubmer_text, value in numbers_dict.items():
            for time_category in time_categories:
                # ظرف شش ماه
                pattern1 = deadline_keyword + ' ' + nubmer_text + ' ' + time_category
                pattern2 = deadline_keyword + ' ' + nubmer_text + ' ' + '(' + str(
                    value['value']) + ')' + ' ' + time_category
                pattern3 = deadline_keyword + ' ' + str(value['value']) + ' ' + time_category

                # ظرف شش‌ماه
                pattern4 = deadline_keyword + ' ' + nubmer_text + '‌' + time_category;
                pattern5 = deadline_keyword + ' ' + nubmer_text + ' ' + '(' + str(
                    value['value']) + ')' + '‌' + time_category
                pattern6 = deadline_keyword + ' ' + str(value['value']) + '‌' + time_category

                # ظرف یکسال
                pattern7 = deadline_keyword + ' ' + nubmer_text + time_category
                pattern8 = deadline_keyword + ' ' + nubmer_text + ' ' + '(' + str(value['value']) + ')' + time_category
                pattern9 = deadline_keyword + ' ' + str(value['value']) + time_category

                patterns = [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8, pattern9]

                for pattern in patterns:
                    if pattern in para_text:
                        deadline_date = pattern

                        year = int(date[0:4])
                        mouth = int(date[5:7])
                        day = int(date[8:10])

                        if time_category == 'روز':
                            day += value['value']

                            if day > 30:
                                day -= 30
                                mouth += 1

                        if time_category == 'ماه':
                            mouth += value['value']

                            # print(value['value'])

                            if mouth > 12:
                                mouth -= 12
                                year += 1

                        if time_category == 'سال':
                            year += value['value']

                        if mouth < 10:
                            mouth = '0' + str(mouth)
                        if day < 10:
                            day = '0' + str(day)

                        new_date = str(year) + '/' + str(mouth) + "/" + str(day)

    return [deadline_date, new_date]
