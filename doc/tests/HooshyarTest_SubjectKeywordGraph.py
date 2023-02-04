from django.test import TestCase
import requests


class SubjectKeywordGraphTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"
    def test_GetSubjectKeywordGraphVersion(self):
        my_url = self.base_url + "/GetSubjectKeywordGraphVersion/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("Versions", req.json())

    def test_GetSubjectListByVersionId(self):
        my_url = self.base_url + "/GetSubjectKeywordGraphVersion/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        version_id = req.json()["Versions"][0][0]
        my_url = self.base_url + "/GetSubjectListByVersionId/" + str(version_id) + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("Subject_Data", req.json())
        for row in req.json()["Subject_Data"]:
            self.assertIn("subject_id", row)
            self.assertIn("subject_name", row)
            self.assertIn("paragraph_count", row)

    def test_GetSubjectSubjectGraphData(self):
        my_url = self.base_url + "/GetSubjectKeywordGraphVersion/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        version_id = req.json()["Versions"][0][0]
        country_id = "1"
        my_url = self.base_url + "/GetSubjectSubjectGraphData/" + country_id + "/" + str(version_id) + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("Nodes_data", req.json())
        self.assertIn("Edges_data", req.json())
        self.assertGreater(req.json()["Nodes_data"].__len__(), 0)
        self.assertGreater(req.json()["Edges_data"].__len__(), 0)

    def test_SubjectKeywordGraphExtractor(self):
        my_url = self.base_url + "/GetSubjectKeywordGraphVersion/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        version_id = req.json()["Versions"][0][0]
        my_url = self.base_url + "/SubjectKeywordGraphExtractor/" + str(version_id) + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("Nodes_data", req.json())
        self.assertIn("Edges_data", req.json())
        self.assertGreater(req.json()["Nodes_data"].__len__(), 0)
        self.assertGreater(req.json()["Edges_data"].__len__(), 0)