import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country, DocumentActor
from doc.models import  Document
from doc.models import ActorType,Actor,ActorCategory,ActorSupervisor
from doc.models import DocumentParagraphs,DocumentGeneralDefinition
from datetime import datetime
import time


def apply(folder_name, Country):
    detected_operators = []
    operators_file = str(Path(config.PERSIAN_PATH, 'operators_paragraphs.txt'))

    keyword_list = ['دارای مجوز','دارای پروانه']

    
    result_paragraphs = DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains = kw) for kw in keyword_list)))

    for para in result_paragraphs:
        paragraph_text = para.text

        for kw in keyword_list:
            if kw in paragraph_text:

                kw_index = paragraph_text.find(kw)
                end_index = (kw_index+len(kw))
                operator_name = paragraph_text[0:end_index]

                if operator_name not in detected_operators:
                    detected_operators.append(operator_name)

    #----------------- write to file  --------------------------------
    with open(operators_file, 'a', encoding="utf-8") as f:
    
        for operator_name in detected_operators:
            f.write(operator_name + '\n')

    f.close()



