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
from doc.models import Country, DocumentActor, ActorCategory
from doc.models import  Document
from doc.models import DocumentParagraphs
from datetime import datetime
from abdal import es_config
import time
from elasticsearch import Elasticsearch
from scripts.Persian.Preprocessing import standardIndexName

import re


def apply(folder_name, Country):
    update_organization_document(Country)



def update_organization_document(Country):
    find_org_id = ActorCategory.objects.get(name = 'سازمان').id
    organization_doc_ids = DocumentActor.objects.filter(actor_id__actor_category_id__id=find_org_id).values('document_id_id', 'actor_id__name')

    # print(organization_doc_ids)

    organization_doc_dict = {}
    organization_unique_id_list = []

    for doc in organization_doc_ids:
        doc_id = doc['document_id_id']
        organization_name = doc['actor_id__name']
        if doc_id not in organization_doc_dict:
            organization_doc_dict[doc_id] = [organization_name]
            organization_unique_id_list.append(doc_id)
        else:
            if organization_name not in organization_doc_dict[doc_id]:
                organization_doc_dict[doc_id].append(organization_name)

    
    print(organization_doc_dict)


    batch_size = 1000

    selected_doc_list = Document.objects.filter(id__in = organization_unique_id_list)

    for doc in selected_doc_list:
        doc.organization_name = '-'.join (organization_doc_dict[doc.id])
    
    Document.objects.bulk_update(
        selected_doc_list,['organization_name'],batch_size)
    
    print('Document Organization updated.')


