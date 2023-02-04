from django.test import TestCase
import requests

class ProfileDataCollectionTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"
    def test_GetDocumentsByCountryId_Modal(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("documentsList", req.json())
        self.assertIn("document_count", req.json())
        self.assertGreater(req.json()["documentsList"].__len__(), 0)
        self.assertGreater(req.json()["document_count"], 0)


    def test_GetPersianDefinitionByDocumentId(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        document_id = "120873" #req.json()["documentsList"][0]["id"]
        my_url = self.base_url + "/GetPersianDefinitionByDocumentId/" + str(document_id) + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("documents_definition", req.json())
        self.assertIn("text", req.json()["documents_definition"][0])
        self.assertIn("keywords", req.json()["documents_definition"][0])


    def test_GetGeneralDefinition(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        document_id = "120873" #req.json()["documentsList"][0]["id"]
        my_url = self.base_url + "/GetGeneralDefinition/" + str(document_id) + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("result", req.json())

    def test_GetTFIDFByDocumentId(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        document_id = "120873" #req.json()["documentsList"][0]["id"]
        my_url = self.base_url + "/GetTFIDFByDocumentId/" + str(document_id) + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("documents_tfidf_list", req.json())
        self.assertIn("word", req.json()["documents_tfidf_list"][0])
        self.assertIn("count", req.json()["documents_tfidf_list"][0])
        self.assertIn("weight", req.json()["documents_tfidf_list"][0])


    def test_GetNGramByDocumentId(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        document_id = "120873" #req.json()["documentsList"][0]["id"]
        my_url = self.base_url + "/GetNGramByDocumentId/" + str(document_id) + "/2/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("document_ngram_list", req.json())
        self.assertIn("id", req.json()["document_ngram_list"][0])
        self.assertIn("text", req.json()["document_ngram_list"][0])
        self.assertIn("count", req.json()["document_ngram_list"][0])
        self.assertIn("score", req.json()["document_ngram_list"][0])


    def test_GetReferencesByDocumentId(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        document_id = "120873" #req.json()["documentsList"][0]["id"]
        my_url = self.base_url + "/GetReferencesByDocumentId/" + str(document_id) + "/1/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("document_references_list", req.json())
        my_url = self.base_url + "/GetReferencesByDocumentId/" + str(document_id) + "/2/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("document_references_list", req.json())

    def GetSubjectByDocumentId(self):
        country_id = "1"
        my_url = self.base_url + "/GetDocumentsByCountryId_Modal/" + country_id + "/1/10/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        document_id = "120873" #req.json()["documentsList"][0]["id"]
        my_url = self.base_url + "/GetReferencesByDocumentId/" + str(document_id) + "/1/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("document_subject_list", req.json())
        self.assertIn("subject", req.json()["document_subject_list"][0])
        self.assertIn("weight", req.json()["document_subject_list"][0])
        self.assertIn("keywords_text", req.json()["document_subject_list"][0])
        self.assertIn("keywords_title", req.json()["document_subject_list"][0])
        self.assertIn("special_references", req.json()["document_subject_list"][0])
