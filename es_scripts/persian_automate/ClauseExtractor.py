import time
from num2fawords import words, ordinal_words, HUNDREDS
from doc.models import DocumentCompleteParagraphs, DocumentClause, DocumentParagraphs
from es_scripts.util.search import search_size_all
from abdal import es_config
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from scripts.Persian.Preprocessing import standardIndexName
from es_scripts.util import clause_type, clause_number, clause_number_names, clause_number_all

es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)
bucket_size = es_config.BUCKET_SIZE
search_result_size = es_config.SEARCH_RESULT_SIZE




def create_clause_patterns():
    patterns = []
    for c_type in clause_type:
        for c_number_key, c_number_value in clause_number.items():
            if len(c_number_value) == 0:
                continue
            patterns.append((c_type, c_number_key, c_number_value))
    for c_number_key, c_number_values in clause_number.items():
        for c_number_value in c_number_values:
            for index, clause_number_type in enumerate(clause_number_all):
                if c_number_value in clause_number_type.values():
                    patterns.append((clause_number_names[index], c_number_key, c_number_value))
    patterns += [(c_type, None, None) for c_type in clause_type]
    return patterns


def create_term(keyword):
    keyword = keyword.split(" ")
    if len(keyword) == 1:
        return {"span_term": {"attachment.content": keyword[0]}}
    else:
        return {"span_near": {"clauses": [
            {"span_term": {"attachment.content": item}} for item in keyword
        ], "slop": 0, "in_order": True}}


def create_query_from_clause_pattern(c_type=None, c_number_value=None):
    if isinstance(c_number_value, list):
        return \
            {
                "span_near": {
                    "clauses": [
                        {
                            "span_first": {
                                "match": {
                                    "span_term": {"attachment.content": c_type}
                                },
                                "end": 1
                            }
                        },
                        {
                            "span_or": {
                                "clauses": [
                                    create_term(c_number) for c_number in c_number_value
                                ]
                            }
                        }
                    ],
                    "slop": 0,
                    "in_order": True
                }
            }

    else:
        return \
            {
                "span_first": {
                    "match": create_term(c_type if c_number_value is None else c_number_value),
                    "end": 1
                }
            }


def search_for_patterns(index_name):
    found_paragraph_ids = set()
    patterns = create_clause_patterns()
    total_pattern_count = len(patterns)
    for index, pattern in enumerate(patterns):
        print(f"{round((index/total_pattern_count)*100, 2)}% ...")
        response = search_size_all(client,
                                   index=index_name,
                                   _source_includes=['paragraph_id'],
                                   request_timeout=100,
                                   query=create_query_from_clause_pattern(pattern[0], pattern[2]))
        paragraph_ids = set([item['_id'] for item in response['hits']['hits']])
        # print(create_query_from_clause_pattern(pattern[0], pattern[2]))
        paragraph_ids -= found_paragraph_ids
        if len(paragraph_ids) > 0:
            data = [
                {
                    "_op_type": 'update',
                    "_index": index_name,
                    "_id": _id,
                    "doc": {
                        "clause_type": pattern[0],
                        'clause_number': pattern[1] if pattern[1] is not None else 1
                    },
                    # "doc_as_upsert": True
                } for _id in paragraph_ids]
            helpers.bulk(client, data, index=index_name)
            client.indices.flush([index_name])
            client.indices.refresh([index_name])
            found_paragraph_ids = found_paragraph_ids.union(paragraph_ids)
    return len(found_paragraph_ids)


def apply(country):
    start_t = time.time()
    index_name = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    # docs_with_strict_clause_order = {
    #     'قانون بودجه': []
    # }
    res = search_for_patterns(index_name)
    end_t = time.time()
    print(f'{res} Clauses found. ({str(end_t - start_t)}).')
    return
