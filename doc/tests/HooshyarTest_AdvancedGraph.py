from django.test import TestCase
import requests

class AdvancedGraphTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"
    def test_GetGraphNodesEdges(self):
        country_id = "1"
        measure_id = "2"
        minimum_weight = "20"
        my_url = self.base_url + "/GetGraphNodesEdges/" + country_id + "/" + measure_id + "/" + minimum_weight + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("Nodes_data", req.json())
        self.assertIn("Edges_data", req.json())
        self.assertGreater(req.json()["Nodes_data"].__len__(), 0)
        self.assertGreater(req.json()["Edges_data"].__len__(), 0)

    def test_GetGraphDistribution(self):
        country_id = "1"
        measure_id = "2"
        my_url = self.base_url + "/GetGraphDistribution/" + country_id + "/" + measure_id + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("graph_distribution", req.json())
        self.assertGreater(req.json()["graph_distribution"].__len__(), 0)
        self.assertIn("similarity", req.json()["graph_distribution"][0])
        self.assertIn("count", req.json()["graph_distribution"][0])

    def test_GetSubjectsByCountryId(self):
        country_id = "1"
        my_url = self.base_url + "/GetSubjectsByCountryId/" + country_id + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("documents_subject_list", req.json())
        self.assertGreater(req.json()["documents_subject_list"].__len__(), 0)
        self.assertIn("id", req.json()["documents_subject_list"][0])
        self.assertIn("subject", req.json()["documents_subject_list"][0])

    def test_GetTypeByCountryId(self):
        country_id = "1"
        my_url = self.base_url + "/GetTypeByCountryId/" + country_id + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("documents_type_list", req.json())
        self.assertGreater(req.json()["documents_type_list"].__len__(), 0)
        self.assertIn("id", req.json()["documents_type_list"][0])
        self.assertIn("type", req.json()["documents_type_list"][0])
