from doc.models import DocumentParagraphs
from es_scripts.util import clause_number, clause_type, clause_number_dict
from es_scripts.util.search import search_size_all
from elasticsearch import Elasticsearch
from abdal import es_config
from scripts.Persian.Preprocessing import standardIndexName


es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)


def _find_clause_number(numbers: list):
    for i in range(len(numbers), 0, -1):
        num = ' '.join(numbers[:i])
        for key, values in clause_number.items():
            if num in values:
                return key
    return 1


def get_document_paragraphs(doc_id: int, country, extra_source=None):
    default_source = ['paragraph_id', 'clause_number', 'clause_type']
    if extra_source is not None:
        default_source += extra_source
    query = {"term": {"document_id": {"value": doc_id}}}
    index_name = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    response = search_size_all(client, index=index_name,
                               _source_includes=default_source,
                               request_timeout=40,
                               query=query,
                               sort=[{'paragraph_id': {"order": "asc"}}],
                               )
    return response['hits']['hits']


def _sub_get_paragraphs_by_clause(paragraphs: list, _clause_type, _clause_number):
    start = -1
    end = len(paragraphs)
    found_type = False
    for index, paragraph in enumerate(paragraphs):
        if start == -1 and not found_type and \
                _clause_type not in ['ماده', 'تبصره'] and \
                paragraph['_source']['clause_type'] in clause_number_dict.keys():
            found_type = True
            _clause_type = paragraph['_source']['clause_type']
        if paragraph['_source']['clause_type'] == _clause_type and \
                paragraph['_source']['clause_number'] == _clause_number:
            start = index
        elif paragraph['_source']['clause_type'] == _clause_type and \
                paragraph['_source']['clause_number'] == _clause_number + 1:
            end = index
    if start == -1:
        # should remove this if later when complete paragraphs
        # are added to elastic paragraph index
        if clause_type == 'ماده' and clause_number == 1:
            return paragraphs
        return []
    return paragraphs[start:end]


# this function returns paragraph id for a relevant clause
def get_paragraphs_by_clause(clause: str, paragraphs: list, country):
    init_size = len(paragraphs)
    index_name = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    response = client.indices.analyze(
        body={
            "text": clause,
            "field": "attachment.content"
        },
        index=index_name
    )
    tokens = [item['token'] for item in response['tokens']]
    last_clause = len(tokens)
    for i in range(len(tokens) - 1, -1, -1):
        if tokens[i] not in clause_type:
            continue
        if i + 1 not in range(len(tokens)):
            num = 1
        else:
            num = _find_clause_number(tokens[i + 1:last_clause])
        # print("****")
        # print(tokens[i])
        # print(num)
        # print(f'old {len(paragraphs)}')
        paragraphs = _sub_get_paragraphs_by_clause(paragraphs[1:], tokens[i], num)
        # print(f'new {len(paragraphs)}')
        if len(paragraphs) == 0:
            # print("-----------")
            break
        last_clause = i
    if init_size == len(paragraphs):
        return []
    return paragraphs


# this function returns clause for a relevant paragraph id
def get_clause_by_paragraph(para_id: int, doc_id: int, country, detailed_clause_type=False):
    paragraphs = get_document_paragraphs(doc_id, country)
    clause_types = []
    clause_numbers = []
    for paragraph in paragraphs:
        if paragraph['_source']['clause_type'] == 'نامشخص':
            continue
        if paragraph['_source']['clause_type'] in clause_types:
            index = clause_types.index(paragraph['_source']['clause_type'])
            clause_types = clause_types[:index]
            clause_numbers = clause_numbers[:index]
        clause_types.append(paragraph['_source']['clause_type'])
        clause_numbers.append(paragraph['_source']['clause_number'])
        if paragraph['_source']['paragraph_id'] == para_id:
            break
    if not detailed_clause_type:
        extra_clause_type = ['بند', 'جز', 'ردیف', 'قسمت']
        counter = 0
        for index, clause in enumerate(clause_types):
            if clause not in clause_type:
                clause_numbers[index] = clause_number_dict[clause][clause_numbers[index]]
                clause_types[index] = extra_clause_type[counter]
                counter += 1
    return [(clause_types[index], clause_numbers[index]) for index in range(len(clause_types) - 1, -1, -1)]
