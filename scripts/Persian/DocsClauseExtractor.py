import operator
import re

from doc.models import DocumentSubject, SubjectKeyWords, Subject, Document, DocumentSubjectKeywords, \
    DocumentCompleteParagraphs, \
    DocumentClause
from django.db.models import Count, Q
from unidecode import unidecode
from functools import reduce

from scripts.ProgressBar import printProgressBar


def detect_num_or_num(text: str, clause: str):
    regex_alphabet = r"[\u0622\u0627\u0628\u067E\u062A-\u062C\u0686\u062D-\u0632\u0698\u0633-\u063A\u0641\u0642\u06A9\u06AF\u0644-\u0648\u06CC\u202C\u064B\u064C\u064E-\u0652]+"
    index = text.find(clause) + len(clause)
    text = text[index:]
    match_1 = re.search(regex_alphabet, text)
    text2 = unidecode(text)
    regex_digit = r'[0-9]+'
    match_2 = re.search(regex_digit, text2)
    if match_1 and match_2:
        if match_1.start() > match_2.start():
            match_1 = None
    if match_1:
        return text[match_1.start():match_1.end()]
    if match_2:
        return text2[match_2.start():match_2.end()]
    return None


def has_madeh(text: str):
    my_regex = r"^" + r"ماده" + r".{0,7}?[-|\n]"
    pattern = re.compile(my_regex)
    # pattern.search(text)
    return pattern.search(text)
    # my_regex = r"(\s" + re.escape(TEXTO) + r"\b(?!\w)"


def has_tabsare(text: str):
    my_regex = r"^" + r"تبصره" + r".{0,7}?[-|\n]"
    pattern = re.compile(my_regex)
    # pattern.search(text)
    return pattern.search(text)


def has_joze(text: str):
    my_regex = r"^" + r"جزء" + r".{0,7}?[-|\n]"
    pattern = re.compile(my_regex)
    # pattern.search(text)
    return pattern.search(text)


def has_band(text: str):
    my_regex1 = r"^" + r"بند" + r".{0,7}?[-|\n]"
    pattern1 = re.compile(my_regex1)
    if pattern1.search(text):
        return 1
    my_regex2 = r"^.{0,7}?-"
    pattern2 = re.compile(my_regex2)
    if pattern2.search(text):
        return 2
    return None


def clean_text(text: str):
    return text.strip().replace('ـ', '-'). \
               replace('\u200c', '').replace('«', '') + '\n'


def get_new_parent_stack(parent_stack:list, obj:dict):
    if any([parent['clause_type'] == obj['clause_type'] for parent in parent_stack]):
        while True:
            parent = parent_stack.pop()
            parent['stop_paragraph_id__id'] = obj['start_paragraph_id__id'] - 1
            parent['parent_clause__id'] = None if len(parent_stack) == 0 else parent_stack[-1]['id']
            if parent['clause_type'] == obj['clause_type']:
                obj['level'] = len(parent_stack) + 1
                parent_stack.append(obj)
                break
    else:
        obj['level'] = len(parent_stack) + 1
        parent_stack.append(obj)
    return parent_stack



