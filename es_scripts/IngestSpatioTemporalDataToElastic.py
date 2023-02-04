
import imp
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Judgment, Standard
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
from datetime import datetime

# ---------------------------------------------------------------------------------

class SpatioTemporalIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self, files_dict, documents):
        
        for doc_id,doc_values in documents.items():

            name = doc_values[0]
            date_time = str(doc_values[1]).replace(' ',"T") + 'Z'
            lat = doc_values[2]
            lon = doc_values[3]

            new_doc = {
                "name": name,
                "date_time": date_time,
                "location": {"lat":lat,"lon":lon}

            }


            new_document = {
                "_index": self.name,
                "_id": doc_id,
                "_source":new_doc,
            }
            yield new_document


def apply(folder, Country):
    settings = {}
    mappings = {}
    index_name = "spatiotemporal_index"

    settings = es_config.EN_Settings
    mappings = es_config.Geo_Mappings

    spatiotemporalFile = str(Path(config.PERSIAN_PATH, '3days-spatiotemporal.csv'))

    fields = ['id','name','time','lat','lon']
    df = pd.read_csv(spatiotemporalFile,usecols=fields)

    geo_documents = df.set_index('id').T.to_dict('list')

    new_index = SpatioTemporalIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder,geo_documents,do_parallel=True)

