import pytest
import requests
from django.urls import reverse

BASE_URL = "http://127.0.0.1:8000"

def test_search_to_paragraph_profile():
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


   doc_id = paragraph_list[0]['_source']['document_id']
   para_id = paragraph_list[0]['_source']['paragraph_id']
   para_text =  paragraph_list[0]['_source']['attachment']['content']
   cleanText = para_text.replace("\\", ".")

   assert get_paragraph_keyword_subject(para_id,doc_id)
   assert get_paragraph_sentiment(cleanText)
   assert get_paragraph_entity_recognizer(cleanText)
   assert get_paragraph_subject_classifier(cleanText)


def get_paragraph_keyword_subject(paragraph_id,document_id):

   all_response_200 = True

   my_url = BASE_URL + "/GetParagraphSubjectContent/" + str(paragraph_id) + "/" + "12" + "/"
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      all_response_200 =  False

   response = req.json()
   doc_id = response["document_id"]
   paragraph_text = response["paragraph_text"]

   if doc_id != document_id:
      all_response_200 = False

   return all_response_200

def get_paragraph_sentiment(paragraph_text):
   sentimentAnalyserLink = BASE_URL + "/sentimentAnalyser/" + paragraph_text + "/"

   my_url = sentimentAnalyserLink
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      return False

   return True

def get_paragraph_entity_recognizer(paragraph_text):
   taggingSentenceLink = BASE_URL +  "/tagAnalyser/" + paragraph_text + "/"
   my_url = taggingSentenceLink
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      return False

   return True

def get_paragraph_subject_classifier(paragraph_text):
   classificationSentenceLink = BASE_URL +  "/classificationAnalyser/" + paragraph_text + "/"

   my_url = classificationSentenceLink
   req = requests.request("GET", my_url)
   if (req.status_code != 200):
      return False

   return True
