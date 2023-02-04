from operator import itemgetter
from doc.models import ParagraphsSubject, SubjectList, SubjectKeywordsList, SubjectsVersion, SubjectSubjectGraphCube
from doc.models import DocumentParagraphs
import heapq
import time
from elasticsearch import Elasticsearch
from abdal import es_config
import after_response
import math
from scripts.Persian.Preprocessing import standardIndexName

es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)

def NormalizeDocumentScore(Score_Dict):
    sum_value = sum([value for key, value in Score_Dict.items()])
    factor = 1/sum_value if sum_value > 0 else 0
    result_dict = {}
    for key, value in Score_Dict.items():
        result_dict[key] = round(Score_Dict[key] * factor, 3)

    return result_dict


@after_response.enable
def apply(folder_name, Country):
    Country.status = "Docs_Subject_Extractor"
    Country.save()

    t = time.time()

    Version = SubjectsVersion.objects.get(id=12)

    ParagraphsSubject.objects.filter(country=Country,
                                     version=Version).delete()

    paragraphs_score = {}
    paragraphs_keyword = {}
    paragraphs_document = {}
    subject_list = SubjectList.objects.filter(version=Version)

    i = 1
    for subject in subject_list:
        subject_keywords_list = SubjectKeywordsList.objects.filter(subject=subject)
        for keyword in subject_keywords_list:
            print(i)
            i+=1
            content_query = {"match_phrase": {"attachment.content": keyword.word}}
            
            model_name = DocumentParagraphs.__name__
            index_name = standardIndexName(Country, model_name)
            index_name = index_name + "_graph"

            query_size = 200000 if Country.id == 1 else 5000

            response = client.search(index=index_name,
                                     _source_includes=['paragraph_id', 'document_id', 'type_name'],
                                     request_timeout=40,
                                     query=content_query,
                                     size=query_size
                                     )
            result = response['hits']['hits']
            for row in result:
                paragraph_id = row['_source']['paragraph_id']
                document_id = row['_source']['document_id']
                type_name = row['_source']['type_name']

            # if type_name == "قانون":
                paragraphs_document[paragraph_id] = document_id
                if paragraph_id not in paragraphs_score:
                    paragraphs_score[paragraph_id] = {subject.id: keyword.score}
                    paragraphs_keyword[paragraph_id] = {subject.id: {keyword.word: keyword.score}}
                else:
                    if subject.id not in paragraphs_score[paragraph_id]:
                        paragraphs_score[paragraph_id][subject.id] = keyword.score
                        paragraphs_keyword[paragraph_id][subject.id] = {keyword.word: keyword.score}
                    else:
                        paragraphs_score[paragraph_id][subject.id] += keyword.score
                        paragraphs_keyword[paragraph_id][subject.id][keyword.word] = keyword.score

    Result_Create_List = []
    a = 1
    for paragraph, subject_score in paragraphs_score.items():
        print(a/paragraphs_score.keys().__len__())
        a+=1
        normalized_subject_score = NormalizeDocumentScore(subject_score)
        topitems = heapq.nlargest(3, normalized_subject_score.items(), key=itemgetter(1))
        res = []
        for subject_id, score in dict(topitems).items():
            res.append([subject_id, score])

        document_id = paragraphs_document[paragraph]

        subject1 = SubjectList.objects.get(id=res[0][0])
        subject1_score = res[0][1]
        subject1_name = subject1.name
        subject1_keywords = paragraphs_keyword[paragraph][res[0][0]]


        subject2 = None if res.__len__() <= 1 else SubjectList.objects.get(id=res[1][0])
        subject2_score = None if res.__len__() <= 1 else res[1][1]
        subject2_name = None if res.__len__() <= 1 else subject2.name
        subject2_keywords = None if res.__len__() <= 1 else paragraphs_keyword[paragraph][res[1][0]]


        subject3 = None if res.__len__() <= 2 else SubjectList.objects.get(id=res[2][0])
        subject3_score = None if res.__len__() <= 2 else res[2][1]
        subject3_name = None if res.__len__() <= 2 else subject3.name
        subject3_keywords = None if res.__len__() <= 2 else paragraphs_keyword[paragraph][res[2][0]]

        Object = ParagraphsSubject(country=Country,
                                     paragraph_id=paragraph,
                                     document_id=document_id,
                                     version=Version,

                                     subject1=subject1,
                                     subject1_score=subject1_score,
                                     subject1_name=subject1_name,
                                     subject1_keywords=subject1_keywords,

                                     subject2=subject2,
                                     subject2_score=subject2_score,
                                     subject2_name=subject2_name,
                                     subject2_keywords=subject2_keywords,

                                     subject3=subject3,
                                     subject3_score=subject3_score,
                                     subject3_name=subject3_name,
                                     subject3_keywords=subject3_keywords
                                         )

        Result_Create_List.append(Object)

    batch_size = 10000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        ParagraphsSubject.objects.bulk_create(sub_list)

    Country.status = "Subject Subject Graph"
    Country.save()

    GetSubjectSubjectGraphData(Country.id, Version.id)

    Country.status = "Done"
    Country.save()

    print("time ", time.time() - t)



def GetSubjectSubjectGraphData(country_id, version_id):
    SubjectSubjectGraphCube.objects.filter(country_id=country_id, version_id=version_id).delete()

    Nodes_List = []
    Subject_Node_List = SubjectList.objects.filter(version_id=version_id)
    for Subject in Subject_Node_List:
        node = {"id": str(Subject.id),
                "name": Subject.name,
                "type": "rect", "size": 30,
                "style": {"fill": "#5C5CD5"}}
        Nodes_List.append(node)

    Edge_Dict = {}
    paragraph_List = ParagraphsSubject.objects.filter(country_id=country_id, version_id=version_id, document__type_id=2)
    b = 1
    for paragraph in paragraph_List:
        print(b/paragraph_List.__len__())
        b+=1

        subject1 = paragraph.subject1
        subject2 = paragraph.subject2
        subject3 = paragraph.subject3

        if subject2 != None:
            edge = "_".join(sorted([str(subject1.id), str(subject2.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

        if subject3 != None:
            edge = "_".join(sorted([str(subject1.id), str(subject3.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

            edge = "_".join(sorted([str(subject2.id), str(subject3.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

        if subject2 == None and subject3 == None:
            edge = "_".join(sorted([str(subject1.id), str(subject1.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

    Edge_List = []
    for key, count in Edge_Dict.items():
        src_id = str(key.split("_")[0])
        src_name = SubjectList.objects.get(version_id=version_id, id=src_id).name
        target_id = str(key.split("_")[1])
        target_name = SubjectList.objects.get(version_id=version_id, id=target_id).name

        edge_obj = {"source": src_id, "source_name": src_name,
                    "target": target_id, "target_name": target_name, "weight": count}

        if src_id == target_id:
            edge_obj["type"] = "loop"

        Edge_List.append(edge_obj)

    SubjectSubjectGraphCube.objects.create(country_id=country_id, version_id=version_id, nodes_data=Nodes_List,
                                           edges_data=Edge_List)








