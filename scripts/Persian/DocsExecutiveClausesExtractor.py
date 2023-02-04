import math
import operator
import re
import threading
from functools import reduce
from itertools import chain

from django.db.models import Q, F

from abdal import config
from doc.models import DocumentCompleteParagraphs
from doc.models import Document, DocumentClause
from doc.models import DocumentParagraphs
from doc.models import ExecutiveRegulations, Actor
import time


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


# def get_paragraphs(base_result):
#     # total 5677 paragraphs found on ایران کامل
#     all_accepted_doc_type = [
#         'ایین نامه',
#         'ائین نامه',
#         'ایین‌نامه',
#         'ائین‌نامه',
#         'اییننامه',
#         'ائیننامه',
#         'ایین­نامه',
#         'ائین­نامه',
#
#         # "بخشنامه",
#         # "بخش نامه",
#         # "بخش‌نامه",
#         # "بخش­نامه",
#         #
#         # "شیوه نامه",
#         # "شیوه‌نامه",
#         # "شیوه­نامه",
#
#         "دستورالعمل",
#
#         # "اساسنامه",
#         # "اساس نامه",
#         # "اساس‌نامه",
#         # "اساس­نامه",
#         #
#         # 'پیش نویس',
#         # 'پیشنویس',
#         # 'پیش‌نویس',
#         # 'پیش­نویس',
#         #
#         # 'مصوبه',
#         #
#         # 'لایحه',
#         # 'لوایح',
#         #
#         # ' طرح',
#     ]
#
#     # result1 = base_result.filter(text__iregex=get_paragraphs_algorithm1(all_accepted_doc_type))
#     # result2 = get_paragraphs_algorithm2(all_accepted_doc_type,base_result)
#     result3 = base_result.filter(text__iregex=get_paragraphs_algorithm3(all_accepted_doc_type))
#     # result4 = base_result.filter(text__iregex=get_paragraphs_algorithm4(all_accepted_doc_type))
#     # result5 = base_result.filter(text__iregex=get_paragraphs_algorithm5(all_accepted_doc_type))
#     # return result5 | result4 | result3 | result2 | result1
#     return result3


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
        # '',
    ]


def get_paragraphs(base_result):
    pishnevis = [
        'پیش نویس',
        'پیشنویس',
        'پیش‌نویس',
        'پیش­نویس',
    ]
    all_accepted_doc_types = [
        'ایین نامه',
        'ائین نامه',
        'ایین‌نامه',
        'ائین‌نامه',
        'اییننامه',
        'ائیننامه',
        'ایین­نامه',
        'ائین­نامه',

        "بخشنامه",
        "بخش نامه",
        "بخش‌نامه",
        "بخش­نامه",

        "شیوه نامه",
        "شیوه‌نامه",
        "شیوه­نامه",

        "دستورالعمل",

        "اساسنامه",
        "اساس نامه",
        "اساس‌نامه",
        "اساس­نامه",

        'مصوبه',

        'لایحه',
        'لوایح',

        ' طرح',
    ]

    result = []

    for para in base_result.iterator():
        text =  para.text

        pattern = get_paragraphs_algorithm6(all_accepted_doc_types,pishnevis)
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm1(all_accepted_doc_types)
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm7()
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm8()
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm9()
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm10()
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm11(all_accepted_doc_types,pishnevis)
        if re.search(pattern, text):
            result.append({'obj': para, 'pattern': pattern})
            continue

        pattern = get_paragraphs_algorithm3(all_accepted_doc_types)
        if re.search(pattern, text):
            result.append({'obj':para,'pattern':pattern})
            continue

        pattern = get_paragraphs_algorithm5(all_accepted_doc_types)
        if re.search(pattern, text):
            result.append({'obj':para,'pattern':pattern})
            continue

    return result

def get_paragraphs_algorithm1(all_accepted_doc_types):
    # ...آیین نامه اجرایی این...
    # detect 1022 paragraphs on ایران کامل
    sub_pattern1 = 'این'
    sub_pattern2 = 'اجرایی'
    regex = fr'({"|".join(all_accepted_doc_types)}) {sub_pattern2} {sub_pattern1}'
    return regex

