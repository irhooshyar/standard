
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentGeneralDefinition, DocumentParagraphs, Judgment, Standard
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



def apply(folder, Country):
    document_name_list = Document.objects.filter(country_id__id =  Country.id).values('id','name')

    judgement_documents = Judgment.objects.filter(
        document_id__country_id__id = Country.id).values('id')

    index_name = standardIndexName(Country,Judgment.__name__)

    client = ES_Index.CLIENT

    for doc in document_name_list:
        res_query = {
            "bool":{
                "filter":{
                    "term":{
                        "document_id":doc['id']
                    }
                },
                "must":{
                    "match_phrase":doc['name']
                }
            }
        }

        response = client.search(index=local_index,
        _source_includes = ['document_id','name','attachment.content'],
        request_timeout=40,
        query=res_query,
        highlight = {
        "order":"score",
        "fields" : {
        "attachment.content" : 
        {"pre_tags" : ["<em>"], "post_tags" : ["</em>"],
            "number_of_fragments":0
        #   "fragment_size":100000
        # "boundary_scanner" : "word"
        # "type":"plain"
        }
    }}

    )
