import re
from doc.models import Rahbari, Document, RahbariType, RahbariTypeKeyword, RahbariDocumentKeywords, RahbariDocumentType
import after_response
from elasticsearch import Elasticsearch
from abdal import es_config
from django.db.models import Sum

TITLE_SCORE = 10
TEXT_SCORE = 1
es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)
bucket_size = es_config.BUCKET_SIZE
search_result_size = es_config.SEARCH_RESULT_SIZE

def standardIndexName(Country,model_name):

    file_name = Country.file_name

    index_name = file_name.split('.')[0] + '_' + model_name
    index_name = index_name.replace(' ','_')
    index_name = index_name.replace(',','_')
    index_name = index_name.lower()

    return index_name

@after_response.enable
def apply(Country):
    RahbariType.objects.all().delete()
    RahbariTypeKeyword.objects.all().delete()
    RahbariDocumentKeywords.objects.all().delete()
    RahbariDocumentType.objects.all().delete()

    print("------------------------------------->", "insert_type_keyword_to_db")
    insert_type_keyword_to_db()
    print("------------------------------------->", "calculate_keyword_frequency")
    calculate_keyword_frequency(Country)
    print("------------------------------------->", "calculate_document_type")
    calculate_document_type()

    print("------------------------------------->", "Done ... ")


def insert_type_keyword_to_db():
    type1 = {"name": "دستوری، تکلیفی و امری",
            "keywords": ["باید", "نباید", "ضروری است", "واجب است", "به هیچ عنوان"]}

    type2 = {"name": "راهبردی، اهدافی، بلند مدت",
             "keywords": ["هدف", "سیاست", "برنامه", "راهبرد", "طرح", "بلند مدت", "غایت", "سیاست‌های کلی"]}

    type3 = {"name": "ارشادی، تجویزی و توصیه‌ای",
              "keywords": ["توصیه", "بهتر است", "پیشنهاد کرده‌ام", "پیشنهاد من این است", "پیشنهاد کردم"]}


    types = [type1, type2, type3]
    RahbariType.objects.create(id=-1, name="نامشخص")
    for type in types:
        rahbari_type = RahbariType.objects.create(name=type["name"])
        key_list = type["keywords"]
        for keyword in key_list:
            RahbariTypeKeyword.objects.create(keyword=keyword, type=rahbari_type)


def calculate_keyword_frequency(Country):
    rahbari_type_list = RahbariType.objects.all()
    for rahbari_type in rahbari_type_list:
        print("------", rahbari_type.name)
        keyword_list = RahbariTypeKeyword.objects.filter(type=rahbari_type)
        for keyword in keyword_list:
            print("*****", keyword.keyword)
            keyword_text = keyword.keyword
            index_name = standardIndexName(Country, Document.__name__)
            result_field = ['document_id']

            res_query = {
                "bool": {
                    "should": []
                }
            }

            title_query = {
                "multi_match": {
                    "query": keyword_text,
                    "type": "phrase",
                    "fields": ["name"],
                    "boost": TITLE_SCORE
                }
            }
            res_query['bool']['should'].append(title_query)

            word_query = {
                "multi_match": {
                    "query": keyword_text,
                    "type": "phrase",
                    "fields": ["attachment.content"],
                    "boost": TEXT_SCORE
                }
            }
            res_query['bool']['should'].append(word_query)

            response = client.search(index=index_name,
                                     _source_includes=result_field,
                                     request_timeout=40,
                                     query=res_query,
                                     size=5000,
                                     highlight={
                                         "order": "score",
                                         "fields": {
                                             "attachment.content":
                                                 {"pre_tags": ["<em>"],
                                                  "post_tags": ["</em>"],
                                                  "number_of_fragments": 0
                                                  },
                                         "name":
                                                 {"pre_tags": ["<em>"],
                                                  "post_tags": ["</em>"],
                                                  "number_of_fragments": 0
                                                 },
                                         }
                                     }
                                     )
            result = response['hits']['hits']
            for row in result:
                document_id = row["_source"]["document_id"]
                title_count = 0
                if "name" in row["highlight"]:
                    title_count = 1

                text_count = 0
                if "attachment.content" in row["highlight"]:
                    text_count = row["highlight"]["attachment.content"][0].count("<em>")

                RahbariDocumentKeywords.objects.create(document_id=document_id, keyword=keyword, type=rahbari_type,
                                                       title_count=title_count, text_count=text_count)

def normalize_json(data, field_name):
    sum_val = 0
    for row in data:
        sum_val += row[field_name]

    for i in range(data.__len__()):
        data[i][field_name] = round(data[i][field_name] / sum_val, 3)

    return data

def calculate_document_type():
    rahbari_documents = Rahbari.objects.all()
    type_id_list = RahbariType.objects.all().values_list("id", flat=True)
    b = 0
    for doc in rahbari_documents:
        print(b, b/rahbari_documents.__len__())
        b+=1
        document_id = doc.document_id.id
        val = RahbariDocumentKeywords.objects.filter(document_id=document_id) \
            .values('type_id').annotate(score=(Sum('title_count') * TITLE_SCORE)+(Sum('text_count') * TEXT_SCORE))

        val = normalize_json(val, "score")

        max_type = None
        max_score = 0

        for type_id in type_id_list:
            row = list(filter(lambda x: x["type_id"] == type_id, val))
            score = 0
            if row.__len__() > 0:
                score = row[0]["score"]

            RahbariDocumentType.objects.create(document_id=document_id, type_id=type_id, score=score)

            if score > max_score:
                max_type = type_id
                max_score = score

        Rahbari.objects.filter(document_id_id=document_id).update(rahbari_type_id=max_type)