def get_paragraphs_algorithm3(all_accepted_doc_types):
    # ...آیین نامه...به تصویب...خواهد رسید/میرسد...
    # detect 1161 paragraphs on ایران کامل
    sub_pattern1 = 'به تصویب'
    sub_pattern2 = ['خواهد رسید','میرسد','می رسد','می‌رسد']
    regex = fr'({"|".join(all_accepted_doc_types)}).*{sub_pattern1}.*({"|".join(sub_pattern2)})'
    return regex

def get_paragraphs_algorithm5(all_accepted_doc_types):
    # ...آیین نامه...تهیه/تدوین/ارایه...میشود/نماید/گردد/کند...
    # detect 3105 paragraphs on ایران کامل
    sub_pattern1 = ['تهیه','تدوین','ارایه','ارائه']
    sub_pattern2 = ['کند','نماید','گردد','خواهد شد','می شود','میشود','می‌شود']
    regex = fr'({"|".join(all_accepted_doc_types)}).*({"|".join(sub_pattern1)}).*({"|".join(sub_pattern2)})'
    return regex

def get_paragraphs_algorithm6(all_accepted_doc_types,pishnevis):
    # ...پیش نویس آیین نامه...
    # detect 71 paragraphs on ایران کامل
    regex = fr'({"|".join(pishnevis)}) ({"|".join(all_accepted_doc_types)})'
    return regex

def get_paragraphs_algorithm7():
    # ...اطلس ملی...
    # detect 4 paragraphs on ایران کامل
    keyword = 'اطلس ملی'
    regex = fr'{keyword}'
    return regex

def get_paragraphs_algorithm8():
    # ...تهیه و تدوین سند...
    # detect 5 paragraphs on ایران کامل
    keyword = 'تهیه و تدوین سند'
    regex = fr'{keyword}'
    return regex

def get_paragraphs_algorithm9():
    # ...تهیه و تدوین ... برنامه ملی...
    # detect 2 paragraphs on ایران کامل
    keyword1 = 'تهیه و تدوین'
    keyword2 = 'برنامه ملی'
    regex = fr'{keyword1}.*{keyword2}'
    return regex

def get_paragraphs_algorithm10():
    # ...ضوابط فنی ... دستورالعمل...
    # detect 4 paragraphs on ایران کامل
    keyword1 = 'ضوابط فنی'
    keyword2 = 'دستورالعمل'
    regex = fr'{keyword1}.{{1,40}}{keyword2}'
    return regex

def get_paragraphs_algorithm11(all_accepted_doc_types,pishnevis):
    # ...تهیه...آیین نامه...
    # detect 1820 paragraphs on ایران کامل
    sub_pattern1 = ['تهیه','تدوین','ارایه','ارائه']
    regex = fr'({"|".join(sub_pattern1)}).{{1,10}}({"|".join(all_accepted_doc_types+pishnevis)})'
    return regex



def Slice_Dict(list_, n):
    results = []
    size = len(list_)
    step = math.ceil(size / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, size)
        results.append(list_[start_idx:end_idx])
    return results


