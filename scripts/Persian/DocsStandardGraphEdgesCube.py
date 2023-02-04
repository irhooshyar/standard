import operator
import re

from doc.models import StandardGraphType, Standard, StandardGraphEdgesCube, JudgmentGraphEdgesCube
from doc.models import CUBE_Subject_TableData, Subject
from django.db.models import Count, Q
import json
from abdal import config
from pathlib import Path
import time

import math


def apply(folder_name, Country):
    StandardGraphEdgesCube.objects.filter(country_id=Country).delete()
    type_list = StandardGraphType.objects.filter(country_id=Country)

    for i in range(type_list.count()-1):
        src_type_id = type_list[i].id
        src_type_name = type_list[i].name
        src_type_id_field = type_list[i].id_field
        src_name_field = type_list[i].name_field
        src_type_prefix = type_list[i].prefix

        for j in range(i+1, type_list.count()):
            target_type_id = type_list[j].id
            target_type_name = type_list[j].name
            target_id_field = type_list[j].id_field
            target_name_field = type_list[j].name_field
            target_type_prefix = type_list[j].prefix

            edges_List = Standard.objects.filter(document_id__country_id=Country)\
                .values(src_type_id_field, src_name_field, target_id_field, target_name_field)\
                .annotate(count=Count("id"))

            edges_list = []

            for row in edges_List:
                src_id = row[src_type_id_field] if row[src_type_id_field] is not None else 0
                target_id = row[target_id_field] if row[target_id_field] is not None else 0

                src_name = row[src_name_field] if row[src_name_field] is not None else "نامشخص"
                target_name = row[target_name_field] if row[target_name_field] is not None else "نامشخص"

                src_id = src_type_prefix + str(src_id)
                target_id = target_type_prefix + str(target_id)

                weight = row["count"]

                edge_obj = {"source": src_id, "source_name": src_name, "source_type_id": src_type_id, "source_type_name": src_type_name,
                            "target": target_id, "target_name": target_name, "target_type_id": target_type_id, "target_type_name": target_type_name,
                            "weight": weight}

                edges_list.append(edge_obj)

            StandardGraphEdgesCube.objects.create(country_id=Country, src_type_id=src_type_id, target_type_id=target_type_id, edges=edges_list)


