from django.test import TestCase
import requests

class SearchDetailTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"

    def test_document_detail(self):
        doc_id = "120838"
        search_type = "exact"
        text = "تنوع زیستی"

        my_url = self.base_url + "/GetSearchDetails_ES_2/" + doc_id + "/" + search_type + "/" + text + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        paragraph_list = response["result"]

        self.assertTrue(req.ok)

        for para in paragraph_list:
            para_doc_id = para['_source']['document_id']
            self.assertEqual(para_doc_id, int(doc_id))