def apply(folder_name, Country):

    start_t = time.time()
    Create_List = []
    batch_size = 1000

    ExecutiveRegulations.objects.filter(country_id=Country).delete()

    # get paragraphs containing pattern
    # doc_ids = Document.objects.filter(country_id=Country, name__istartswith='قانون').values("id")
    # base_result = DocumentCompleteParagraphs.objects.filter(document_id__in=doc_ids)
    base_result = DocumentCompleteParagraphs.objects.filter(document_id__country_id=Country). \
        exclude(reduce(operator.or_, (Q(document_id__name__startswith=word) for word in get_disallowed_doc_type())))

    paras_containing_pattern = get_paragraphs(base_result)

    total = len(paras_containing_pattern)
    print(f'found {total} paras.')


    document_clauses = DocumentClause.objects.filter(document_id__country_id=Country). \
        order_by('-start_paragraph_id'). \
        values('id' , 'document_id__id' , 'start_paragraph_id__id',
               'start_paragraph_id__text', 'clause_type', 'clause_number', 'document_id__name',
               'parent_clause', 'parent_clause__clause_type', 'parent_clause__clause_number',
               'parent_clause__parent_clause', 'parent_clause__parent_clause__clause_type',
               'parent_clause__parent_clause__clause_number',
               'parent_clause__parent_clause__parent_clause',
               'parent_clause__parent_clause__parent_clause__clause_type',
               'parent_clause__parent_clause__parent_clause__clause_number', )
    document_clauses_dict = {}
    for document_clause in document_clauses:
        if document_clause['document_id__id'] not in document_clauses_dict.keys():
            document_clauses_dict[document_clause['document_id__id']] = \
                {
                    document_clause['start_paragraph_id__id']:document_clause
                }
        else:
            document_clauses_dict[document_clause['document_id__id']][document_clause['start_paragraph_id__id']] = document_clause
    print(f'created clauses dict.')


    paras = DocumentParagraphs.objects.filter(document_id__country_id=Country)\
        .values('text', 'document_id__approval_date', 'id', 'document_id__id')
    paras_dict = {}
    for para in paras:
        paras_dict[para['text']] = {para['document_id__id']:para}

    iteration_count = len(paras_containing_pattern)//batch_size
    Sliced_for_iterations = Slice_Dict(paras_containing_pattern, iteration_count)

    for index,Slice in enumerate(Sliced_for_iterations):
        iterate(Slice,document_clauses_dict,paras_dict,Country)
        print(f'iteration {index+1} completed. {batch_size*(index+1)} paras completed')




    # ExecutiveRegulations.objects.bulk_create(Result_Create_List)

    end_t = time.time()
    print('Complete paragraphs added (' + str(end_t - start_t) + ').')


def iterate(paras_containing_pattern,document_clauses_dict,paras_dict,Country):
    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    Sliced_Files = Slice_Dict(paras_containing_pattern, Thread_Count)
    thread_obj = []
    thread_number = 0
    for S in Sliced_Files:
        thread = threading.Thread(target=extract_executive,
                                  args=(
                                  Result_Create_List, S, document_clauses_dict, paras_dict, Country, thread_number))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))
    ExecutiveRegulations.objects.bulk_create(Result_Create_List)




