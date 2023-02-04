import os
from re import search
import time
from argparse import Action
import json
import xlrd
from dateutil import parser
import pandas as pd
from django.db.models import Max, Min, F, IntegerField, QuerySet, Sum, Count, Q
from openpyxl import load_workbook

from abdal import config
from pathlib import Path
from doc.models import ActorArea, ActorSubArea, CUBE_DocumentJsonList, JudgmentGraphType, DocumentActor, Judgment, \
    JudgmentCategories, JudgmentConclusionDisplayName, JudgmentJudge, JudgmentSearchParameters, \
    JudgmentSubjectTypeDisplayName, JudgmentType, LegalOrientation, RevokedType, SimilarityType, Standard, \
    Standard_Branch, Standard_Status, StandardSearchParameters, Type, KeywordList, Subject, SubjectKeyWords, Slogan, \
    SloganSynonymousWords, SubjectSubAreaKeyWords, SubjectArea, SubjectSubArea
from doc.models import ActorArea, ActorSubArea, CUBE_DocumentJsonList, JudgmentGraphType, DocumentActor, Rahbari, StandardGraphType, Judgment, JudgmentCategories, JudgmentConclusionDisplayName, JudgmentJudge, JudgmentSearchParameters, JudgmentSubjectTypeDisplayName, JudgmentType, LegalOrientation, SimilarityType, Standard, Standard_Branch, Standard_Status, StandardSearchParameters, Type, KeywordList, Subject, SubjectKeyWords, Slogan , SloganSynonymousWords
from doc.models import ApprovalReference, Document, Measure, Level, UserRole
from doc.models import LegalOrientation,LegalOrientationKeyWords
from doc.models import Document,DocumentParagraphs
from doc.models import Regulator,RegularityArea,RegularityTools
from doc.models import Actor,ActorCategory,ActorType,ActorGraphType
from doc.models import CollectiveActor,SearchParameters, RahbariSearchParameters
from doc.models import Template_Panels_Info,RevokedType
from doc.models import Operator,ClusteringAlorithm,FeatureSelectionAlgorithm
from doc.models import RahbariLabel
from django.shortcuts import get_object_or_404
from pathlib import Path
import glob
import os
import docx2txt
import time
from elasticsearch import helpers
from collections import deque
from en_doc import models as en_model
import textract

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

def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)
    text = numbers_preprocessing(text)

    return text

def CheckDate(date):
    try:
        format = '%Y-%m-%d'
        parser.parse(date)
        return date
    except ValueError:
        return None

def DataFrame2Dict(df, key_field, values_field):
    result_dict = {}
    for index, row in df.iterrows():
        data_list = {}
        for field in values_field:
            data_list[field] = row[field]
        result_dict[str(row[key_field])] = data_list

    return result_dict

def Roles_Insert():
    rolesFile = str(Path(config.PERSIAN_PATH, 'Roles.txt'))
    with open(rolesFile, encoding="utf8") as f:
        lines = f.readlines()
        for role in lines:
            role = role.replace("\n", "")
            result_count = UserRole.objects.filter(persian_name=role).count()
            if result_count == 0:
                UserRole.objects.create(persian_name=role)
    f.close()

def Levels_Insert():
    levelsFile = str(Path(config.PERSIAN_PATH, 'Levels.txt'))
    with open(levelsFile, encoding="utf8") as f:
        lines = f.readlines()
        for level in lines:
            level = level.replace("\n", "")
            result_count = Level.objects.filter(name=level).count()
            if result_count == 0:
                Level.objects.create(name=level)
    f.close()

