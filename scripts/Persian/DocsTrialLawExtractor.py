from doc.models import Document, TrialLaw, TrialLawType
from elasticsearch import Elasticsearch
from abdal import es_config

es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)

def standardIndexName(Country, model_name):
    file_name = Country.file_name
    index_name = file_name.split('.')[0] + '_' + model_name
    index_name = index_name.replace(' ', '_')
    index_name = index_name.replace(',', '_')
    index_name = index_name.lower()
    return index_name


def apply(Country):
    TrialLaw.objects.filter(country=Country).delete()

    phrase_list = {
        "اجرا": ["اجرای آزمایشی", "قانون اجرای آزمایشی"],
        "تمدید": ["استمرار اجرای آزمایشی", "تمدید مهلت اجرای آزمایشی", "تمدید مدت اجرای آزمایشی",
                  "قانون استمرار اجرای آزمایشی", "قانون تمدید مهلت اجرای آزمایشی", "قانون تمدید مدت اجرای آزمایشی"],
        "دائمی شدن": ["دائمی شدن", "قانون دائمی شدن"]
    }

    # Add Type in Table
    for type_name, phrase in phrase_list.items():
        type_count = TrialLawType.objects.filter(name=type_name).count()
        if type_count == 0:
            TrialLawType.objects.create(name=type_name)

    # Main Code For Trial Law
    added_doc = []
    for type_name, phrase_list in phrase_list.items():
        trial_type = TrialLawType.objects.get(name=type_name)
        for phrase in phrase_list:
            content_query = {"match_phrase_prefix": {"name": phrase}}
            index_name = es_config.DOTIC_DOC_INDEX
            response = client.search(index=index_name,
                                     _source_includes=['document_id', 'name', 'approval_year',
                                                       'approval_date', 'approval_reference_name'],
                                     request_timeout=40,
                                     query=content_query,
                                     highlight={
                                         "order": "score",
                                         "fields": {
                                             "name":
                                                 {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                                  "number_of_fragments": 0
                                                  }
                                         }},
                                     size=5000
                                     )

            result = response['hits']['hits']

            for row in result:
                doc_id = row['_source']['document_id']
                doc_name = row["_source"]["name"]
                doc_approval_ref = row["_source"]["approval_reference_name"]
                doc_approval_date = row["_source"]["approval_date"]
                doc_approval_year = row["_source"]["approval_year"]
                doc_name_highlighted = row["highlight"]["name"][0]

                if doc_id not in added_doc and doc_name_highlighted.index("<em>") == 0:

                    main_document_name1 = doc_name_highlighted.split("</em>")[-1][1:]
                    main_doc_name = main_document_name1
                    main_document_name2 = None
                    if "مصوب" in main_document_name1:
                        mosavab_index = main_document_name1.index("مصوب")
                        main_document_name2 = main_document_name1[:mosavab_index-1]

                    main_doc_id = search_affected_name_ES(main_document_name1)

                    if main_doc_id is None and main_document_name2 is not None:
                        main_doc_name = main_document_name2
                        main_doc_id = search_affected_name_ES(main_document_name2)

                    in_dotic = 0
                    main_doc_approval_ref, main_doc_approval_date, main_doc_approval_year = "نامشخص", "نامشخص", "نامشخص"
                    if main_doc_id is not None:
                        main_doc = Document.objects.get(id=main_doc_id)
                        main_doc_name = main_doc.name
                        in_dotic = 1
                        main_doc_approval_ref = main_doc.approval_reference_name
                        main_doc_approval_date = "نامشخص" if main_doc.approval_date is None else main_doc.approval_date
                        main_doc_approval_year = "نامشخص" if main_doc.approval_date is None else main_doc.approval_date[:4]

                    TrialLaw.objects.create(country=Country, document_id=doc_id, document_name=doc_name,
                                            document_approval_references= doc_approval_ref,
                                            document_approval_date=doc_approval_date,
                                            document_approval_year=doc_approval_year,
                                            main_document_id=main_doc_id, main_document_name=main_doc_name,
                                            main_document_approval_references=main_doc_approval_ref,
                                            main_document_approval_date=main_doc_approval_date,
                                            main_document_approval_year=main_doc_approval_year,
                                            in_dotic=in_dotic,
                                            type=trial_type)

                    added_doc.append(doc_id)

def mlt_query_search(affected_doc_name, index_name):
    result_doc_id = None

    like_query = {
        "more_like_this": {
            "analyzer": "persian_custom_analyzer",
            "fields": ["name"],
            "like": affected_doc_name,
            "min_term_freq": 1,
            "max_query_terms": 200,
            "min_doc_freq": 1,
            "max_doc_freq": 150000,
            "min_word_length": 2,
            "minimum_should_match": "75%"
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['name'],
                             request_timeout=40,
                             query=like_query,
                             size=1
                             )

    if len(response['hits']['hits']) > 0:
        result_doc_id = response['hits']['hits'][0]['_id']
        result_doc_name = response['hits']['hits'][0]['_source']['name']

        res_doc_name_chars_count = len(result_doc_name.replace(' ', ''))
        affected_doc_name_chars_count = len(affected_doc_name.replace(' ', ''))

        diff_chars_count = abs(res_doc_name_chars_count - affected_doc_name_chars_count)
        if diff_chars_count > 2:
            result_doc_id = None

    return result_doc_id

def match_phrase_query(affected_doc_name, index_name):
    result_doc_id = None
    res_query = {
        "match_phrase": {
            "name": affected_doc_name
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name'],
                             request_timeout=40,
                             query=res_query,
                             size=1
                             )

    if len(response['hits']['hits']) > 0:
        result_doc_id = response['hits']['hits'][0]['_id']
        result_doc_name = response['hits']['hits'][0]['_source']['name']

        res_doc_name_chars_count = len(result_doc_name.replace(' ', ''))
        affected_doc_name_chars_count = len(affected_doc_name.replace(' ', ''))

        diff_chars_count = abs(res_doc_name_chars_count - affected_doc_name_chars_count)
        if diff_chars_count > 2:
            result_doc_id = None

    return result_doc_id

def term_query_search(affected_doc_name, index_name):
    result_doc_id = None

    name_term_query = {
        "term": {
            "name.keyword": affected_doc_name
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name'],
                             request_timeout=40,
                             query=name_term_query,
                             size=1
                             )

    if len(response['hits']['hits']) > 0:
        result_doc_id = response['hits']['hits'][0]['_id']
        result_doc_name = response['hits']['hits'][0]['_source']['name']

    return result_doc_id

def search_affected_name_ES(affected_doc_name):
    result_doc_id = None

    index_name = es_config.DOTIC_DOC_INDEX

    # ############### 1. Term Query ###############################

    result_doc_id = term_query_search(affected_doc_name, index_name)

    # ############### 2. Match Query ###############################

    if result_doc_id == None:
        result_doc_id = match_phrase_query(affected_doc_name, index_name)

    # ############### 3. MLT Query ###############################

    if result_doc_id == None:
        result_doc_id = mlt_query_search(affected_doc_name, index_name)

    return result_doc_id