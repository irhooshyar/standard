from doc.models import  Document, CUBE_DocumentJsonList, DocumentActor
from django.db.models import  F

def GetActorsByDocumentIdActorType(document_id, actor_type_name):
    actor_dict = {}

    document_actors = DocumentActor.objects.filter(document_id_id=document_id,
                                                   actor_type_id__name=actor_type_name).annotate(
        actor_name=F('actor_id__name')).values('actor_name')

    # fill actor dict
    for actor in document_actors:
        actor_name = actor['actor_name']

        if actor_name not in actor_dict:
            actor_dict[actor_name] = 1
        else:
            actor_dict[actor_name] += 1

    return actor_dict


def apply(folder_name, Country):
    Document.objects.filter(country_id=Country).update(json_text=None)

    doc_list = Document.objects.filter(country_id=Country)
    i = 0
    for document in doc_list:

        print(i/doc_list.__len__())
        i +=1

        document_actors = {}

        motevalian_dict = GetActorsByDocumentIdActorType(document.id, 'متولی اجرا')
        hamkaran_dict = GetActorsByDocumentIdActorType(document.id, 'همکار')
        salahiat_dict = GetActorsByDocumentIdActorType(document.id, 'دارای صلاحیت اختیاری')

        document_actors['motevalian'] = motevalian_dict
        document_actors['hamkaran'] = hamkaran_dict
        document_actors['salahiat'] = salahiat_dict

        approval_ref = "نامشخص"
        if document.approval_reference_id != None:
            approval_ref = document.approval_reference_name

        approval_date = "نامشخص"
        approval_year = "نامشخص"
        if document.approval_date != None:
            approval_date = document.approval_date
            approval_year = approval_date[0:4]

        communicated_date = "نامشخص"
        if document.communicated_date != None:
            communicated_date = document.communicated_date

        type_name = "سایر"
        if document.type_id != None:
            type_name = document.type_name

        level_name = "نامشخص"
        if document.level_id != None:
            level_name = document.level_name

        subject_name = "نامشخص"
        if document.subject_id != None:
            subject_name = document.subject_name

        result = {"id": document.id,
                  "name": document.name,
                  "country_id": document.country_id_id,
                  "country": document.country_id.name,
                  "level_id": document.level_id_id,
                  "level": level_name,
                  "subject_id": document.subject_id_id,
                  "subject": subject_name,
                  "type_id": document.type_id_id,
                  "type": type_name,
                  "approval_reference_id": document.approval_reference_id_id,
                  "approval_reference": approval_ref,
                  "approval_date": approval_date,
                  "approval_year": approval_year,
                  "communicated_date": communicated_date,
                  "word_count": document.word_count,
                  "distinct_word_count": document.distinct_word_count,
                  "stopword_count": document.stopword_count
                  }

        Document.objects.filter(id=document.id).update(json_text=result)




