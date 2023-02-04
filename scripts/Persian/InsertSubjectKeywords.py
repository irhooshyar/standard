from scripts.Persian import Preprocessing
from doc.models import SubjectsVersion, SubjectList, SubjectKeywordsList, SubjectKeywordGraphCube
import math
from itertools import chain
import time
import threading
from abdal import config
from pathlib import Path
from hazm import *
import random

def Preprocessing(text):
  # Cleaning
  ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",", "{","}", '\xad', ".", "؟", "?",
                "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\t", '"', "٫",'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "\u200c"]
  for item in ignoreList:
      text = text.replace(item, " ")

  # Normalization
  normalizer = Normalizer()
  text = normalizer.normalize(text)

  # delete multi space
  while "  " in text:
    text = text.replace("  ", " ")


  # arabic char replace
  arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": ""}
  for key, value in arabic_char.items():
      text = text.replace(key, value)

  # strip text
  text = text.lstrip().rstrip()

  return text


def apply(folder_name, Country):

    t = time.time()

    Subject_Version_Name = "نسخه 4 - کلیدواژگان دکتر بهره مند (54 موضوع کامل)"
    Subject_Version_File = str(Path(config.PERSIAN_PATH, "Subject_v4.txt"))

    #SubjectsVersion.objects.filter(id=8).delete()

    Version = SubjectsVersion.objects.create(name=Subject_Version_Name)

    SubjectKeyword_File = open(Subject_Version_File,encoding = "utf-8").read().split("\n")

    last_subject = None
    keyword_degree = {}

    nodes_list = []
    edges_list = []
    added_edge = []

    color_list = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(60)]
    i = 0
    for row in SubjectKeyword_File:
        if "*" in row:
            row = Preprocessing(row)
            last_subject = SubjectList.objects.create(name=row, version=Version, color=color_list[i])
            i += 1

            node_id = "S" + str(last_subject.id)
            subject_node = {"id": node_id,
                            "node_type": "subject",
                            "name": last_subject.name,
                            "type": "rect", "size": 20,
                            "style": {"fill": "#5C5CD5"}}
            nodes_list.append(subject_node)


        else:
            row = Preprocessing(row)
            keyword_count = SubjectKeywordsList.objects.filter(word=row, subject=last_subject).count()
            if keyword_count == 0 and row != "":
                keyword_object = SubjectKeywordsList.objects.create(word=row, subject=last_subject)

                node_id = keyword_object.word
                keyword_node = {"id": node_id,
                                "node_type": "keyword",
                                "name": keyword_object.word,
                                "style": {"fill": "#33C77D"}}
                nodes_list.append(keyword_node)

                if row in keyword_degree:
                    keyword_degree[row] += 1
                else:
                    keyword_degree[row] = 1

                subject_node_id, keyword_node_id = "S" + str(last_subject.id), str(keyword_object.word)
                subject_node_name, keyword_node_name = str(last_subject.name), str(keyword_object.word)

                edge_obj = {"source": subject_node_id, "source_name": subject_node_name,
                            "target": keyword_node_id, "target_name": keyword_node_name}

                if [subject_node_id, keyword_node_id] not in added_edge:
                    edges_list.append(edge_obj)
                    added_edge.append([subject_node_id, keyword_node_id])

    for keyword, degree in keyword_degree.items():
        SubjectKeywordsList.objects.filter(word=keyword).update(degree=degree, score=1/degree)

    SubjectKeywordGraphCube.objects.create(version=Version, nodes_data=nodes_list, edges_data=edges_list)

    print("time ", time.time() - t)
