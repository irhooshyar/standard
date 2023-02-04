from django.test import TestCase
import requests


class ActorsSearchTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"
    def test_SearchTable(self):
        country_id = "1"
        multiselect_role_value = "0"
        area_id = "0"
        multiselect_actor_value = "0"
        preprocessed_keywords_text = "زیست"
        curr_page1 = "1"

        my_url = self.base_url + "/SearchActorsByKeywords_es/" \
                + country_id + "/" + multiselect_role_value + "/" + area_id + "/" + multiselect_actor_value + "/" + preprocessed_keywords_text + "/" + curr_page1 + "/"
        
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        

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