from optparse import Values
import re
from scripts.Persian import Preprocessing
from doc.models import Document, DocumentParagraphs, ParagraphsSubject
# from transformers import BertTokenizer, TFBertModel
from hazm import sent_tokenize, Normalizer
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaMulticore
from collections import Counter
import math
import time
import numpy as np
from scipy import spatial
from abdal import config
import threading
from itertools import chain
import os
import re

normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"

def Local2Preprocessing(text):
  # Cleaning
  ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",", "{","}", '\xad', ".", "؟", "?",
                "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\t", '"', "٫",'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "\u200c"]
  for item in ignoreList:
      text = text.replace(item, " ")

  # Normalization
  normalizer = Normalizer()
  text = normalizer.normalize(text)

  # delete /n and multi space
  text = text.replace("\n", "")
  while "  " in text:
    text = text.replace("  ", " ")

  # strip text
  text = text.lstrip().rstrip()

  return text


def LocalPreprocessing(text):
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

def entropy(array):
    total_entropy = 0
    s = sum(array)

    for i in array:
        pi = (i/s)
        if i != 0:
            total_entropy += -pi * math.log(pi, 2)

    return total_entropy

def CreateSubjectKeywordGraph(Subject_Keyword_Dict):
    Keyword_Degree = {}

    for subject, keywords in Subject_Keyword_Dict.items():
        for keyword in keywords:
            if keyword not in Keyword_Degree:
                Keyword_Degree[keyword] = 1
            else:
                Keyword_Degree[keyword] += 1

    return Keyword_Degree

def DocumentScoreInSubjectGroup(Keywords_Degree_Dict, Subject_Keyword_Dict, Document_Text):
    Document_Result = {}
    for subject, keywords in Subject_Keyword_Dict.items():
        Document_Result[subject] = {"score": 0, "keywords": []}
        for keyword in keywords:
            keyword_score = 1/Keywords_Degree_Dict[keyword]
            if keyword in Document_Text:
                Document_Result[subject]["score"] += keyword_score
                Document_Result[subject]["keywords"].append(keyword)
    return Document_Result

def NormalizeDocumentScore(Document_Score_Dict):
    sum_value = sum([value["score"] for key, value in Document_Score_Dict.items()])
    factor = 1/sum_value if sum_value > 0 else 0

    for key, value in Document_Score_Dict.items():
        Document_Score_Dict[key]["normal_score"] = round(Document_Score_Dict[key]["score"] * factor, 3)

    return Document_Score_Dict

def DocumentSubjectExtractor(text,subject_keywords_dict,keyword_degree):
        
    Document_Result = DocumentScoreInSubjectGroup(keyword_degree, subject_keywords_dict, text)
    Document_Score_Normalized = NormalizeDocumentScore(Document_Result)

    Max_normal_score_name = ''
    Max_normal_score = 0
    for key, value in Document_Score_Normalized.items():
        if Document_Score_Normalized[key]["normal_score"] > Max_normal_score:
            Max_normal_score = Document_Score_Normalized[key]["normal_score"]
            Max_normal_score_name = key

    return Max_normal_score_name , Max_normal_score

def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list




def create_subject_keyword_dict():
    file_path = os.path.join(config.PERSIAN_PATH, "Subject_v1.txt")
    subject_keyword_file = open(file_path, encoding='utf-8').read().split("\n")

    subject_keyword = {}
    # Insert Subject Keyword Data

    last_subject = ""
    for line in subject_keyword_file:
        if "*" in line:
            line = Local2Preprocessing(line.replace("*", ""))
            subject_keyword[line] = []
            last_subject = line
        else:
            subject_keyword[last_subject].append(Local2Preprocessing(line))


    # Create Graph Object With Function Call
    Keyword_Degree = CreateSubjectKeywordGraph(subject_keyword)


    return [subject_keyword,Keyword_Degree]

def apply(folder_name, Country):
    t = time.time()

    ParagraphsSubject.objects.filter(country__id=Country.id).delete()
    paragraph_list = list(DocumentParagraphs.objects.filter(document_id__country_id_id=Country).values())

    print(paragraph_list.__len__())

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    Sliced_Paragraph = Slice_List(paragraph_list, Thread_Count)


    subject_keywords_dict, keyword_degree = create_subject_keyword_dict()

    thread_obj = []
    thread_number = 0
    for S in Sliced_Paragraph:
        thread = threading.Thread(target=Extract_Paragraph_Subject, args=(S, Result_Create_List, thread_number, Country,subject_keywords_dict,keyword_degree))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()
    
    Result_Create_List = list(chain.from_iterable(Result_Create_List))
    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        ParagraphsSubject.objects.bulk_create(sub_list)
        print(f"{i} of /{slice_count}")

    
    print("time ", time.time() - t)

def Extract_Paragraph_Subject(paragraph_list, Result_Create_List, thread_number, Country,subject_keywords_dict,keyword_degree):
    Create_List = []
    for p in paragraph_list:
        if len(p['text']) > 80:
            Max_normal_score_name , Max_normal_score = DocumentSubjectExtractor(p['text'],subject_keywords_dict,keyword_degree)

            if Max_normal_score > 0:
                para_subject = ParagraphsSubject(country = Country, paragraph_id = p['id'],subject_name = Max_normal_score_name)
                Create_List.append(para_subject)
        
    Result_Create_List[thread_number] = Create_List