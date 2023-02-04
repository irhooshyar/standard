from argparse import Action
import json
from os import name
import re

from abdal import config
from pathlib import Path

from en_doc.models import ApprovalReference, Document, Measure, Level, Actor

import pandas as pd

from scripts.English.Preprocessing import standardFileName, Preprocessing

def Measure_to_DB():
    measureFile = str(Path(config.PERSIAN_PATH, 'measure.txt'))

    with open(measureFile, encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            persian_name = line.split(",")[0]
            english_name = line.split(",")[1]
            type = line.split(",")[2]
            result_count = Measure.objects.filter(persian_name=persian_name, english_name=english_name).count()
            # if not exist, creat
            if result_count == 0:
                Measure.objects.create(persian_name=persian_name, english_name=english_name, type=type)
            else:
                Measure.objects.filter(persian_name=persian_name, english_name=english_name).update(type=type)
    f.close()

def Level_to_DB():
    levelsFile = str(Path(config.ENGLISH_PATH, 'Levels.txt'))
    with open(levelsFile, encoding="utf8") as f:
        lines = f.readlines()
        for level in lines:
            level = level.replace("\n", "")
            result_count = Level.objects.filter(name=level).count()
            # if not exist, create
            if result_count == 0:
                Level.objects.create(name=level)
    f.close()

def ApprovalReference_to_DB():
    levelsFile = str(Path(config.ENGLISH_PATH, 'ApprovalReference.txt'))
    with open(levelsFile, encoding="utf8") as f:
        lines = f.readlines()
        for level in lines:
            level = level.replace("\n", "")
            result_count = ApprovalReference.objects.filter(name=level).count()
            # if not exist, create
            if result_count == 0:
                ApprovalReference.objects.create(name=level)
    f.close()

def Excel_Update_DB(Country):
    documentList = Document.objects.filter(country_id=Country)

    excelFile = str(Path(config.ENGLISH_PATH, 'files_ukus.xlsx'))
    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df = df.drop_duplicates(subset=['title'])

    # approval Level table insertion
    level_list = df['type'].unique()

    for level in level_list:
        if level in ["نامشخص", "Unknown"]:
            continue
        result_count = Level.objects.filter(name=level).count()
        if result_count == 0:
            Level.objects.create(name=level)

    # documents update
    for document in documentList:
        document_id = document.id
        document_name_preprocess = standardFileName(document.name)
        result_count = len(df.loc[df['title'] == document_name_preprocess])
        if result_count > 0:
            # print("found in excel no preprocess")
            location = df.loc[df['title'] == document_name_preprocess]
            year = location['year'].iloc[0]
            level = location['type'].iloc[0]
            # print(f"title:{level}")
            if level in ["نامشخص", "Unknown"]:
                continue
            level_id = Level.objects.get(name=level).id
            Document.objects.filter(id=document_id).update(level_id_id=level_id, level_name=level, approval_date=year)

def Actors_to_DB():
    actorsFile = str(Path(config.ENGLISH_PATH, 'Actors_en.txt'))
    lines = open(actorsFile, encoding="utf8").read().split("\n")

    for actor in lines:

        actor_list = actor.split(" ")

        for i in range(actor_list.__len__()):
            if sum(1 for c in actor_list[i] if c.isupper()) <= 1:
                actor_list[i] = actor_list[i].lower()

        actor = " ".join(actor_list)

        if actor != "" and ( (actor[0] == "*" and actor[1] != "*") or actor[0] != "*"):
            result_count = Actor.objects.filter(name=actor).count()
            if result_count == 0:
                Actor.objects.create(name=actor)

def apply(folder_name, Country):

    print("Measure_to_DB")
    Measure_to_DB()

    print("Level_to_DB")
    Level_to_DB()

    print("ApprovalReference_to_DB")
    ApprovalReference_to_DB()

    print("Excel_Update_DB")
    Excel_Update_DB(Country)

    print("Actors_to_DB")
    Actors_to_DB()

