import time

from doc.models import Document, Judgment, Level, ApprovalReference, Type, DocumentParagraphs
from abdal import config
from pathlib import Path
import pandas as pd

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

def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text

def numbers_preprocessing(text):
  persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
  arabicNumbers  = ['٠','١', '٢', '٣','٤', '٥', '٦','٧', '٨', '٩']
  for c in persianNumbers:
    text = text.replace(c, str(ord(c)-1776))
  for c in arabicNumbers:
    text = text.replace(c, str(ord(c)-1632))
  return text

def apply(folder_name, Country):
    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation.xlsx'))
    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df = df.drop_duplicates(subset=['title'])

    judgment_list = Judgment.objects.filter(document_id__country_id=Country).values_list('document_id', flat=True) 
    Doc_list= Document.objects.filter(id__in=judgment_list)

    doc_dict_name = {}
    doc_dict_id = {}
    for index, row in df.iterrows():
        doc_dict_id[str(row["id"])] = row["title"]
        doc_dict_name[str(row["title"])] = row["id"]

    i=1
    for doc in Doc_list:
        print(i/Doc_list.count())
        i+=1
        if str(doc.name) in doc_dict_id.keys():
            Document.objects.filter(id=doc.id).update(name=doc_dict_id[doc.name], file_name=doc.name)
        elif doc.file_name in doc_dict_id.keys():
            Document.objects.filter(id=doc.id).update(name=doc_dict_id[doc.file_name])
        elif str(doc.name) in doc_dict_name.keys():
            Document.objects.filter(id=doc.id).update(file_name=doc_dict_name[str(doc.name)])
        else:
            doc.name = doc.file_name


