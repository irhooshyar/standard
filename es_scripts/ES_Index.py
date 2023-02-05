
from pydoc import doc
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Book, Document, DocumentParagraphs, Standard, Standard_Branch, Standard_Status
from django.db.models.functions import Substr, Cast
from django.db.models import Max, Min, F, IntegerField, Q
import pandas as pd
from pathlib import Path
import glob
import os
import docx2txt
import time
from elasticsearch import helpers
from collections import deque
import textract

def readFiles(path):
    result_text = {}
        

    all_files = glob.glob(path + "/*")
    for file in all_files:
        format = str(os.path.basename(file)).split(".")[-1]
        try:
            text = ''
            if format.lower() == "doc":
                text = textract.process(file, encoding='utf-8').decode("utf-8")
            if format.lower() =='docx':
                text = docx2txt.process(file)

            text_bytes = bytes(text,encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            file = str(os.path.basename(file)).split(".")[0]
            result_text[file] =base64_text
        except:
            print(f'{file} can not read')

    all_files = glob.glob(path + "//*.txt")
    for file in all_files:
        text_bytes = open(file, "rb").read()
        base64_bytes = base64.b64encode(text_bytes)
        base64_text = (str(base64_bytes)[2:-1])
        file = str(os.path.basename(file)).split(".")[0]
        result_text[file] =base64_text

    return result_text

class ES_Index():

    ES_URL = es_config.ES_URL
    CLIENT = Elasticsearch(ES_URL, timeout=40)

    def __init__(self, name, settings,mappings):
        self.name = name
        self.settings = settings
        self.mappings = mappings


    def create(self):
        if self.CLIENT.indices.exists(index=self.name):
            print(f'{self.name} existed!')

            # self.CLIENT.indices.create(index=self.name, mappings=self.mappings,
            #                 settings=self.settings, ignore=400)
            
            # print(f'{self.name} updated')
            # self.CLIENT.indices.put_mapping(index=[self.name],body = self.mappings)

        else:
            self.CLIENT.indices.create(index=self.name, mappings=self.mappings,
                            settings=self.settings)
            print(f'{self.name} created')

# --------------- Documents Insert ----------------------------------------

    def generate_docs(self,files_dict,documents):
        pass


    def bulk_insert_documents(self, folder_name,documents, do_parallel=False):
        print('Insert_Documents started ...')
        start_t = time.time()

        generate_docs_method = self.generate_docs

        dataPath = str(Path(config.DATA_PATH, folder_name))
        files_dict = readFiles(dataPath)

        if do_parallel:

            deque(helpers.parallel_bulk(self.CLIENT, generate_docs_method(files_dict,documents),thread_count=8,chunk_size=500,request_timeout=3000),
             maxlen=0)

        else:
            helpers.bulk(self.CLIENT, generate_docs_method(files_dict,documents),chunk_size=500,request_timeout = 120)


        self.CLIENT.indices.flush([self.name])
        self.CLIENT.indices.refresh([self.name])

        # Check the results:
        result = self.CLIENT.count(index=self.name)

        end_t = time.time()
        
        print(f"{result['count']} documents indexed.")
        print('Ingestion completed (' + str(end_t - start_t) + ').')




