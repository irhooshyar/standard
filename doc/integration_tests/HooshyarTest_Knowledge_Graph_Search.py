import pytest
import requests
from django.urls import reverse

BASE_URL = "http://127.0.0.1:8000"


def test_knowledge_graph_to_search():
    username = "test_user"
    my_url = BASE_URL + "/GetAllKnowledgeGraphList/" + username + "/"
    req = requests.request("GET", my_url)
    assert req.status_code == 200
    knowledge_graph_list = req.json()["knowledge_graph_list"]

    if knowledge_graph_list.__len__() >= 0:
        graph_id = knowledge_graph_list[0]["id"]
        my_url = BASE_URL + "/GetKnowledgeGraphData/" + str(graph_id) + "/"
        req = requests.request("GET", my_url)
        assert req.status_code == 200

        Nodes_data = req.json()["Nodes_data"]

        node_sample_name = Nodes_data[0]["name"]
        node_sample_english_name = Nodes_data[0]["EN_name"]
        node_sample_weight = Nodes_data[0]["weight"]

        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "IRI"
        search_type = "AND"
        my_url = BASE_URL + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"

        form_data = {'cluser_keyword_data': [",".join([node_sample_name, node_sample_english_name, node_sample_weight])]}
        req = requests.post(my_url, data=form_data)

        assert req.status_code == 200


