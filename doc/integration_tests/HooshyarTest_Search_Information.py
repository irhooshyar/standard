import pytest
import requests
from django.urls import reverse

BASE_URL = "http://127.0.0.1:8000"


def test_search_to_information():
   user_text = "جام جهانی"
   place = "عنوان"
   search_type = "and"

   my_url = BASE_URL + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
            + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
            + "0" + "/" + place + "/" + user_text + "/" + search_type + "/" \
            + "1" + "/"
   req = requests.request("GET", my_url)
   response = req.json()
   total_hits = response["total_hits"]
   assert req.status_code == 200
   assert 1 == total_hits


   doc_id = response["result"][0]["_id"]
   
   my_url = BASE_URL + "/GetSearchDetails_ES_2/" + doc_id + "/" + search_type + "/" + user_text + "/"
   req = requests.request("GET", my_url)
   response = req.json()
   paragraph_list = response["result"]

   assert req.status_code == 200

   for para in paragraph_list:
      para_doc_id = para['_source']['document_id']
      assert para_doc_id == int(doc_id)

   assert get_document_information(doc_id)


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