def Mesures_Insert():
    measureFile = str(Path(config.PERSIAN_PATH, 'measure.txt'))
    with open(measureFile, encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            persian_name = line.split(",")[0]
            english_name = line.split(",")[1]
            type = line.split(",")[2]
            result_count = Measure.objects.filter(persian_name=persian_name, english_name=english_name).count()
            if result_count == 0:
                Measure.objects.create(persian_name=persian_name, english_name=english_name, type=type)
            else:
                Measure.objects.filter(persian_name=persian_name, english_name=english_name).update(type=type)
    f.close()


def Actor_Graph_Types_Insert():
    measureFile = str(Path(config.PERSIAN_PATH, 'ActorGraphTypes.txt'))
    with open(measureFile, encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            graph_type_name = line.strip()
            result_count = ActorGraphType.objects.filter(name = graph_type_name).count()
            if result_count == 0:
                ActorGraphType.objects.create(name = graph_type_name)

    f.close()
    print('Actor Graph Types added.')

def Type_Colors_Insert():
    typecolorsFile = str(Path(config.PERSIAN_PATH, 'Type.txt'))
    with open(typecolorsFile, encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            l = line.split('\t')
            docType = l[0]
            color = l[1].replace("\n", "")

            result_count = Type.objects.filter(name=docType).count()

            if result_count == 0:
                Type.objects.create(name=docType, color=color)
    f.close()

def Keywords_Insert():
    arabic_char_dict = {"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ", "\u200c": " "}
    keywordListFile = str(Path(config.PERSIAN_PATH, 'keywordList.txt'))
    with open(keywordListFile, encoding="utf8") as f:
        lines = f.readlines()
        lines = set(lines)
        for line in lines:
            for key, value in arabic_char_dict.items():
                line = line.replace(key, value)
            line = line.strip()
            result_count = KeywordList.objects.filter(word=line).count()
            if result_count == 0:
                KeywordList.objects.create(word=line)
    f.close()

def Subjects_Insert():
    SubjectKeyWords.objects.filter(place=None).delete()
    subjectKeywordsFile = str(Path(config.PERSIAN_PATH, 'Subjects.txt'))
    data = open(subjectKeywordsFile, encoding="utf8").read().split("\n")
    subject = ""
    last_subject_star_count = 1
    for row in data:
        row = arabic_preprocessing(row)
        starcount = row.count("*")
        if starcount >= 1:
            subject = row.replace("*", "")
            result_count = Subject.objects.filter(name=subject).count()
            if result_count == 0:
                Subject.objects.create(name=subject)
            last_subject_star_count = starcount
        else:
            keyword = row
            subject_id = Subject.objects.get(name=subject)
            place = "متن و عنوان"
            if last_subject_star_count == 2:
                place = "مرجع تصویب"
            result_count = SubjectKeyWords.objects.filter(subject_id=subject_id, word=keyword, place=place).count()
            if result_count == 0:
                SubjectKeyWords.objects.create(subject_id=subject_id, word=keyword, place=place)

def Subjects_area_Insert(country_id):
    print('Subjects_area_Insert ...')
    SubjectSubAreaKeyWords.objects.filter(place=None).delete()
    files_dir = Path(config.PERSIAN_PATH, 'SubjectArea')
    for filename in os.listdir(files_dir):
        file_addr = os.path.join(files_dir, filename)
        xls = pd.ExcelFile(file_addr)
        area_name = str(filename).replace('.xlsx','')
        area_name = arabic_preprocessing(area_name)
        area = SubjectArea.objects.filter(name = area_name,language=country_id.language)
        if area.count() > 0:
            area = area[0]
        else:
            area = SubjectArea.objects.create(name = area_name,language=country_id.language)
        sheets_name = load_workbook(file_addr,read_only=True, keep_links=False).sheetnames
        for sub_area_name in sheets_name:
            
            df = pd.read_excel(xls, sub_area_name,header=None,index_col=None)
            
            sub_area_name = arabic_preprocessing(sub_area_name)
            sub_area = SubjectSubArea.objects.filter(name=sub_area_name, subject_area_id=area)
            if sub_area.count() > 0:
                sub_area = sub_area[0]
            else:
                sub_area = SubjectSubArea.objects.create(name=sub_area_name, subject_area_id=area)
            
            df = df[df[0].notna()]

            for index,row in df.iterrows():
                keyword = row[0]

                if keyword != '':

                    result_count = SubjectSubAreaKeyWords.objects.filter(subject_sub_area_id=sub_area, word=keyword,
                                                                        place="متن و عنوان").count()
                    if result_count == 0:
                        SubjectSubAreaKeyWords.objects.create(subject_sub_area_id=sub_area, word=keyword,
                                                            place="متن و عنوان")


def Update_Docs_fromExcel(Country):
    documentList = Document.objects.filter(country_id=Country)

    # excelFile = str(Path(config.PERSIAN_PATH, 'DoticFull_with_limited_title.xlsx'))
    excelFile = str(Path(config.PERSIAN_PATH, 'Rahbari_Full_Excel.xlsx'))
    


    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df['limited_title'] = df['limited_title'].apply(lambda x: standardFileName(x))
    df = df.drop_duplicates(subset=['limited_title'])

    maraje_list = df['row_MarjaeTasvib'].unique()

    for marja in maraje_list:
        marja = arabic_preprocessing(marja)
        result_count = ApprovalReference.objects.filter(name=marja).count()
        if result_count == 0:
            ApprovalReference.objects.create(name=marja)

    # documents update
    dataframe_dictionary = DataFrame2Dict(df, "limited_title", ["row_MarjaeTasvib", "TasvibDate", "EblaghieDate","title"])

    for document in documentList:
        document_id = document.id
        document_name = standardFileName(document.name)
        document_file_name = standardFileName(document.file_name)

        if document_file_name in dataframe_dictionary:
            marjae_tasvib = arabic_preprocessing(dataframe_dictionary[document_file_name]['row_MarjaeTasvib'])
            tasvib_date = CheckDate(str(dataframe_dictionary[document_file_name]['TasvibDate']))
            eblagh_date = CheckDate(str(dataframe_dictionary[document_file_name]['EblaghieDate']))
            title = str(dataframe_dictionary[document_file_name]['title'])

            ApprovalRef = ApprovalReference.objects.get(name=marjae_tasvib)
            Document.objects.filter(id=document_id).update(name = title,
                                                            approval_reference_id=ApprovalRef,
                                                           approval_reference_name=marjae_tasvib,
                                                           approval_date=tasvib_date, communicated_date=eblagh_date)

def LegalOrientations_Insert():
    arabic_char_dict = {"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ", "\u200c": " "}
    LegalOrientationsFile = str(Path(config.PERSIAN_PATH, 'LegalOrientations.txt'))
    with open(LegalOrientationsFile, encoding="utf-8") as f:
        lines = f.readlines()
        current_legal_orientation = ''
        for line in lines:
            for key, value in arabic_char_dict.items():
                line = line.replace(key, value)
            line = line.strip()
            if '*' in line:
                legal_orientation_name = line.replace('*', '')
                current_legal_orientation = legal_orientation_name
                result_count = LegalOrientation.objects.filter(name=legal_orientation_name).count()
                # if not exist, creat
                if result_count == 0:
                    LegalOrientation.objects.create(name=legal_orientation_name)
            else:
                legal_orientation = LegalOrientation.objects.get(name=current_legal_orientation)
                result_count = LegalOrientationKeyWords.objects.filter(legal_orientation_id=legal_orientation,
                                                                       word=line).count()
                if result_count == 0:
                    LegalOrientationKeyWords.objects.create(legal_orientation_id=legal_orientation, word=line)
    f.close()

def RegularityTools_Insert():
    RegularityToolsFile = str(Path(config.PERSIAN_PATH, 'RegularityTools.txt'))
    with open(RegularityToolsFile, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            tool_name = line.strip()
            result_count = RegularityTools.objects.filter(name=tool_name).count()

            # if not exist, creat
            if result_count == 0:
                RegularityTools.objects.create(name=tool_name)
    f.close()


def ActorRolePatternKeywords_Insert():
    ActorRolePatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'ActorRolePatternKeywords.json'))
    f = open(ActorRolePatternKeywordsFile,encoding="utf-8")
    ActorRolePatternKeywords = json.load(f)
    f.close()
    for actor_role,keywords in ActorRolePatternKeywords.items():
        role_kws = '/'.join(keywords)
        result_count = ActorType.objects.filter(name=actor_role).count()
        if result_count == 0:
            ActorType.objects.create(name=actor_role,pattern_keywords = role_kws)
        else:
            ActorType.objects.filter(name=actor_role).update(pattern_keywords = role_kws)

def Actors_Insert():

    fullActorsInformationFile = str(Path(config.PERSIAN_PATH, 'fullActorsInformation.json'))

    f = open(fullActorsInformationFile, encoding="utf-8")
    fullActorsInformation = json.load(f)
    f.close()

    for category in fullActorsInformation:
        category_count = ActorCategory.objects.filter(name=category).count()

        # if not exist, creat
        if category_count == 0:
            actor_category = ActorCategory.objects.create(name=category)
        else:
            actor_category = ActorCategory.objects.get(name=category)

        actors = fullActorsInformation[category]

        for actor in actors:
            actor_forms = actors[actor]
            actor_forms = '/'.join(actor_forms)

            actor_count = Actor.objects.filter(name=actor, actor_category_id=actor_category).count()

            # if not exist, creat
            if actor_count == 0:
                Actor.objects.create(name=actor, actor_category_id=actor_category,
                                     forms=actor_forms)
            else:
                # if exist, update
                Actor.objects.filter(
                    name=actor, actor_category_id=actor_category).update(forms=actor_forms)

    print('Actors updated.')


def Area_SubArea_Insert():
    AreaFile = str(Path(config.PERSIAN_PATH, 'AreaActorsInformation.json'))

    f = open(AreaFile, encoding="utf-8")
    areaActorsInformation = json.load(f)
    f.close()

    for main_area in areaActorsInformation:
        result_count = ActorArea.objects.filter(name = main_area).count()

        if result_count == 0:
            main_area_obj = ActorArea.objects.create(name = main_area)

            for sub_area in  areaActorsInformation[main_area]:
                result_count_2 = ActorSubArea.objects.filter(name = sub_area,main_area = main_area_obj).count()
                if result_count_2 == 0:
                    ActorSubArea.objects.create(name = sub_area,main_area = main_area_obj)


        else:
            main_area_obj = ActorArea.objects.get(name = main_area)

            for sub_area in  areaActorsInformation[main_area]:
                result_count_2 = ActorSubArea.objects.filter(name = sub_area,main_area = main_area_obj).count()
                if result_count_2 == 0:
                    ActorSubArea.objects.create(name = sub_area,main_area = main_area_obj)

    print('Actor area/sub-area added.')  


def Update_ActorsArea():
    batch_size = 10000

    excelFile = str(Path(config.PERSIAN_PATH, 'حوزه های تنظیمگری و زیرحوزها1401415.xlsx'))
    all_sheets = pd.read_excel(excelFile,sheet_name=None) 

    arabic_char_dict = {"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ", "\u200c": " "}
    
    actor_area_dict = {}

    for area in all_sheets:
        main_area = area.replace('حوزه','').strip()
        
        for actor in all_sheets[area]['کنشگران ذیصلاح']:
            actor = actor.strip()
            if actor != 'اتاق ایران':
                actor = actor.replace(' ایران','').strip()
                
            actor = actor.replace(' ','').replace('‌','')
            
            for key, value in arabic_char_dict.items():
                actor = actor.replace(key, value)
                                
            actor_area_dict[actor] = main_area


    actor_list = Actor.objects.all()
    c = 0
    for actor in actor_list:
        actor_forms = actor.forms.split('/')

        actor_forms2 = [actor_form.replace(' ','').replace('‌','') for actor_form in actor_forms]

        for actor_form in actor_forms2:

            for key, value in arabic_char_dict.items():
                actor_form = actor_form.replace(key, value)


        if any (actor_form in actor_area_dict for actor_form in actor_forms2):
            c += 1
            
            current_actor_form =''
            for af in actor_forms2:
                if af in actor_area_dict:
                    current_actor_form = af
                    
                    area_name = actor_area_dict[current_actor_form]
                    print(area_name)

                    try:
                        area_obj = ActorArea.objects.get(name = area_name)
                        
                        actor.area = area_obj
                    except:
                        pass
                    break




    Actor.objects.bulk_update(
        actor_list,['area'],batch_size)

    print(f'Updated {c} Actor`s Area.')

def Regulators_Insert():
    arabic_char_dict = {"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ", "\u200c": " "}
    RegulatorsFile = str(Path(config.PERSIAN_PATH, 'Regulators.txt'))
    with open(RegulatorsFile, encoding="utf-8") as f:
        lines = f.readlines()
        current_area = ''
        for line in lines:
            for key, value in arabic_char_dict.items():
                line = line.replace(key, value)
            line = line.strip()  # remove space of both sides
            if '*' in line:
                area_name = line.replace('*', '')
                area_name = area_name.strip()
                current_area = area_name
                result_count = RegularityArea.objects.filter(name=area_name).count()
                # if not exist, creat
                if result_count == 0:
                    RegularityArea.objects.create(name=area_name)
            else:

                regulator_area = RegularityArea.objects.get(name=current_area)
                result_count = Regulator.objects.filter(area_id=regulator_area, name=line).count()
                try:
                    related_actor_obj = Actor.objects.get(name =line )
                except:
                    related_actor_obj = None

                # print('---------------------')
                if result_count == 0:
                    Regulator.objects.create(area_id=regulator_area, name=line,actor_id = related_actor_obj)

                else:
                    Regulator.objects.filter(area_id=regulator_area, name=line).update(
                        actor_id = related_actor_obj
                    )
    f.close()
    print('Regulators added.')

def Slogan_Insert(): 
    sloganFile = str(Path(config.PERSIAN_PATH, 'slogan.txt'))

    with open(sloganFile, encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            year = line.split(",")[0]
            content = line.split(",")[1]
            keywords = line.split(",")[2]
            result_count = Slogan.objects.filter(year=year).count()
            # if not exist, create
            if result_count == 0:
                Slogan.objects.create(year=year, content=content, keywords=keywords)
            else:
                Slogan.objects.filter(year=year).update(content=content, keywords=keywords)
    f.close()

def Slogan_Synonymous_Words_Insert():
    SloganSynonymousWordsFile = str(Path(config.PERSIAN_PATH, 'SloganSynonymousWords.json'))
    f = open(SloganSynonymousWordsFile,encoding="utf-8")
    SloganSynonymousWds = json.load(f)
    f.close()
    for year,synonymousWords in SloganSynonymousWds.items():
        synonymous_ws = '-'.join(synonymousWords)
        slgn = Slogan.objects.filter(year=year).first()
        result_count = SloganSynonymousWords.objects.filter(year = year).count()
        if result_count == 0:
            SloganSynonymousWords.objects.create(slogan = slgn,words = synonymous_ws,year = year) ##
        else:
            SloganSynonymousWords.objects.filter(year=year).update(slogan = slgn , words = synonymous_ws)

def Collective_Actors_Insert():
    # ----------  Collective Actor to DB  ---------------------
    CollectiveActorInfoFile = str(Path(config.PERSIAN_PATH, 'CollectiveActorsInfo.json'))

    # Opening JSON file
    f = open(CollectiveActorInfoFile, encoding="utf-8")
    collective_actors = json.load(f)
    f.close()

    for clc_actor_name in collective_actors:
        clc_forms_list = collective_actors[clc_actor_name]
        clc_actor_forms = ",".join(clc_forms_list)

        result_count = CollectiveActor.objects.filter(name=clc_actor_name).count()

        # if not exist, creat
        if result_count == 0:
            CollectiveActor.objects.create(name=clc_actor_name, forms=clc_actor_forms)

        else:  # update
            CollectiveActor.objects.filter(
                name=clc_actor_name).update(
                forms=clc_actor_forms)

    print('Collective-Actor Types added.')

def Operators_Insert():
    fullOperatorsInformationFile = str(Path(config.PERSIAN_PATH, 'fullOperatorsInformation.json'))

    # Opening JSON file
    f = open(fullOperatorsInformationFile, encoding="utf-8")
    operators = json.load(f)
    f.close()

    for operator_name in operators:

        operator_forms = operators[operator_name]
        operator_forms = '/'.join(operator_forms)

        operator_count = Operator.objects.filter(name=operator_name).count()

        # if not exist, creat
        if operator_count == 0:
            Operator.objects.create(name=operator_name, forms=operator_forms)
        else:
            # if exist, update
            Operator.objects.filter(
                name=operator_name).update(forms=operator_forms)

    print('Operators added')

def Template_Panels_Insert():
    Template_Panels_File = str(Path(config.PERSIAN_PATH, 'TemplatePanels.json'))

    # Opening JSON file
    f = open(Template_Panels_File, encoding="utf-8")
    Template_Panels_Data = json.load(f)
    f.close()

    panels = Template_Panels_Data['Panels']

    for panel in panels:
        panel_id = panel['id']
        panel_name = panel['name']
        page_title = panel['page_title']
        keywords_info = {
            "keyword_list": panel['keyword_list']
        }
        optional_keywords_info = {
            "optional_keyword_list": panel['optional_keyword_list']
        }

        result_count = Template_Panels_Info.objects.filter(id=panel_id).count()
        # if not exist, create
        if result_count == 0:
            Template_Panels_Info.objects.create(
                id=panel_id,
                panel_name=panel_name,
                page_title=page_title,
                keywords_info=keywords_info,
                optional_keywords_info=optional_keywords_info
            )

        else:
            # if exist, update
            Template_Panels_Info.objects.filter(panel_name=panel_name).update(
                panel_name=panel_name,
                page_title=page_title,
                keywords_info=keywords_info,
                optional_keywords_info=optional_keywords_info
            )


def Judgment_GraphType_Insert(Country):
    typecolorsFile = str(Path(config.PERSIAN_PATH, 'JudgmentGraphType.txt'))
    f = open(typecolorsFile, encoding="utf8")
    type_list = f.read().split("\n")
    for type_obj in type_list:
        name, id_field, name_field, color, prefix, is_checked = type_obj.split("\t")
        jt = JudgmentGraphType.objects.filter(country_id=Country, name=name)
        if jt.count() == 0:
            JudgmentGraphType.objects.create(country_id=Country, name=name, id_field=id_field, name_field=name_field, color=color, prefix=prefix, is_checked=is_checked)
    f.close()

def Standard_GraphType_Insert(Country):
    typecolorsFile = str(Path(config.PERSIAN_PATH, 'StandardGraphType.txt'))
    f = open(typecolorsFile, encoding="utf8")
    type_list = f.read().split("\n")
    for type_obj in type_list:
        name, id_field, name_field, color, prefix, is_checked = type_obj.split("\t")
        jt = StandardGraphType.objects.filter(country_id=Country, name=name)
        if jt.count() == 0:
            StandardGraphType.objects.create(country_id=Country, name=name, id_field=id_field, name_field=name_field, color=color, prefix=prefix, is_checked=is_checked)
    f.close()


def apply(folder_name, Country):

    t = time.time()

    print("Judgment_GraphType_Insert ...")
    Judgment_GraphType_Insert(Country)

    print("Standard_GraphType_Insert ...")
    Standard_GraphType_Insert(Country)

    print("Roles_Insert ...")
    Roles_Insert()

    print("Levels_Insert ...")
    Levels_Insert()

    print("Mesures_Insert ...")
    Mesures_Insert()

    print("Type_Colors_Insert ...")
    Type_Colors_Insert()

    print("Keywords_Insert ...")
    Keywords_Insert()

    print("Subjects_Insert ...")
    Subjects_Insert()

    print("Subjects_area_Insert ...")
    Subjects_area_Insert(Country)

    print("Update_Docs_fromExcel ...")
    Update_Docs_fromExcel(Country)

    # print("create_judgments_table_from_excel ...")
    # create_judgments_table_from_excel(Country)

    # print("update_standard_table_from_excel ...")
    # update_standard_table_from_excel(Country)

    print("LegalOrientations_Insert ...")
    LegalOrientations_Insert()

    print("RegularityTools_Insert ...")
    RegularityTools_Insert()

    #---------- Order is important! -----------------------
    print("ActorRolePatternKeywords_Insert ...")
    ActorRolePatternKeywords_Insert()

    print("Actors_Insert ...")
    Actors_Insert()

    print("Actor_Graph_Types_Insert ...")
    Actor_Graph_Types_Insert()


    print("Area_SubArea_Insert ...")
    Area_SubArea_Insert()

    print("Update_ActorsArea ...")
    Update_ActorsArea()
    # --------------------------------

    print("Regulators_Insert ...")
    Regulators_Insert()

    print("Slogan_Insert ...")
    Slogan_Insert()

    print("Slogan_Synonymous_Words_Insert ...")
    Slogan_Synonymous_Words_Insert()

    print("Collective_Actors_Insert ...")
    Collective_Actors_Insert()

    print("Operators_Insert ...")
    Operators_Insert()

    print("Template_Panels_Insert ...")
    Template_Panels_Insert()

    print("Books_Similarity_Type_Insert ...")
    book_similarity()


    print("Rahbari_Insert_fromExcel ...")
    Rahbari_Insert_fromExcel(Country)

    print("Rahbari_Search_Parameters_Insert ...")
    Rahbari_Search_Parameters_Insert(Country)

    
    print("time ", time.time() - t)

def Slogan_Key_And_Synonymous_Words_Insert():
    t = time.time()

    #---------- Order is important! -----------------------
    
    print("Slogan_Insert ...")
    Slogan_Insert()

    print("Slogan_Synonymous_Words_Insert ...")
    Slogan_Synonymous_Words_Insert()

    # --------------------------------

    print("time ", time.time() - t)


def create_judgments_table_from_excel(Country):
    t = time.time()

    print("Update_Judgment_Search_Parameter ...")
    update_judgment_search_parameter()

    print("Judgments_Insert_fromExcel ...")
    Judgments_Insert_fromExcel(Country)

    from es_scripts import IngestJudgmentsToElastic
    from doc.models import Country as C

    file = get_object_or_404(C, id=Country.id)    
    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestJudgmentsToElastic.apply(folder_name, file)

    from scripts.Persian import FindSubjectComplaint
    FindSubjectComplaint.apply(None, Country)

    print("Judgment_Search_Parameters_Insert ...")
    Judgment_Search_Parameters_Insert(Country)

    IngestJudgmentsToElastic.apply(folder_name, file)

    print("time ", time.time() - t)   


def create_standard_table_from_excel(folder_name,Country):
    t = time.time()
    
    # print('Update_Standard_Search_Parameter')
    # update_standard_search_parameter()

    # print("Standards_Insert_fromExcel ...")
    # Standards_Insert_fromExcel(Country)

    print("StandardSearchParameters_Insert ...")
    StandardSearchParameters_Insert(Country)


    # print("update_file_name_extention ...")
    # update_file_name_extention(folder_name, Country)

    # print("revoked_types_to_db ...")
    # revoked_types_to_db(Country)

    print("time ", time.time() - t)


def update_file_name_extention(folder_name,Country):
    batch_size = 10000
    result_dict = {}
    dataPath = str(Path(config.DATA_PATH, folder_name))

    all_files = glob.glob(dataPath + "/*")
    for file in all_files:

        file_name_with_extention = str(os.path.basename(file))
        format = file_name_with_extention.split(".")[-1]
        base_file_name = file_name_with_extention.split(".")[0]

        if format.lower() == "doc":
            result_dict[base_file_name] = file_name_with_extention

    all_stan_docs = Standard.objects.filter(document_id__country_id__id = Country.id)
    updated_count = 0
    for doc in all_stan_docs:
        try:
            doc.file_name_with_extention = result_dict[doc.standard_number]
            updated_count += 1
        except:
            print('Not found!')

    Standard.objects.bulk_update(all_stan_docs,['file_name_with_extention'],batch_size)
    
    print(f'{updated_count}/{len(all_stan_docs)}')

def Search_Parameters_Insert(Country):

   
    SearchParameters.objects.filter(country__id = Country.id).delete()

    parameters = {
        "level":Level,
        "subject":Subject,
        "type":Type,
        "approval_reference":ApprovalReference,
        "subject_area_id": SubjectArea,
        "subject_sub_area_id": SubjectSubArea,
    }


    for parameter,model_name in parameters.items():
        add_parameter_values(Country,parameter,model_name)

    # ----------------------------------------------
    result_tag = ''
    
    documents_list = Document.objects.filter(
        country_id_id=Country.id, approval_date__isnull=False)

    min_year_res = -1
    max_year_res = -1
    if documents_list.count() > 0:
        max_year = documents_list.aggregate(Max('approval_date'))[
                       "approval_date__max"][0:4]
        min_year = documents_list.aggregate(Min('approval_date'))[
                       "approval_date__min"][0:4]
        
        min_year_res = int(min_year) - 1
        max_year_res = int(max_year) + 1

    if max_year_res != -1 and min_year_res != -1 : 
        for  i in range(max_year_res,(min_year_res-1),-1):
            tag = "<option value=" + str(i) + " >" + str(i) + "</option>"
            result_tag += tag

        json_result = {
            "options":result_tag
        }

        SearchParameters.objects.create(
            country=Country, parameter_name= "FromYear",parameter_values = json_result)

        SearchParameters.objects.create(
            country=Country, parameter_name= "ToYear",parameter_values = json_result) 
    # ----------------------------------------------
    result_tag = ''
    revoked_type_list =  RevokedType.objects.all().values()

    for r_type in revoked_type_list:
        revoked_type_id = r_type['id']
        revoked_type_name = r_type['name']
        tag = "<option value=" + str(revoked_type_id) + " >" + revoked_type_name + "</option>"
        result_tag += tag
        
    json_result = {
        "options":result_tag
    }

    SearchParameters.objects.create(
        country=Country, parameter_name= "ValidationType",parameter_values = json_result)

    # ----------------------------------------------
    result_tag = ''
    find_org_id = ActorCategory.objects.get(name = 'سازمان').id
    organization_type_list =  Actor.objects.filter(actor_category_id__id=find_org_id).values('name')

    for o_type in organization_type_list:
        organization_type_name = o_type['name']
        tag = "<option value='" + organization_type_name + "'>" + organization_type_name + "</option>"
        result_tag += tag
        
    json_result = {
        "options":result_tag
    }

    SearchParameters.objects.create(
        country=Country, parameter_name= "OrganizationType",parameter_values = json_result)

def add_parameter_values(Country,parameter,model_name):
        value = parameter + "_id"
        order_by = value + "__name"

        documents_list = Document.objects.filter(country_id_id=Country.id).values(value).order_by(
            order_by).distinct()

        result_tag = ""
        for row in documents_list:
            parameter_id = row[value]
            if parameter_id is not None:
                para_obj = model_name.objects.get(id=parameter_id)
                parameter_id = para_obj.id
                parameter_name = para_obj.name

                tag = "<option value=" + str(parameter_id) + " >" + parameter_name + "</option>"

                if parameter_name not in [""," ",None]:
                    result_tag += tag

        json_result = {
            "options":result_tag
        }
        SearchParameters.objects.create(
            country=Country, parameter_name= parameter,parameter_values = json_result)


def book_similarity():
    similarityFile = str(Path(config.PERSIAN_PATH, 'BookSimilarityMeasures.txt'))
    with open(similarityFile, encoding="utf8") as f:
        lines = f.readlines()
        for type in lines:
            type = type.replace("\n", "")
            result_count = SimilarityType.objects.filter(name=type).count()
            if result_count == 0:
                SimilarityType.objects.create(name=type)
    f.close()        


def update_judgment_search_parameter():
    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation_full.xlsx'))

    df = pd.read_excel(excelFile)
    df = df.drop_duplicates(subset=['id'])
    df = df.fillna('')

    for i in range(len(df['categories'])):
        category = str(df['categories'][i])
        p_index = category.rfind('(')
        df['categories'][i] = category[:p_index]

    search_parameters_list = [
        [df['conclusion_display_name'].unique(), JudgmentConclusionDisplayName],
        [df['subject_type_display_name'].unique(), JudgmentSubjectTypeDisplayName],
        [df['judgment_type'].unique(), JudgmentType],
        [df['categories'].unique(), JudgmentCategories],
    ]


    for search_parameters in search_parameters_list:
        search_parameter = search_parameters[0]
        search_parameter_model = search_parameters[1]
        search_parameter_model_list = search_parameter_model.objects.all().values_list('name', flat=True)
        # search_parameter_model.objects.all().delete()
        CreateList = []
        for search_parameter_value in search_parameter:
            if not search_parameter_value:
                continue
            # search_parameter_value = arabic_preprocessing(search_parameter_value)
            if search_parameter_value not in search_parameter_model_list:
                new_obj = search_parameter_model(name=search_parameter_value)
                CreateList.append(new_obj)
        search_parameter_model.objects.bulk_create(CreateList)

    AllJudgmentJudge = JudgmentJudge.objects.all().values_list('name', flat=True)
    JudgmentJudgeObjects = []
    judge_unique_name_list = list(set(judge_name_dict.values()))
    for judge_name in judge_unique_name_list:
        if judge_name in AllJudgmentJudge:
            continue
        forms = [name for name in judge_name_dict if judge_name_dict.get(name) in [judge_name]]
        forms = '/'.join(forms)
        new_judge = JudgmentJudge(name=judge_name, forms=forms)
        JudgmentJudgeObjects.append(new_judge)
    JudgmentJudge.objects.bulk_create(JudgmentJudgeObjects)


def Judgments_Insert_fromExcel(Country):
    excelFile = str(Path(config.PERSIAN_PATH, 'db_legislation_full.xlsx'))

    df = pd.read_excel(excelFile)
    df = df.drop_duplicates(subset=['id'])
    df = df.fillna('نامشخص')

    for i in range(len(df['categories'])):
        category = str(df['categories'][i])
        p_index = category.rfind('(')
        df['categories'][i] = category[:p_index]

    # judgments insert
    dataframe_dictionary = DataFrame2Dict(df, "id", [
        "statement_digest", "judgment_number", "judgment_approve_date_persian", "complaint_serial",
        "conclusion_display_name", "subject_type_display_name", "judgment_type", "complainant",
        "complaint_from", "laws", "categories"
    ])

    Judgment.objects.filter(document_id__country_id=Country).delete()

    new_judgs = []

    documents_queryset = Document.objects.filter(file_name__in=dataframe_dictionary.keys(), country_id__id=Country.id)
    documents_dictionary = {document.file_name: document for document in documents_queryset}
    conclusion_display_name_queryset = JudgmentConclusionDisplayName.objects.all()
    conclusion_display_name_dictionary = {conclusion_display_name.name: conclusion_display_name for conclusion_display_name in conclusion_display_name_queryset}
    subject_type_display_name_queryset = JudgmentSubjectTypeDisplayName.objects.all()
    subject_type_display_name_dictionary = {subject_type_display_name.name: subject_type_display_name for subject_type_display_name in subject_type_display_name_queryset}
    judgment_type_queryset = JudgmentType.objects.all()
    judgment_type_dictionary = {judgment_type.name: judgment_type for judgment_type in judgment_type_queryset}
    categories_queryset = JudgmentCategories.objects.all()
    categories_dictionary = {categories.name: categories for categories in categories_queryset}

    for id in dataframe_dictionary:
        document=documents_dictionary.get(str(id))
        if document is not None:
            conclusion_display_name = conclusion_display_name_dictionary.get(dataframe_dictionary[id]['conclusion_display_name'])
            subject_type_display_name = subject_type_display_name_dictionary.get(dataframe_dictionary[id]['subject_type_display_name'])
            judgment_type = judgment_type_dictionary.get(dataframe_dictionary[id]['judgment_type'])
            categories = categories_dictionary.get(dataframe_dictionary[id]['categories'])
            
            new_judg = Judgment(
                document_id=document,
                judgment_number=dataframe_dictionary[id]['judgment_number'],
                judgment_date=dataframe_dictionary[id]['judgment_approve_date_persian'],
                judgment_year=dataframe_dictionary[id]['judgment_approve_date_persian'][:4],
                complaint_serial=dataframe_dictionary[id]['complaint_serial'],
                conclusion_display_name=conclusion_display_name,
                subject_type_display_name=subject_type_display_name,
                judgment_type=judgment_type,
                complainant=dataframe_dictionary[id]['complainant'],
                complaint_from=dataframe_dictionary[id]['complaint_from'],
                affected_document_name=dataframe_dictionary[id]['laws'],
                affected_document=None,
                categories=categories
            )
            new_judgs.append(new_judg)
            document.name = dataframe_dictionary[id]['statement_digest']

    Judgment.objects.bulk_create(new_judgs)
    Document.objects.bulk_update(documents_queryset, ['name'])


judge_name_dict = {
    'حکمتعلی مظفری': 'حکمتعلی مظفری',
    'محمد مصدقی': 'محمد مصدقی',
    'محمدکاظم بهرامی': 'محمد کاظم بهرامی',
    'محمد کاظم بهرامی': 'محمد کاظم بهرامی',
    'رهبرپور': 'رهبرپور',
    'علی رازینی': 'علی رازینی',
    'قربانعلی دری نجف آبادی': 'قربانعلی دری نجف آبادی',
    'محمد رضا عباسی فردوسی': 'محمد رضا عباسی فردوسی',
    'مقدسی‎فرد': 'مقدسی فرد',
    'محمد رضا عباسی‌فرد': 'محمدرضا عباسی فرد',
    'مرتضی علی اشراقی': 'مرتضی علی اشراقی',
    'محمدجعفر منتظری': 'محمد جعفر منتظری',
    'محمد جعفر منتظری': 'محمد جعفر منتظری',
    'علی مبشری': 'علی مبشری',
    'مبشری': 'علی مبشری',
    'قدیانی': 'قدیانی',
    'رهبر پور': 'رهبرپور',
    'مقدسی‎ فرد': 'مقدسی فرد',
    'سیدابوالفضل موسوی تبریزی': 'سید ابوالفضل موسوی تبریزی',
    'سید ابوالفضل موسوی تبریزی': 'سید ابوالفضل موسوی تبریزی',
    'اسماعیل فردوسی‌پور': 'اسماعیل فردوسی پور',
    'اسماعیل فردوسی پور': 'اسماعیل فردوسی پور',
    'محمدرضا عباسی‌فرد': 'محمدرضا عباسی فرد',
    'محمدرضا عباسی فرد': 'محمدرضا عباسی فرد',
    'محمدعلی فیض': 'محمدعلی فیض',
    'محمد علی فیض': 'محمدعلی فیض',
    'غلامرضا رضوانی': 'غلامرضا رضوانی',
    'محمد امامی کاشانی': 'محمد امامی کاشانی'
}


def Judgment_Search_Parameters_Insert(Country):    
    JudgmentSearchParameters.objects.filter(country__id = Country.id).delete()

    parameters = {
        "conclusion_display_name": JudgmentConclusionDisplayName,
        "subject_type_display_name": JudgmentSubjectTypeDisplayName,
        "judgment_type": JudgmentType,
        "categories": JudgmentCategories,
        "judge_name": JudgmentJudge,
    }


    for parameter,model_name in parameters.items():
        judgment_add_parameter_values(Country,parameter,model_name)

    # ----------------------------------------------
    result_tag = ''
    
    # documents_list = Document.objects.filter(
    #     country_id_id=Country.id, approval_date__isnull=False)

    min_year_res = 1300
    max_year_res = 1402
    # if documents_list.count() > 0:
    #     max_year = documents_list.aggregate(Max('approval_date'))[
    #                    "approval_date__max"][0:4]
    #     min_year = documents_list.aggregate(Min('approval_date'))[
    #                    "approval_date__min"][0:4]
        
    #     min_year_res = int(min_year) - 1
    #     max_year_res = int(max_year) + 1

    if max_year_res != -1 and min_year_res != -1 : 
        for  i in range(max_year_res,(min_year_res-1),-1):
            tag = "<option value=" + str(i) + " >" + str(i) + "</option>"
            result_tag += tag

        json_result = {
            "options":result_tag
        }

        JudgmentSearchParameters.objects.create(
            country=Country, parameter_name= "FromYear",parameter_values = json_result)

        JudgmentSearchParameters.objects.create(
            country=Country, parameter_name= "ToYear",parameter_values = json_result) 


def judgment_add_parameter_values(Country,parameter,model_name):
    value = parameter + "_id"
    order_by = value + "__name"

    documents_list = Judgment.objects.filter(document_id__country_id=Country).values(value).order_by(
        order_by).distinct()

    result_tag = ""
    for row in documents_list:
        parameter_id = row[value]
        if parameter_id is not None:
            para_obj = model_name.objects.get(id=parameter_id)
            parameter_id = para_obj.id
            parameter_name = para_obj.name

            tag = "<option value=" + str(parameter_id) + " >" + parameter_name + "</option>"

            if parameter_name not in ["",None]:
                result_tag += tag

    json_result = {
        "options":result_tag
    }
    JudgmentSearchParameters.objects.create(
        country=Country, parameter_name= parameter,parameter_values = json_result)


def update_standard_search_parameter():
    excelFile = str(Path(config.PERSIAN_PATH, 'Standard.xlsx'))

    df = pd.read_excel(excelFile)
    df = df.drop_duplicates(subset=['standard_number'])
    df = df.fillna('')

    search_parameters_list = [
        [df['branch'].unique(), Standard_Branch],
        [df['status'].unique(), Standard_Status],
    ]

    for search_parameters in search_parameters_list:
        search_parameter = search_parameters[0]
        search_parameter_model = search_parameters[1]
        search_parameter_model_list = search_parameter_model.objects.all().values_list('name', flat=True)
        # search_parameter_model.objects.all().delete()
        CreateList = []
        for search_parameter_value in search_parameter:
            if not search_parameter_value:
                continue
            # search_parameter_value = arabic_preprocessing(search_parameter_value)
            if search_parameter_value not in search_parameter_model_list:
                new_obj = search_parameter_model(name=search_parameter_value)
                CreateList.append(new_obj)
        search_parameter_model.objects.bulk_create(CreateList)


def Standards_Insert_fromExcel(Country):
    excelFile = str(Path(config.PERSIAN_PATH, 'Standard.xlsx'))

    df = pd.read_excel(excelFile)
    df = df.drop_duplicates(subset=['standard_number'])
    df = df.fillna('')

    # standards insert
    Standard.objects.filter(document_id__country_id=Country).delete()
    dataframe_dictionary = DataFrame2Dict(df, "standard_number", ["subject",'approval_year','ICS','branch','status'])

    new_stas = []

    documents_queryset = Document.objects.filter(country_id=Country)
    documents_dictionary = {str(document.file_name): document for document in documents_queryset}
    branch_queryset = Standard_Branch.objects.all()
    branch_dictionary = {branch.name: branch for branch in branch_queryset}
    status_queryset = Standard_Status.objects.all()
    status_dictionary = {status.name: status for status in status_queryset}

    for id in documents_dictionary.keys():
        document = documents_dictionary[id]

        if dataframe_dictionary.get(id):
            branch = branch_dictionary.get(dataframe_dictionary[id]['branch'])
            status = status_dictionary.get(dataframe_dictionary[id]['status'])
            
            new_sta = Standard(
                document_id=document,
                standard_number=id,
                subject=dataframe_dictionary[id]['subject'],
                approval_year=dataframe_dictionary[id]['approval_year'],
                ICS=dataframe_dictionary[id]['ICS'],
                branch=branch,
                status=status,
            )
            new_stas.append(new_sta)
            document.name = dataframe_dictionary[id]['subject']

        else:
            new_sta = Standard(
                document_id=document,
                standard_number=id,
                subject= 'نامشخص' + '(' + id + ')',
            )
            new_stas.append(new_sta)   
            document.name = 'نامشخص' + '(' + id + ')' 


    Standard.objects.bulk_create(new_stas)
    Document.objects.bulk_update(documents_queryset, ['name'])

    from scripts.Persian import DocsCreateDocumentsListCubeData
    DocsCreateDocumentsListCubeData.apply(None,Country) 

    document_cube_queryset = CUBE_DocumentJsonList.objects.filter(country_id=Country)
    document_cube_dictionary = {str(document.document_id.file_name): document for document in document_cube_queryset}

    for id in document_cube_dictionary.keys():
        branch = 'نامشخص'
        if dataframe_dictionary.get(id):
            branch = branch_dictionary.get(dataframe_dictionary[id]['branch']).name
        document_cube = document_cube_dictionary[id]
        json_text = document_cube.json_text
        json_text['branch'] = branch
        document_cube.json_text = json_text

    CUBE_DocumentJsonList.objects.bulk_update(document_cube_queryset, ['json_text'])


def StandardSearchParameters_Insert(Country):    
   
    StandardSearchParameters.objects.filter(country__id = Country.id).delete()

    parameters = {
        "branch": Standard_Branch,
        "status": Standard_Status,
    }

    for parameter,model_name in parameters.items():
        standard_add_parameter_values(Country,parameter,model_name)

    # ----------------------------------------------
    result_tag = ''
    

    min_year_res = 1300
    max_year_res = 1402


    if max_year_res != -1 and min_year_res != -1 : 
        for  i in range(max_year_res,(min_year_res-1),-1):
            tag = "<option value=" + str(i) + " >" + str(i) + "</option>"
            result_tag += tag

        json_result = {
            "options":result_tag
        }

        StandardSearchParameters.objects.create(
            country=Country, parameter_name= "FromYear",parameter_values = json_result)

        StandardSearchParameters.objects.create(
            country=Country, parameter_name= "ToYear",parameter_values = json_result)


def standard_add_parameter_values(Country,parameter,model_name):
    result_tag = ""
    parameter_object_list = model_name.objects.all().order_by('name')
    for parameter_object in parameter_object_list:
        parameter_id = parameter_object.id
        parameter_name = parameter_object.name

        tag = "<option value=" + str(parameter_id) + " >" + parameter_name + "</option>"

        if parameter_name not in ["",None]:
            result_tag += tag

    json_result = {
        "options":result_tag
    }
    StandardSearchParameters.objects.create(
        country=Country, parameter_name= parameter,parameter_values = json_result)
    # ----------------------------------------
    if parameter == "branch":
        result_tag = ""
        parameter_object_list = model_name.objects.all().order_by('name')
        for parameter_object in parameter_object_list:
            parameter_id = parameter_object.id
            parameter_name = parameter_object.name
            subject_category = parameter_name.replace('کمیته ملی','').strip()

            tag = "<option value=" + str(parameter_id) + " >" + subject_category + "</option>"

            if subject_category != None:
                result_tag += tag

        json_result = {
            "options":result_tag
        }
        StandardSearchParameters.objects.create(
            country=Country, parameter_name= "SubjectCategory",parameter_values = json_result)       



def revoked_types_to_db(Country):

    RevokedTypesFile = str(Path(config.PERSIAN_PATH, 'RevokedTypes.txt'))

    with open(RevokedTypesFile, encoding="utf8") as f:
        lines = f.readlines()
        for r_type in lines:
            r_type = r_type.replace("\n", "")
            result_count = RevokedType.objects.filter(name=r_type).count()
            if result_count == 0:
                RevokedType.objects.create(name=r_type)
    f.close()



def Rahbari_Update_Fields_From_File(folder_name,Country):
    from scripts.Persian import Preprocessing

    excelFile = str(Path(config.PERSIAN_PATH, 'Rahbari_Excel.xlsx'))
    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df = df.fillna('نامشخص')

    excel_data_dict = {}
    for index, row in df.iterrows():
        title = row["title"]
        TasvibDate = row["TasvibDate"]
        data_list = {"labels":row['labels'],"type":row['type']}

        doc_key = title + "_" +TasvibDate
        excel_data_dict[doc_key] = data_list


    dataPath = str(Path(config.DATA_PATH, folder_name))
    all_files = Preprocessing.readFiles(dataPath, preprocess=False)
    file_data_dict = {}

    for file_name,text in all_files.items():
        file_name = standardFileName(file_name)

        second_line = text.split('\n')[1].strip()

        if second_line.count('/') == 2:
            TasvibDate = second_line
            file_data_dict[file_name] = TasvibDate

    # ------ update doc approval date --------------------
    result_docs = Document.objects.filter(
        country_id__id =Country.id
    )
    doc_counter = 0
    doc_count = result_docs.count()

    for doc in result_docs:
        file_name = standardFileName(doc.file_name)

        try:
            approval_date = file_data_dict[file_name]
            doc_key = file_name + "_" +approval_date
            doc.approval_date = approval_date
        except:
            pass

        doc_counter += 1
        print(f"{doc_counter}/{doc_count}")

    Document.objects.bulk_update(
        result_docs,['approval_date'])

    # ------ update rahbari  --------------------
    rahbari_docs = Rahbari.objects.filter(
        document_id__country_id__id =Country.id
    )

    doc_counter = 0
    doc_count = rahbari_docs.count()
    for doc in rahbari_docs:
        file_name = standardFileName(doc.document_id.file_name) 
        approval_date = file_data_dict[file_name]
        approval_year = approval_date[:4] if approval_date is not None and len(approval_date) > 4 else 0

        try:
            doc_key = file_name + "_" +approval_date
            labels = excel_data_dict[doc_key]["labels"]

            doc.rahbari_date = approval_date
            doc.rahbari_year = approval_year
            doc.labels = labels
        except:
            pass

        doc_counter += 1
        print(f"{doc_counter}/{doc_count}")
    Rahbari.objects.bulk_update(
        rahbari_docs,['rahbari_date','rahbari_year','labels'])


def Rahbari_Insert_fromExcel(Country):
    excelFile = str(Path(config.PERSIAN_PATH, 'Rahbari_Full_Excel.xlsx'))

    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df['limited_title'] = df['limited_title'].apply(lambda x: standardFileName(x))
    df = df.fillna('نامشخص')

    # documents update
    dataframe_dictionary = DataFrame2Dict(df, "limited_title", ["TasvibDate", "labels", "type","title"])

    Rahbari.objects.filter(document_id__country_id=Country).delete()

    documents = Document.objects.filter(country_id__id=Country.id)

    for doc in documents:
        if standardFileName(doc.file_name) in dataframe_dictionary.keys():
            document_id = doc.id
            document_name = doc.name
            document_file_name = doc.file_name
            document_date= doc.approval_date if doc.approval_date is not None else "نامشخص"
            document_year = doc.approval_date[:4] if doc.approval_date is not None and len(doc.approval_date) > 4 else 0
            document_labels = dataframe_dictionary[standardFileName(document_file_name)]["labels"]
            document_type = dataframe_dictionary[standardFileName(document_file_name)]["type"]

            type_obj = Type.objects.get(name=document_type)
            Document.objects.filter(id=document_id).update(type_id=type_obj, type_name=type_obj.name)

            Rahbari.objects.create(document_id=doc, document_name=document_name, document_file_name=document_file_name,
                                   rahbari_date=document_date, rahbari_year=document_year, labels=document_labels, type=type_obj)

    # from doc.models import Country as C
    # file = get_object_or_404(C, id=Country.id)
    # my_file = file.file.path
    # my_file = str(os.path.basename(my_file))
    # dot_index = my_file.rfind('.')
    # folder_name = my_file[:dot_index]
    # #
    # from es_scripts import IngestRahbariToElastic
    # IngestRahbariToElastic.apply(folder_name, file)


def Rahbari_Search_Parameters_Insert(Country):
    RahbariSearchParameters.objects.filter(country__id=Country.id).delete()

    parameters = {
        "type": JudgmentConclusionDisplayName,
        "labels": JudgmentSubjectTypeDisplayName,
    }

    # -------------- Type --------------------------------
    RahbariList = Rahbari.objects.all()
    added_type = []
    result_tag = ""
    for item in RahbariList:
        if item.type.id not in added_type:
            tag = "<option value=" + str(item.type.id) + " >" + str(item.type.name) + "</option>"
            result_tag += tag
            added_type.append(item.type.id)

    json_result = {"options": result_tag}
    RahbariSearchParameters.objects.create(
        country=Country, parameter_name="Type", parameter_values=json_result)

    # -------------- Labels --------------------------------
    Rahbari_labels = Rahbari.objects.all().values("labels")
    added_labels = []
    result_tag = ""
    for t in Rahbari_labels:
        label_list = t["labels"].split("؛")
        for label_item in label_list:
            label_item = label_item.strip().replace("؛", "")
            if label_item.replace(" ", "").replace("\u200c", "") not in added_labels:
                tag = "<option value='" + str(label_item) + "' >" + str(label_item) + "</option>"
                result_tag += tag
                added_labels.append(label_item.replace(" ","").replace("\u200c", ""))

    json_result = {"options": result_tag}
    RahbariSearchParameters.objects.create(
        country=Country, parameter_name="Labels", parameter_values=json_result)


    # -------------- Year --------------------------------
    result_tag = ''
    min_year_res = 1300
    max_year_res = 1401
    if max_year_res != -1 and min_year_res != -1:
        for i in range(max_year_res, (min_year_res - 1), -1):
            tag = "<option value=" + str(i) + " >" + str(i) + "</option>"
            result_tag += tag

        json_result = {
            "options": result_tag
        }

        RahbariSearchParameters.objects.create(
            country=Country, parameter_name="FromYear", parameter_values=json_result)

        RahbariSearchParameters.objects.create(
            country=Country, parameter_name="ToYear", parameter_values=json_result)


def clustering_algorithms_to_db(Country):
    CreateList = []

    algorithm_abbreviation_dict = {
        "K-Means":"KMS",
        "Agglomerative":"AGG",
        "FCM":"FCM",
        "LDA":"LDA"
    }

    vector_abbreviation_dict = {
        "TF-IDF":"T",
        "LDA":"L",
        "BERT":"B"
    }

    min_k = 2
    max_k = 100
    step = 1

    ClusteringAlorithm.objects.all().delete()

    ClusteringAlgorithmsFile = str(Path(config.PERSIAN_PATH, 'ClusteringAlgorithms.txt'))
    DocumentVectorTypesFile = str(Path(config.PERSIAN_PATH, 'DocumentVectorTypes.txt'))

    vector_names = []

    with open(DocumentVectorTypesFile, encoding="utf8") as f:
        lines = f.readlines()
        for vector_name in lines:
            vector_name = vector_name.replace("\n", "")
            vector_names.append(vector_name)
    f.close()

    ngram_types = [(1,1),(2,2)]
    with open(ClusteringAlgorithmsFile, encoding="utf8") as f:
        lines = f.readlines()
        for c_name in lines:
            c_name = c_name.replace("\n", "")

            for vector_name in vector_names:

                for cluster_count in range(min_k, (max_k + 1), step):

                    for ngram in ngram_types:
                        ngram = str(ngram)
                        result_count = ClusteringAlorithm.objects.filter(
                        name=c_name,
                        ngram_type = ngram,
                        input_vector_type = vector_name,
                        cluster_count = cluster_count).count()

                        alg_abbreviation = algorithm_abbreviation_dict[c_name]
                        vec_abbreviation = vector_abbreviation_dict[vector_name]

                        res_abbreviation = alg_abbreviation + "-" + str(cluster_count) + "-" + ngram + "-" + vec_abbreviation


                        if result_count == 0:
                            ClusteringAlorithm_obj = ClusteringAlorithm(name=c_name,
                            input_vector_type = vector_name,
                            cluster_count = cluster_count,
                            ngram_type = ngram,
                            abbreviation = res_abbreviation)
                            CreateList.append(ClusteringAlorithm_obj)
                        else:

                            ClusteringAlorithm.objects.filter(
                            name=c_name,
                            ngram_type = ngram,
                            input_vector_type = vector_name,
                            cluster_count = cluster_count
                            ).update(
                                abbreviation = res_abbreviation)


    f.close()



    ClusteringAlorithm.objects.bulk_create(CreateList)

    feature_selection_algorithms_to_db(Country)



def feature_selection_algorithms_to_db(Country):
    
    FeatureSelectionAlgorithmsFile = str(Path(config.PERSIAN_PATH, 'FeatureSelectionAlgorithms.txt'))

    with open(FeatureSelectionAlgorithmsFile, encoding="utf8") as f:
        lines = f.readlines()
        for f_name in lines:
            f_name = f_name.replace("\n", "")
            result_count = FeatureSelectionAlgorithm.objects.filter(name=f_name).count()

            if result_count == 0:
                FeatureSelectionAlgorithm.objects.create(name=f_name)
    f.close()


def rahbari_labels_to_db(Country):
    RahbariLabel.objects.all().delete()
    rahbari_labels = Rahbari.objects.all().values("id",'labels')

    CreateList = []
    added_labels = []
    
    for row in rahbari_labels:
        label_list = row["labels"].split("؛")
        for label_item in label_list:
            label_item = label_item.strip().replace("؛", "").replace("ورزش‌کاران", "ورزشکاران")
            no_space_label_item = label_item.replace(" ", "").replace("\u200c", "")
            if no_space_label_item not in added_labels:
                if label_item not in [None,'','نامشخص']:
                    added_labels.append(no_space_label_item)
                    label_obj = RahbariLabel(name=label_item)
                    CreateList.append(label_obj)
    RahbariLabel.objects.bulk_create(CreateList)