def extract_executive(Result_Create_List,paras_containing_pattern,document_clauses_dict,paras_dict,Country,thread_number):
    Create_List = []
    symboles = ['-', 'ـ']
    total = len(paras_containing_pattern)
    count = 1
    for para_dict in paras_containing_pattern:
        para = para_dict['obj']
        if count % 100 == 0 and thread_number == 0:
            print(f'{(count/total)*100}%')
        count += 1
        if para.document_id.id not in document_clauses_dict.keys():
            # print(f"can't find any clause for document {para.document_id}(id).")
            continue
        res = document_clauses_dict[para.document_id.id]
        start_para_ids = [x for x in res.keys() if x <= para.id]
        if len(start_para_ids) == 0:
            # print(f"can't find any clause for document {para.document_id}(id).")
            continue
        res = res[max(start_para_ids)]


        para_text = res['start_paragraph_id__text']
        clause_segment = para_text[:10]
        clause_list = []

        for symbol in symboles:
            # executive_doc_obj = None
            symbol_index = clause_segment.find(symbol)
            if symbol_index == -1:
                continue
            # clause_name = clause_segment[:symbol_index].strip()

            clause_para = res
            clause_type = (
                clause_para['clause_type']) if clause_para['clause_type'] != None else ''
            clause_number = str(
                clause_para['clause_number']) if clause_para['clause_number'] != None else ''
            clause_str = (clause_type + ' ' + clause_number).strip()
            clause_list.append(clause_str)

            if clause_para['parent_clause'] is not None:
                clause_type_parent = (
                    clause_para['parent_clause__clause_type']) if clause_para['parent_clause__clause_type'] else ''

                clause_number_parent = str(
                    clause_para['parent_clause__clause_number']) if clause_para['parent_clause__clause_number'] else ''


                clause_str = (clause_type_parent + ' ' +
                              clause_number_parent).strip()
                clause_list.append(clause_str)

                if clause_para['parent_clause__parent_clause'] is not None:

                    clause_type_parent_parent = (
                        clause_para['parent_clause__parent_clause__clause_type']) if clause_para['parent_clause__parent_clause__clause_type'] else ''

                    clause_number_parent_parent = str(
                        clause_para['parent_clause__parent_clause__clause_number']) if clause_para['parent_clause__parent_clause__clause_number'] else ''

                    clause_str = (clause_type_parent_parent +
                                  ' ' + clause_number_parent_parent).strip()

                    clause_list.append(clause_str)

                    if clause_para['parent_clause__parent_clause__parent_clause'] is not None:
                        clause_type_parent_parent_parent = (
                            clause_para['parent_clause__parent_clause__parent_clause__clause_type']) if clause_para['parent_clause__parent_clause__parent_clause__clause_type'] else ''

                        clause_number_parent_parent_parent = str(
                            clause_para['parent_clause__parent_clause__parent_clause__clause_number']) if clause_para['parent_clause__parent_clause__parent_clause__clause_number'] else ''

                        clause_str = (clause_type_parent_parent_parent +
                                      ' ' + clause_number_parent_parent_parent).strip()

                        clause_list.append(clause_str)


            clause_info = ' از '.join(clause_list)
            clause_info2 = ' '.join(clause_list)
            # print(f'{count} done ')

            if para.text not in paras_dict.keys() or para.document_id.id not in paras_dict[para.text].keys():
                continue
            original_para = paras_dict[para.text][para.document_id.id]

            actors_info = get_para_actors_info(original_para['text'])


            [has_executive, executive_doc_obj] = get_para_executive_info(clause_info2, res['document_id__name'], Country,clause_para)

            try:
                [deadline_date, new_date] = get_para_deadline_info(original_para['text'], original_para['document_id__approval_date'])
                deadline_status = None

                if has_executive == False and deadline_date != None:
                    deadline_status = 'منقضی شده'

                if executive_doc_obj != None and new_date != None:
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
                found_pattern=para_dict['pattern'],
                country_id=Country,
                paragraph_id_id=original_para['id'],
                document_id_id=original_para['document_id__id'],
                clause_info=clause_info,
                actors_info=actors_info,
                document_clause_id=clause_para['id'],
                has_executive=has_executive,
                executive_regulation_doc=executive_doc_obj,
                deadline_date=deadline_date,
                deadline_status=deadline_status,
            )
            Create_List.append(exe_reg_obj)

    Result_Create_List[thread_number] = Create_List



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



