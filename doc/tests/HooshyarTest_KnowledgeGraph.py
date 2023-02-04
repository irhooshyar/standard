from django.test import TestCase
import requests

class KnowledgeGraphTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"
    def test_GetAllKnowledgeGraphList(self):
        username = "test_user"
        my_url = self.base_url + "/GetAllKnowledgeGraphList/" + username + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        knowledge_graph_list = req.json()["knowledge_graph_list"]
        self.assertGreater(knowledge_graph_list.__len__(), 0)

    def test_GetKnowledgeGraphData(self):
        username = "test_user"
        my_url = self.base_url + "/GetAllKnowledgeGraphList/" + username + "/"
        graph_id = requests.request("GET", my_url).json()["knowledge_graph_list"][0]["id"]
        my_url = self.base_url + "/GetKnowledgeGraphData/" + str(graph_id) + "/"
        graph_data_req = requests.request("GET", my_url)
        self.assertTrue(graph_data_req.ok)
        self.assertIn("Nodes_data", graph_data_req.json())
        self.assertIn("Edges_data", graph_data_req.json())
        self.assertGreater(graph_data_req.json()["Nodes_data"].__len__(), 0)
        self.assertGreater(graph_data_req.json()["Edges_data"].__len__(), 0)

    def test_SaveKnowledgeGraph(self):
        username = "test_user"
        graph_name = "test_graph"
        my_url = self.base_url + "/SaveKnowledgeGraph/" + graph_name + "/" + username + "/0/"
        nodes_data = ",".join(["1", "تست1", "test1", "3", "2", "تست2", "test2", "6",
                               "3", "تست3", "test3", "8", "4", "تست4", "test4", "2"])
        edges_data = ",".join(["1", "تست1", "test1", "2", "تست2", "test2", "8",
                               "3", "تست3", "test3", "4", "تست4", "test4", "9"])
        form_data = {"nodes_data": nodes_data, "edges_data": edges_data}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("version_id", req.json())
        self.assertGreaterEqual(req.json()["version_id"], 1)

    # def test_DeleteKnowledgeGraph(self):
    #     username = "test_user"
    #     my_url = self.base_url + "/GetAllKnowledgeGraphList/" + username + "/"
    #     graph_id = requests.request("GET", my_url).json()["knowledge_graph_list"][0]["id"]
    #     my_url = self.base_url + "/DeleteKnowledgeGraph/" + str(graph_id) + "/"
    #     req = requests.request("GET", my_url)
    #     self.assertTrue(req.ok)

    def test_BoostingSearchKnowledgeGraph_ES_AND_IRI(self):
        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "IRI"
        search_type = "AND"
        my_url = self.base_url + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "signature", "5", "دیجیتال", "digital", "7"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)

    def test_BoostingSearchKnowledgeGraph_ES_OR_IRI(self):
        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "IRI"
        search_type = "OR"
        my_url = self.base_url + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "signature", "5", "دیجیتال", "digital", "7"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)

    def test_BoostingSearchKnowledgeGraph_ES_ANDDOC_IRI(self):
        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "IRI"
        search_type = "AND_DOC"
        my_url = self.base_url + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "signature", "5", "دیجیتال", "digital", "7"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)

    def test_BoostingSearchKnowledgeGraph_ES_AND_UK(self):
        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "UK"
        search_type = "AND"
        my_url = self.base_url + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "signature", "5", "دیجیتال", "digital", "7"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)

    def test_BoostingSearchKnowledgeGraph_ES_OR_UK(self):
        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "UK"
        search_type = "OR"
        my_url = self.base_url + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "signature", "5", "دیجیتال", "digital", "7"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)

    def test_BoostingSearchKnowledgeGraph_ES_ANDDOC_UK(self):
        country_id = "1"
        filed_name = "0"
        field_value = "0"
        language = "UK"
        search_type = "AND_DOC"
        my_url = self.base_url + "/BoostingSearchKnowledgeGraph_ES/" + country_id + "/" + filed_name + "/" + \
                 field_value + "/" + language + "/" + search_type + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "signature", "5", "دیجیتال", "digital", "7"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)
