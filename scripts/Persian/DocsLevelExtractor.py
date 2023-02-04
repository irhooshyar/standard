import time

from doc.models import Document, Level, ApprovalReference, Type, DocumentParagraphs
from django.db.models import Max

def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "", "": ""}
    for key,value in arabic_char.items():
        text = text.replace(key, value)

    return text

level_list = [
    "اسناد بالادستی",
    "قانون",
    "مقررات",
]
level_list_id = []


level_1_approval_reference = "شورای عالی"
level_2_approval_reference = ["مصوبات مجلس شورا", "مجلس شورای اسلامی"]
level_3_approval_reference = ["مصوبات هیات وزیران", "کمیسیون تنظیم مقررات"]

level_3_type = [
    "شیوه نامه",
    "بخش نامه",
    "دستورالعمل",
    "آيين‌نامه",
]

level_1_name_include = [
    "قانون اساسی",
    "رهبری",
]


def apply(folder_name, Country):

    t = time.time()


    Document.objects.filter(country_id=Country).update(level_id_id=None)

    for level_name in level_list:
        level_list_id.append(Level.objects.get(name=level_name).id)

    Document.objects.exclude(level_id_id=None).filter(country_id=Country).update(level_id_id=None)

    #  ----------------   detect by ApprovalReference   ------------------- #
                        #  -------   level 2   -------- #
    level_2_approval_reference_id = ApprovalReference.objects.filter(name__in=level_2_approval_reference)
    Document.objects.filter(approval_reference_id__in=level_2_approval_reference_id, country_id=Country)\
        .update(level_id_id=level_list_id[1], level_name=level_list[1])

                        #  -------   level 3   -------- #
    level_3_approval_reference_id = []
    appr_level_3 = ApprovalReference.objects.filter(name=level_3_approval_reference[0])
    if appr_level_3.count() > 0:
        level_3_approval_reference_id.append(ApprovalReference.objects.get(name=level_3_approval_reference[0]).id)
        level_3_approval_reference_id += \
            [x.id for x in ApprovalReference.objects.filter(name__icontains=level_3_approval_reference[1])]
    Document.objects.filter(approval_reference_id_id__in=level_3_approval_reference_id,level_id_id=None,country_id=Country)\
        .update(level_id_id=level_list_id[2], level_name=level_list[2])
                        #  -------   level 1   -------- #
    level_1_approval_reference_id = \
        [x.id for x in ApprovalReference.objects.filter(name__icontains=level_1_approval_reference)]
    Document.objects.filter(approval_reference_id_id__in=level_1_approval_reference_id,level_id_id=None,country_id=Country)\
        .update(level_id_id=level_list_id[0], level_name=level_list[0])

    #  ----------------   detect by type   ------------------- #
                        #  -------   level 3   -------- #

    # type based
    level_3_type_id = [x.id for x in Type.objects.filter(name__in=level_3_type)]
    Document.objects.filter(type_id_id__in=level_3_type_id,level_id_id=None,country_id=Country)\
        .update(level_id_id=level_list_id[2], level_name=level_list[2])


    # title based
    for word in level_3_type:
        doc_list = Document.objects.filter(level_id_id=None, country_id=Country)
        for doc in doc_list:
            if Local_preprocessing(word) in Local_preprocessing(doc.name):
                Document.objects.filter(id=doc.id).update(level_id_id=level_list_id[2], level_name=level_list[2])

    # text based - 2 last paragraph
    for word in level_3_type:
        doc_list = Document.objects.filter(level_id_id=None, country_id=Country)
        docs_max_paragraph = DocumentParagraphs.objects.filter(document_id__in=doc_list).values("document_id_id").annotate(max_number=Max("number"))
        for doc in docs_max_paragraph:
            doc_id = doc["document_id_id"]
            max_number = doc["max_number"] - 2
            paragraph_list = DocumentParagraphs.objects.filter(document_id_id=doc_id, number__gte=max_number, text__icontains=word)
            if paragraph_list.count() > 0:
                Document.objects.filter(id=doc_id).update(level_id_id=level_list_id[2], level_name=level_list[2])

    #  ----------------   detect by name   ------------------- #
                        #  -------   level 1   -------- #
    for name in level_1_name_include:
        Document.objects.filter(name__icontains=name,level_id_id=None,country_id=Country)\
            .update(level_id_id=level_list_id[0], level_name=level_list[0])

    print("time ", time.time() - t)
