
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Standard
from django.db.models.functions import Substr, Cast
from django.db.models import Max, Min, F, IntegerField, Q
import pandas as pd
from pathlib import Path
import glob
import os
import docx2txt
import time
from es_scripts.ES_Index import ES_Index
from es_scripts.ES_Index import readFiles
import time
from elasticsearch import helpers
from collections import deque
from scripts.Persian.Preprocessing import standardIndexName
from en_doc import models as en_model
from doc.models import ParagraphsTopic

from hazm import *


normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"

stemmer = Stemmer()


def stemming(word):
    word_s = stemmer.stem(word)
    return word_s

# ---------------------------------------------------------------------------------

class ClusteringParagraphIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    

    def LocalPreprocessing(self,text):
        # Cleaning
        ignoreList = ["!", "@", "$", "%", "^", "&", "*", "_", "+", "*", "'",
                    "{", "}", "[", "]", "<", ">", ".", '"', "\t"]
        for item in ignoreList:
            text = text.replace(item, " ")

        # Delete non-ACII char
        for ch in text:
            if ch != "/" and ord(ch) <= 255 or (ord(ch) > 2000):
                text = text.replace(ch, " ")

        return text



    def Preprocessing(self,country_name,text, tokenize=True, stem=True, removeSW=True, normalize=True, removeSpecialChar=True):

        # Cleaning
        if removeSpecialChar:
            ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",", ""
                                                                                                                    "{",
                        "}", '\xad', '­'
                        "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"',
                        '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', "٫",
                        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            for item in ignoreList:
                text = text.replace(item, " ")

        # Normalization
        if normalize:
            normalizer = Normalizer()
            text = normalizer.normalize(text)
            
            # Delete non-ACII char
            for ch in text:
                if ord(ch) <= 255 or (ord(ch) > 2000):
                    text = text.replace(ch, " ")

        # Tokenization
        if tokenize:
            text = [word for word in text.split(" ") if word != ""]

            # stopwords
            if removeSW:


                stopword_list = open(Path(config.PERSIAN_PATH, "all_stopwords.txt"), encoding="utf8").read().split(
                    "\n")

                stopword_list = list(set(stopword_list))


                if country_name == 'فاوا':
                    stopword_list += ['فناوری','اطلاعات','ارتباطات']

                text = [word for word in text if word not in stopword_list]

                # filtering
                text = [word for word in text if len(word) >= 2]

            # stemming
            if stem:
                text = [stemming(word) for word in text]

        return text



    def generate_docs(self,files_dict,paragraphs):


        for row in paragraphs:
            row_id = row['id']
            country_name = row['country_name']

            paragraph_id = row['paragraph_id']
            
            paragraph_text = row['paragraph_text']

            preprocessed_text = self.LocalPreprocessing(paragraph_text)

            para_token_list = self.Preprocessing(country_name,preprocessed_text, stem=False)
            
            preprocessed_text = " ".join(para_token_list)

            document_id = row['doc_id']
            document_name = row['doc_name']

            approval_reference_name = row['approval_reference_name'] if row['approval_reference_name'] != None else 'نامشخص'
            level_name =  row['level_name'] if row['level_name'] != None else 'نامشخص'
            approval_year = row['approval_year'] if row['approval_year'] != None else 0
            keyword_subject = row['keyword_subject'] if row['keyword_subject'] != None else 'نامشخص'
            
            
            topic_id = row['topic_id']
            topic_name = row['topic_name']
            score = row['score']

            text_bytes = bytes(paragraph_text,encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_para = {
                "paragraph_id": paragraph_id,
                "preprocessed_text":preprocessed_text,
                "document_id": document_id,
                "document_name": document_name,
                'approval_reference_name':approval_reference_name,
                'level_name':level_name,
                'approval_year':approval_year,
                'keyword_subject':keyword_subject,
                "topic_id": topic_id,
                "topic_name": topic_name,
                "score":score,
                "data": base64_file
            }


            new_paragraph = {
                "_index": self.name,
                "_id": row_id,
                "pipeline":"attachment",
                "_source":new_para,
            }
            yield new_paragraph



def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = ParagraphsTopic.__name__
    
    index_name = standardIndexName(Country,model_name)
        
    country_lang = Country.language

    if country_lang in ["فارسی","استاندارد"]:
        settings = es_config.Clustering_Paragraphs_Settings
        mappings = es_config.Clustering_Paragraphs_Mappings




    paragraphs = ParagraphsTopic.objects.filter(
        country__id = Country.id).annotate(
            country_name = F('country__name'),
            doc_id = F('paragraph__document_id__id'),
            doc_name = F('paragraph__document_id__name'),
            approval_reference_name = F('paragraph__document_id__approval_reference_name'),
            level_name = F('paragraph__document_id__level_name'),
            approval_year=Cast(Substr('paragraph__document_id__approval_date', 1, 4), IntegerField()),

            paragraph_text = F('paragraph__text'),
            topic_name = F('topic__name')).values(
            'id','country_name',
            'doc_id','doc_name',
            'level_name','approval_year','approval_reference_name','keyword_subject',
            'paragraph_id','paragraph_text',
            'topic_id','topic_name','score')

    print("=========== Ingest topics paragraphs ================")
    
    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index = ClusteringParagraphIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder, paragraphs,do_parallel=True)