def apply(folder_name, Country):
    docs_with_strict_clause_order = [
        'قانون بودجه'
    ]
    batch_size = 20000

    DocumentClause.objects.filter(document_id__country_id=Country).delete()
    print("Removed Old Clauses.")

    paragraphs = DocumentCompleteParagraphs.objects.filter(document_id__country_id=Country).\
        order_by('document_id__id', 'number').values('document_id__id','text','id','document_id__name')
    total = paragraphs.count()
    print(f'Fetched all Paragraphs for Collection with ID {Country.id} ({total} paragraphs). ')


    is_strict_doc = False
    count = 1
    clauses_list = []
    parent_stack = []
    doc_id = -1
    clause_id = DocumentClause.objects.order_by('-id')
    if clause_id.count() > 0:
        clause_id = clause_id[0].id + 1
    else:
        clause_id = 1
    print(f'max id = {clause_id}')

    for paragraph in paragraphs:
        # obj = {}
        # print(f'{count} of {total}')
        count += 1
        if doc_id != paragraph['document_id__id']:
            is_strict_doc = any([doc_with_strict_clause_order in paragraph['document_id__name'] for doc_with_strict_clause_order in docs_with_strict_clause_order])
            if doc_id != -1:
                stop_paragraph_id_id = DocumentCompleteParagraphs.objects.filter(document_id__id=doc_id).order_by('-number')[0].id
                while len(parent_stack) > 0:
                    parent = parent_stack.pop()
                    parent['stop_paragraph_id__id'] = stop_paragraph_id_id
                    parent['parent_clause__id'] = None if len(parent_stack) == 0 else parent_stack[-1]['id']
            doc_id = paragraph['document_id__id']
            if len(clauses_list) > batch_size:
                bulk_create(clauses_list)
                clauses_list = []

        para_text = clean_text(paragraph['text'])


        band_type = has_band(para_text)
        if has_madeh(para_text) is not None:
            para_text = para_text[:para_text.find('-')].strip()
            obj = {
                'id' : clause_id,
                'document_id__id' : doc_id,
                'clause_type' : 'ماده',
                'clause_number' : detect_num_or_num(para_text, 'ماده'),
                'start_paragraph_id__id' : paragraph['id']
            }

        elif has_tabsare(para_text) is not None:
            if is_strict_doc and not any([parent_stack_obj['clause_type'] == 'ماده' for parent_stack_obj in parent_stack]):
                continue
            para_text = para_text[:para_text.find('-')].strip()
            obj = {
                'id' : clause_id,
                'document_id__id' : doc_id,
                'clause_type' : 'تبصره',
                'clause_number' : detect_num_or_num(para_text, 'تبصره'),
                'start_paragraph_id__id' : paragraph['id']
            }

        elif band_type is not None:
            para_text = para_text[:para_text.find('-')].strip()
            num = detect_num_or_num((para_text if band_type == 1 else 'بند ' + para_text), 'بند')
            if len(parent_stack) == 0 or \
                    parent_stack[-1]['clause_type'] == 'تبصره' or parent_stack[-1]['clause_type'] == 'ماده':
                if is_strict_doc and not any(
                        [parent_stack_obj['clause_type'] == 'تبصره' for parent_stack_obj in parent_stack]):
                    continue
                obj = {
                    'type':band_type,
                    'id': clause_id,
                    'document_id__id': doc_id,
                    'clause_type': 'بند',
                    'clause_number': num,
                    'start_paragraph_id__id': paragraph['id']
                }
            elif band_type == parent_stack[-1]['type']:
                obj = {
                    'type':band_type,
                    'id': clause_id,
                    'document_id__id': doc_id,
                    'clause_type': parent_stack[-1]['clause_type'],
                    'clause_number': num,
                    'start_paragraph_id__id': paragraph['id']
                }
            else:
                obj = {
                    'type': band_type,
                    'id': clause_id,
                    'document_id__id': doc_id,
                    'clause_type': 'جزء' if parent_stack[-1]['clause_type'] == 'بند' else 'بند',
                    'clause_number': num,
                    'start_paragraph_id__id': paragraph['id']
                }
        else:
            continue

        clauses_list.append(obj)
        parent_stack = get_new_parent_stack(parent_stack, obj)
        clause_id += 1

    stop_paragraph_id_id = DocumentCompleteParagraphs.objects.filter(document_id__id=doc_id).order_by('-number')[0].id
    while len(parent_stack) > 0:
        parent = parent_stack.pop()
        parent['stop_paragraph_id__id'] = stop_paragraph_id_id
        parent['parent_clause__id'] = None if len(parent_stack) == 0 else parent_stack[-1]['id']
    bulk_create(clauses_list)
    print("Added Clauses.")


def bulk_create(clauses_list):
    Create_List = []
    for obj in clauses_list:
        Create_List.append(
            DocumentClause(
                id=obj['id'],
                document_id_id=obj['document_id__id'],
                clause_type=obj['clause_type'],
                clause_number=obj['clause_number'],
                start_paragraph_id_id=obj['start_paragraph_id__id'],
                stop_paragraph_id_id=obj['stop_paragraph_id__id'],
                parent_clause_id=obj['parent_clause__id'],
                level=obj['level'],
            )
        )
    DocumentClause.objects.bulk_create(Create_List)