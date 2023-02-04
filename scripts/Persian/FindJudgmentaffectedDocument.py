import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path
import string
from doc.models import Country, Judgment, JudgmentJudge
from doc.models import  Document
from doc.models import DocumentParagraphs
from datetime import datetime
from abdal import es_config
import time
from elasticsearch import Elasticsearch
from scripts.Persian.Preprocessing import standardIndexName

es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)



def apply(folder_name, Country):
    find_judgmeny_affected_document(Country)
 


def find_judgmeny_affected_document(Country):
    doc_list = Judgment.objects.filter(document_id__country_id__id = Country.id)
    batch_size = 1000
    
    for doc in doc_list:
        affected_document_name = doc.affected_document_name
        print(affected_document_name)

    
    Judgment.objects.bulk_update(doc_list,['affected_document'],batch_size) 