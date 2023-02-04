import re

from doc.models import Document, DocumentRegulator, CUBE_RegularityLifeCycle_TableData
import time


def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)

    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_name

    approval_date = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date

    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_name

    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_name

    type_name = "نامشخص"
    if document.type_id != None:
        type_name = document.type_name

    result = {
        "subject_id": document.subject_id_id,
        "subject": subject_name,
        "approval_reference_id": document.approval_reference_id_id,
        "approval_reference": approval_ref,
        "approval_date": approval_date,
        "level": level_name,
        "level_id": document.level_id_id,
        "type_id": document.type_id_id,
        "type": type_name,
        "name": document.name,
        "id": document.id,
        "country": document.country_id.name
    }
    return result


def apply(folder_name, Country, host_url):
    create_TableData_CUBE(Country, host_url)


def create_TableData_CUBE(Country, host_url):
    start_t = time.time()

    batch_size = 10000

    CUBE_RegularityLifeCycle_TableData.objects.filter(country_id=Country).delete()

    added = []

    # Filter by keywords
    keywords_list = ['صدور',
                     'تمدید',
                     'اصلاح',
                     'لغو',
                     'ابطال',
                     'تعلیق',
                     'کاهش مدت اعتبار',
                     'انتقال']

    Result_DocumentRegulator = []

    for word in keywords_list:

        doc_paragraphs = DocumentRegulator.objects.filter(document_id__country_id=Country,
                                                          paragraph_id__text__icontains=word)

        for res in doc_paragraphs:
            if res.id in added:
                continue
            para = DocumentRegulator.objects.get(id=res.id).paragraph_id.text
            # and_ = 'و'
            # or_ = 'یا'
            # comma_ = '،'
            # pattern = re.compile(rf"{word}({'|'.join(keywords_list)}|\s|/|{and_}|{or_}|{comma_})*{res.tool_id.name}")
            # if pattern.search(para) is None:
            #     continue
            added.append(res.id)
            json_data = {'document_regulator_id': res.id}
            # index = 0
            # json_data['highlights'] = []
            # reg = pattern.search(para, index)
            # while reg is not None:
            #     json_data['highlights'].append(reg.span())
            #     reg = pattern.search(para, reg.span()[1])
            #     # if res.document_id.id == 4:
            #     #     print(json_data['highlights'])
            obj = CUBE_RegularityLifeCycle_TableData(country_id=Country, tool_id=res.tool_id,
                                                     document_id=res.document_id,
                                                     regularity_life_cycle=word, table_data=json_data)
            Result_DocumentRegulator.append(obj)
            if len(Result_DocumentRegulator) > batch_size:
                CUBE_RegularityLifeCycle_TableData.objects.bulk_create(Result_DocumentRegulator)
                Result_DocumentRegulator = []

    CUBE_RegularityLifeCycle_TableData.objects.bulk_create(Result_DocumentRegulator)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ')')
