import pytest
import requests
from django.urls import reverse

BASE_URL = "http://127.0.0.1:8000"


def test_graph_to_information():
    country_id = "1"
    measure_id = "2"
    minimum_weight = "20"
    my_url = BASE_URL + "/GetGraphNodesEdges/" + country_id + "/" + measure_id + "/" + minimum_weight + "/"
    req = requests.request("GET", my_url)
    assert req.status_code == 200

    Nodes_data = req.json()["Nodes_data"]
    Edges_data = req.json()["Edges_data"]


    node_sample_id = Nodes_data[0]["id"]
    node_sample_name = Nodes_data[0]["name"]

    my_url = BASE_URL + "/GetDocumentById/" + node_sample_id + "/"
    req = requests.request("GET", my_url)
    assert req.status_code == 200
    assert node_sample_name == req.json()["document_information"][0]["name"]
    assert get_document_information(node_sample_id)
    
    edge_id = Edges_data[0]["source"] + "__" + Edges_data[0]["target"]
    my_url = BASE_URL + "/comparison?id=" + edge_id
    req = requests.request("GET", my_url)
    assert req.status_code == 200


def test_subject_graph():
    my_url = BASE_URL + "/GetSubjectKeywordGraphVersion/"
    req = requests.request("GET", my_url)
    assert req.status_code == 200
    version_id = req.json()["Versions"][0][0]
    my_url = BASE_URL + "/SubjectKeywordGraphExtractor/" + str(version_id) + "/"
    req = requests.request("GET", my_url)
    assert req.status_code == 200
    Nodes_data = req.json()["Nodes_data"]

    node_sample_id = Nodes_data[0]["id"]
    node_sample_name = Nodes_data[0]["name"]

    if node_sample_id[0] == "S":
        my_url = BASE_URL + "/GetSubjectDocumentParagraphListBySubjectId/" + node_sample_id[1:] + "/" + "localhost/"
        req = requests.request("GET", my_url)
        assert req.status_code == 200
    else:
        my_url = BASE_URL + "/GetSubjectsListByKeywordId/" + version_id + "/" + node_sample_name + "/"
        req = requests.request("GET", my_url)
        assert req.status_code == 200


def get_document_information(document_id):
   all_response_200 = True

   my_url = BASE_URL + "/GetDocumentById/" + document_id + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False


   my_url = BASE_URL + "/GetPersianDefinitionByDocumentId/" + document_id + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False

   my_url = BASE_URL + "/GetGeneralDefinition/" + document_id + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False

   my_url = BASE_URL + "/GetTFIDFByDocumentId/" + document_id + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False

   my_url = BASE_URL + "/GetNGramByDocumentId/" + document_id + "/" + "2" + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False

   my_url = BASE_URL + "/GetNGramByDocumentId/" + document_id + "/" + "3" + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False

   my_url = BASE_URL + "/GetActorsPararaphsByDocumentId/" + document_id + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False


   return all_response_200
