import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re
from charset_normalizer import detect

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country, DocumentActor
from doc.models import  Document,DocumentClause
from doc.models import ActorType,Actor,ActorCategory,ActorSupervisor
from doc.models import DocumentParagraphs,DocumentGeneralDefinition
from doc.models import ExecutiveRegulations
from datetime import datetime
from scripts.Persian import Preprocessing,DocsCompleteParagraphsExtractor
import time
import os
from pathlib import Path

import docx2txt
import glob
from hazm import *

from abdal import config
from scripts.Persian.DocsExecutiveClausesExtractor import get_paragraphs, get_disallowed_doc_type


def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)

    return text


def apply(folder_name, Country):
    start_t = time.time()

    # get documents which need to be saved as complete paragraphs
    base_result = DocumentParagraphs.objects.filter(document_id__country_id=Country).\
        exclude(reduce(operator.or_, (Q(document_id__name__startswith=word) for word in get_disallowed_doc_type())))
    # doc_ids_list_of_dict = get_paragraphs(base_result).annotate(doc_id = F("document_id__id")).values("doc_id").distinct()
    doc_ids_list_of_dict = get_paragraphs(base_result)


    doc_ids = []
    print(f'found {len(doc_ids_list_of_dict)} paras')
    for doc_id in doc_ids_list_of_dict:
        id_ = doc_id['obj'].document_id.id
        if id_ not in doc_ids:
            doc_ids.append(id_)

    print(f'found {len(doc_ids)} docs')

    result_document_list = Document.objects.filter(id__in = doc_ids)
    selected_files = []

    for doc in result_document_list:
        doc_file_name = doc.name # without extension
        selected_files.append(doc_file_name)

    country_file_name = str(Country.file).split('.')[0].split('/')[-1]
    dataPath = str(Path(config.DATA_PATH, country_file_name))
    print(dataPath)
    files_text = custom_readFiles(dataPath,readContent=True,preprocess=False,preprocessArg={},selected_files=selected_files)
    
    DocsCompleteParagraphsExtractor.apply(folder_name,Country,files_text)

    end_t = time.time()        
    print('Complete paragraphs added (' + str(end_t - start_t) + ').')





def custom_readFiles(path, readContent=True, preprocess=True, preprocessArg={},selected_files=[]):
    # all_files = glob.glob(path + "//*.docx")
    all_files = [file for file in glob.glob(path + "//*.docx") if str(os.path.basename(file).split(".")[0]) in selected_files]

    result_text = {}

    for file in all_files:

        if readContent:
            text = docx2txt.process(file)
            # Arabic char convert
            text = arabicCharConvert(text)
            if preprocess:
                text = Preprocessing(text, **preprocessArg)
        else:
            text = ""
        file = str(os.path.basename(file)).split(".")[0]
        result_text[file] = text

        
        
    # all_files = glob.glob(path + "//*.txt")


    all_files = [file for file in glob.glob(path + "//*.txt") if standardFileName(str(os.path.basename(file).split(".")[0])) in selected_files]
    # print(all_files)
    # print(str(len(selected_files)))
    for file in all_files:
        if readContent:
            text = open(file, encoding="utf8").read()
            # Arabic char convert
            text = arabicCharConvert(text)
            if preprocess:
                text = Preprocessing(text, **preprocessArg)
        else:
            text = ""
        file = str(os.path.basename(file)).split(".")[0]
        result_text[file] = text

    return result_text


def standardFileName(name):
    name = name.replace(".", "")
    name = arabicCharConvert(name)
    name = persianNumConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  "," ")

    return name

def persianNumConvert(text):
    persian_num_dict = {"۱": "1" ,"۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹":"9" , "۰": "0" }
    for key, value in persian_num_dict.items():
        text = text.replace(key, value)
    return text


def arabicCharConvert(text):
    arabic_char_dict = {"ى": "ی" ,"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ":" ", "\n\n":"\n", "\n ":"\n" , }
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)

    return text



