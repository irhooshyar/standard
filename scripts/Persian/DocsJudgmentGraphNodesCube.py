import operator
import re

from doc.models import JudgmentGraphType, Judgment, JudgmentGraphNodesCube
from doc.models import CUBE_Subject_TableData, Subject
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time

import math


def apply(folder_name, Country):
    JudgmentGraphNodesCube.objects.filter(country_id=Country).delete()
    type_list = JudgmentGraphType.objects.filter(country_id=Country)

    for type_obj in type_list:
        type_id = type_obj.id
        type_name = type_obj.name
        type_id_field = type_obj.id_field
        type_name_field = type_obj.name_field
        type_color = type_obj.color
        type_prefix = type_obj.prefix

        nodes_list = []

        Judgment_List = Judgment.objects.filter(document_id__country_id=Country).distinct().values_list(type_id_field,
                                                                                                        type_name_field)
        for judge in Judgment_List:
            judge = list(judge)
            judge_id, judge_name = judge[0], judge[1]
            if judge_id is None:
                judge_id = 0
                judge_name = "نامشخص"

            judge_id = type_prefix + str(judge_id)

            node = {"id": judge_id, "name": judge_name, "type_id": type_id, "type_name": type_name,  "style": {"fill": type_color}}
            nodes_list.append(node)

        JudgmentGraphNodesCube.objects.create(country_id=Country, type_id=type_id, nodes=nodes_list)