def get_para_executive_info(clause_info_list, law_document_name:str, Country, clause_para):
    executive_doc_obj = None
    has_executive = False
    law_document_name = law_document_name.strip()
    disallowed_executive_type = [
        'قانون الحاق',
        'اصلاح'
    ]


    law_document_name_regex = law_document_name.replace(' ','[\s ‌­]*').replace('‌','[\s ‌­]*').replace('­','[\s ‌­]*')
    res_docs = Document.objects.filter(country_id = Country). \
        exclude(name = law_document_name). \
        filter(name__regex = rf'{law_document_name_regex}'). \
        exclude(reduce(operator.or_, (Q(name__startswith=word) for word in disallowed_executive_type)))



    # first algorithm

    # get target clause with its parent
    clauses_in_doc = [[clause_para['clause_type'], clause_para['clause_number']]]
    if clause_para['parent_clause'] is not None:
        clauses_in_doc.append([clause_para['parent_clause__clause_type'],
                               clause_para['parent_clause__clause_number']])
    if clause_para['parent_clause__parent_clause'] is not None:
        clauses_in_doc.append([clause_para['parent_clause__parent_clause__clause_type'],
                               clause_para['parent_clause__parent_clause__clause_number']])
    if clause_para['parent_clause__parent_clause__parent_clause'] is not None:
        clauses_in_doc.append([clause_para['parent_clause__parent_clause__parent_clause__clause_type'],
                               clause_para['parent_clause__parent_clause__parent_clause__clause_number']])



    # detect ماده واحده from its clauses
    made_vahed = (clauses_in_doc[-1][1] is not None) and (clauses_in_doc[-1][1].strip() == 'واحده')



    try:
        # search for regulations with target clause in their name
        index = 0
        while index < len(clauses_in_doc):
            if index == len(clauses_in_doc)-1 and made_vahed:
                break
            pattern = get_clause_list_regex(clauses_in_doc[index:])
            result = res_docs.filter(name__regex=pattern)
            if result.count() == 1:
                doc_name = result[0].name.strip()
                doc_name = re.sub(law_document_name_regex,"#",doc_name)
                while pattern.endswith(".+"):
                    pattern = pattern[:-2]
                doc_name = re.sub(pattern,"#",doc_name).replace(" ","")
                if any([clauses_in_doc[i][0] in doc_name for i in range(index)]):
                    index += 1
                    continue
                index_1 = doc_name.find('#')
                index_2 = doc_name.find('#',index_1)
                if index_2 - index_1 < 3:
                    return [True, result[0]]
            index += 1

        if made_vahed:
            index = 0
            clauses_in_doc_no_made = clauses_in_doc[:-1].copy()
            while index < len(clauses_in_doc_no_made):
                pattern = get_clause_list_regex(clauses_in_doc_no_made[index:])
                result = res_docs.filter(name__regex=pattern)
                if result.count() == 1:
                    doc_name = result[0].name.strip()
                    doc_name = re.sub(law_document_name_regex, "#", doc_name)
                    while pattern.endswith(".+"):
                        pattern = pattern[:-2]
                    doc_name = re.sub(pattern, "#", doc_name).replace(" ", "")
                    if any([clauses_in_doc_no_made[i][0] in doc_name for i in range(index)]):
                        index += 1
                        continue
                    index_1 = doc_name.find('#')
                    index_2 = doc_name.find('#', index_1)
                    if index_2 - index_1 < 3:
                        return [True, result[0]]
                index += 1

    except:
        pass
        # print('error')
        # print(clauses_in_doc)
        # print(law_document_name_regex)






    # second algorithm
    try:
        clause_info_list = clause_info_list.replace('ماده واحده', '').strip()
        kw1 = 'نامه اجرایی'
        kw2 = 'قانون'

        for res in res_docs:
            if res.name.find(kw1) == -1 or res.name.find(kw2) == -1:
                continue
            start_index = res.name.find(kw1) + len(kw1)
            end_index = res.name.find(kw2)

            if res.name[start_index:end_index].__len__() < 40:
                selected_doc_clause = res.name[start_index:end_index].strip()
                selected_doc_clause = selected_doc_clause.replace('(' , '').replace(')', '').replace('”','').replace('“','') \
                    .replace('»','').replace('«','').strip()
                selected_doc_clause = selected_doc_clause.replace('  ',' ').strip()

                if selected_doc_clause == clause_info_list:
                    # print(res.name)
                    executive_doc_obj = res
                    has_executive = True
                    break
    except:
        pass

    return [has_executive,executive_doc_obj]


def get_clause_list_regex(clauses:list):
    regex = r''
    clauses.reverse()
    for clause in clauses:
        regex += rf'{clause[0]}.+{clause[1] if clause[1] is not None else ""}.+'
    return regex


def get_para_deadline_info(para_text, date):

    deadline_date = None
    new_date = None

    deadline_pattern_keywords = ['ظرف', 'ظرف مدت', 'ظرف مهلت', 'طی', 'طی مدت', 'طی مهلت', 'حداکثر', 'فواصل زمانی', 'تا','در مدت']
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
                pattern2 = deadline_keyword + ' ' + nubmer_text + ' ' + '(' + str(value['value']) + ')' + ' ' + time_category
                pattern3 = deadline_keyword + ' ' + str(value['value']) + ' ' + time_category

                # ظرف شش‌ماه
                pattern4 = deadline_keyword + ' ' + nubmer_text + '‌' + time_category;
                pattern5 = deadline_keyword + ' ' + nubmer_text + ' ' + '(' + str(value['value']) + ')' + '‌' + time_category
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

                        if mouth <10:
                            mouth = '0' + str(mouth)
                        if day <10:
                            day = '0' + str(day)


                        new_date = str(year)+ '/'+ str(mouth)+ "/"+ str(day)







    return [deadline_date, new_date]