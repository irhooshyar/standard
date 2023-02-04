import imp
import operator
from argparse import Action
import json
from functools import reduce
from os import name
import re

from django.db.models import Q,F

from abdal import config
from pathlib import Path

from doc.models import Country, RegulatorOperator, DocumentRegulator, RegularityTools
from doc.models import  Document
from doc.models import ActorType,Actor,ActorCategory,ActorSupervisor
from doc.models import DocumentParagraphs,DocumentGeneralDefinition
from datetime import datetime
import time
from difflib import SequenceMatcher
from doc.models import Operator
import re

def apply(folder_name, Country):
    start_t = time.time()
    batch_size = 1000
    Create_List = []


    documentList = Document.objects.filter(country_id=Country)
    RegulatorOperator.objects.filter(document_id__country_id = Country).delete()

    operatorList = Operator.objects.all()
    operatorDict = {}
    for operator_obj in operatorList:
        operatorDict[operator_obj.name] = operator_obj.forms.split('/')

    # regularity_tools = RegularityTools.objects.all()
    regularity_tools = RegularityTools.objects.filter(name = 'مجوز')


    for rg_tool in regularity_tools:
        tool_name = rg_tool.name

        pattern_keyword = tool_name + ' ' + 'از'


        regulator_paragraphs = DocumentRegulator.objects.filter(
            document_id__in = documentList,
            tool_id__name = tool_name)

        regulator_paragraphs = regulator_paragraphs.filter(
            paragraph_id__text__icontains = pattern_keyword)

        for result in regulator_paragraphs:
            paragraph_text =  result.paragraph_id.text

            indices = [m.start() for m in re.finditer(tool_name, paragraph_text )]

            for index in indices:
                pattern_kw_index = index

                cropped_text = paragraph_text[:pattern_kw_index]

                for operator_obj in operatorList:
                    operator_forms_list = operatorDict[operator_obj.name]

                    if any(operator_form in cropped_text for operator_form in operator_forms_list):

                        for operator_form in operator_forms_list:

                            if operator_form in cropped_text:

                                
                                RegulatorOperator_obj = RegulatorOperator(
                                    document_id = result.document_id,
                                    tool_id = result.tool_id,
                                    operator_id = operator_obj,
                                    regulator_id = result.regulator_id,
                                    paragraph_id = result.paragraph_id,
                                    current_operator_form = operator_form
                                )
                                if RegulatorOperator_obj not in Create_List:
                                    Create_List.append(RegulatorOperator_obj)
                                else:
                                    print('y')
                                    
                               
        
        if Create_List.__len__() > batch_size:
            RegulatorOperator.objects.bulk_create(Create_List)
            Create_List = []

    RegulatorOperator.objects.bulk_create(Create_List)

    # Deleting duplicates
    duplicated_rows_count = 0
    for row in RegulatorOperator.objects.all().reverse():
        if RegulatorOperator.objects.filter(
            document_id__id = row.document_id.id,
            tool_id__id = row.tool_id.id,
            operator_id__id = row.operator_id.id,
            regulator_id__id = row.regulator_id.id,
            paragraph_id__id = row.paragraph_id.id,
            current_operator_form = row.current_operator_form).count() > 1:
            duplicated_rows_count += 1
            row.delete()


    print(f'{duplicated_rows_count} duplicated rows deleted')

    end_t = time.time()        
    print('Operators added (' + str(end_t - start_t) + ').')




