from doc.models import Document, DocumentParagraphs, ReferencesParagraphs, Graph, Measure
from elasticsearch import Elasticsearch
import math
from abdal import es_config
es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)

def standardIndexName(Country,model_name):

    file_name = Country.file_name

    index_name = file_name.split('.')[0] + '_' + model_name
    index_name = index_name.replace(' ','_')
    index_name = index_name.replace(',','_')
    index_name = index_name.lower()

    return index_name


def apply(folder_name, Country):
    ReferencesParagraphs.objects.filter(document_id__country_id=Country).delete()
    Graph.objects.filter(src_document_id__country_id=Country).delete()

    Document_List = Document.objects.filter(country_id=Country)

    ReferencesCreateList = []
    GraphDict = {}
    for doc in Document_List:

        doc_id = doc.id
        doc_name = doc.name

        content_query = {"match_phrase": {"attachment.content": doc_name}}

        index_name = standardIndexName(Country, DocumentParagraphs.__name__) + "_graph"

        response = client.search(index=index_name,
                                 _source_includes=['document_id', 'paragraph_id'],
                                 request_timeout=40,
                                 query=content_query,
                                 size=5000
                                 )
        result = response['hits']['hits']

        for row in result:
            ref_doc_id = row['_source']['document_id']
            ref_paragraph_id = row['_source']['paragraph_id']

            References_Object = ReferencesParagraphs(document_id_id=ref_doc_id, paragraph_id_id=ref_paragraph_id)
            ReferencesCreateList.append(References_Object)

            key = str(ref_doc_id) + "_" + str(doc_id)
            if key not in GraphDict:
                GraphDict[key] = 1
            else:
                GraphDict[key] += 1

    batch_size = 20000
    slice_count = math.ceil(ReferencesCreateList.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, ReferencesCreateList.__len__())
        sub_list = ReferencesCreateList[start_idx:end_idx]
        ReferencesParagraphs.objects.bulk_create(sub_list)

    GraphCreateList = []
    measure = Measure.objects.get(english_name="ReferenceSimilarity")
    for key, value in GraphDict.items():
        source, destination = key.split("_")
        Graph_Object = Graph(src_document_id_id=source, dest_document_id_id=destination, weight=value, measure_id=measure)
        GraphCreateList.append(Graph_Object)

    slice_count = math.ceil(GraphCreateList.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, GraphCreateList.__len__())
        sub_list = GraphCreateList[start_idx:end_idx]
        Graph.objects.bulk_create(sub_list)

