import operator
from functools import reduce
import heapq
from jdatetime import datetime as jdatetime
from django.shortcuts import redirect, get_object_or_404
import os
import re
from hazm import *
from django.forms import FileField
from doc.forms import ZipFileForm
from doc.models import *
from django.db.models import Avg
from es_scripts.persian_automate import ExecutiveClausesExtractor
from es_scripts.util.Clause import get_clause_by_paragraph, get_paragraphs_by_clause, get_document_paragraphs
from scripts import ZipFileExtractor, StratAutomating
from abdal import es_config
import shutil
import after_response
from django.http import JsonResponse, HttpResponse
from scripts.Persian import Preprocessing
from django.db.models import Max, Min, F, IntegerField, Count, Q
from django.db.models.functions import Substr, Cast, Length
from django.core.files.storage import FileSystemStorage
import docx2txt
import datetime
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
import pdfplumber
from zipfile import ZipFile
from abdal import config
from pathlib import Path
import json
from multilingual_pdf2text.pdf2text import PDF2Text
from multilingual_pdf2text.models.document_model.document import Document as PDF_Document
import math
from urllib.parse import urlparse
from itertools import chain, groupby
from collections import Counter
import numpy as np
from operator import itemgetter
from numpy import dot
from numpy.linalg import norm
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from .decorators import allowed_users, unathenticated_user, is_login
from .const import *
import glob
from elasticsearch import Elasticsearch
from sklearn.metrics.pairwise import cosine_similarity
import string
from scripts.Persian.Preprocessing import standardIndexName
from transformers import MT5ForConditionalGeneration, MT5Tokenizer, AutoTokenizer, AutoModelForTokenClassification, \
    pipeline, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM

# ---------- elastic configs -------------------
es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)
bucket_size = es_config.BUCKET_SIZE
search_result_size = es_config.SEARCH_RESULT_SIZE

book_index_name = es_config.Book_Index
doctic_doc_index = es_config.DOTIC_DOC_INDEX
doctic_para_index = es_config.DOTIC_PARA_INDEX

from doc.huggingface_views import *


# preprocessing function

@after_response.enable
def extractor(newdoc, newDoc, tasks_list):
    ZipFileExtractor.extractor(newdoc, newDoc, tasks_list, "")


def arabic_preprocessing(text):
    while "  " in text:
        text = text.replace("  ", " ")

    text = text.lstrip().rstrip().strip()
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}

    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def deleter(name, filename, only_result):
    try:
        filename = str(os.path.basename(filename)).split(".")[0]
        result_path = os.path.join(config.RESULT_PATH, filename)
        shutil.rmtree(result_path)
        if not only_result:
            data_path = os.path.join(config.DATA_PATH, filename)
            doc_zip_path = os.path.join(config.ZIPS_PATH, filename + ".zip")
            shutil.rmtree(data_path)
            os.remove(doc_zip_path)
    except Exception as e:
        print(e)


def update_doc(request, id, language, ):
    host_url = urlparse(request.build_absolute_uri()).netloc

    file = get_object_or_404(Country, id=id)

    # file = Country.objects.get(file_id=id)
    # deleter(file.name, file.file.name, True)
    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]
    # start_automating.apply(folder_name)
    file.status = "Starting..."
    file.save()

    StratAutomating.apply.after_response(folder_name, file, "DocsAreaGraphCubeData", host_url)

    return redirect('zip')


def Create_Folder():
    if not os.path.isdir(config.RESULT_PATH):
        os.mkdir(config.RESULT_PATH)
    if not os.path.isdir(config.DATA_PATH):
        os.mkdir(config.DATA_PATH)
    if not os.path.isdir(config.ZIPS_PATH):
        os.mkdir(config.ZIPS_PATH)


def UploadFile(request, country, language, tasks_list):
    Create_Folder()

    host_url = urlparse(request.build_absolute_uri()).netloc
    if request.method == 'POST':
        inputFile = request.FILES['inputFile']
        country_count = Country.objects.filter(name=country).count()
        file_ext = (inputFile.name).split(".")[-1]

        if country_count > 0:
            return JsonResponse({"response": "duplicate country"})
        elif file_ext != "zip":
            return JsonResponse({"response": "wrong format"})
        else:
            country_object = Country(name=country, language=language, file=inputFile, file_name=inputFile.name,
                                     status="Running")

            country_object.save()
            ZipFileExtractor.extractor(country_object, country_object, tasks_list, host_url)
            return JsonResponse({"response": "Ok"})


def get_task_list(request):
    file_path = str(Path(config.PERSIAN_PATH, 'TaskList.json'))
    data = json.load(open(file_path, encoding='utf-8'))
    return JsonResponse(data)


def get_standard_maps(country_objects):
    dataset_map = {}
    # country_objects = country_objects.order_by("-id")
    country_objects = country_objects.order_by("id")
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "استاندارد":
            dataset_map[id] = name
    return dataset_map


def get_similarity_maps(graph_objects):
    dataset_map = {}
    for each in graph_objects:
        id = each.measure_id_id
        name = each.measure_id.name
        if id not in dataset_map:
            dataset_map[id] = name
    return dataset_map


# html load function

@allowed_users('admin_accept_user_comments')
def seeAllComment(request):
    comments = DocumentComment2.objects.all().order_by('is_accept')

    result = []
    for c in comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()

        result.append(
            {"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
             "agreed_count": agreed_count, "disagreed_count": disagreed_count, "document_name": c.document.name,
             "is_accept": c.is_accept, "time": c.time})

    return render(request, 'doc/admin_accept_user_comments.html', {'comments': result})


def seeAllComment2(request):
    comments = DocumentComment2.objects.all()

    result = []
    for c in comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()

        result.append(
            {"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
             "agreed_count": agreed_count, "disagreed_count": disagreed_count, "document_name": c.document.name,
             "is_accept": c.is_accept})

    return render(request, 'doc/admin_accept_user_comments2.html', {'comments': result})


@allowed_users('admin_accepted_user')
def seeAcceptedUser(request):
    activated_user = User.objects.all().filter(is_active=1)
    return render(request, 'doc/admin_accepted_user.html', {'activated_user': activated_user})


@allowed_users('admin_upload')
def admin_upload(request):
    return render(request, 'doc/admin_upload.html')


@allowed_users('super_admin_user_log')
def showUserLogs(request):
    users = User.objects.all().filter(is_active=1)
    return render(request, 'doc/admin_user_log.html', {'users': users})


@allowed_users('admin_user_recommendation')
def get_user_recommendation(request):
    recommendation = Recommendation.objects.all()
    return render(request, 'doc/admin_user_recommendation.html', {'recommendation': recommendation})


@allowed_users('admin_user_report_bug')
def get_user_report_bug(request):
    reports = Report_Bug2.objects.order_by('checked', 'date')
    return render(request, 'doc/admin_user_report_bug.html', {'report_bug': reports})


@allowed_users('admin_waiting_user')
def getRegisteredUser(request):
    data = User.objects.all().filter(is_active=0)
    return render(request, 'doc/admin_waiting_user.html', {'data': data})


def getRegisteredUser2(request):
    data = User.objects.all().filter(is_active=0)
    return render(request, 'doc/admin_waiting_user2.html', {'data': data})


@allowed_users('AI_topics')
def AI_topics(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/AI_topics.html', {'countries': country_map})


# @allowed_users('AI_topics')
def paragrraph_clustering(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/paragraph_clustering2.html', {'countries': country_map})


def comparison(request):
    return render(request, 'doc/comparison2.html')


def recommendation(request):
    return render(request, 'doc/recommendation.html')


def report_bug(request):
    return render(request, 'doc/report_bug.html')


# @allowed_users('AI_topics')
def decision_tree(request, country_id, clustering_algorithm_id):
    country = Country.objects.get(id=country_id)

    result = {"id": country.id,
              "name": country.name,
              "folder": str(country.file.name.split("/")[-1].split(".")[0]),
              "language": country.language,
              "clustering_algorithm_id": clustering_algorithm_id
              }

    return render(request, 'doc/decision_tree.html', {"country_info": result})


@allowed_users('advanced_graph')
def graph2(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/graph3.html', {'countries': country_map})


@allowed_users('es_search')
def es_search(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/ES_Search3.html', {'countries': country_map})


def dendrogram(request, country_id, ngram_type):
    country = Country.objects.get(id=country_id)
    folder = str(country.file.name.split("/")[-1].split(".")[0])
    file_path = "dendrogram_plots/" + folder + "_" + str(ngram_type) + '_dendrogram.png'

    return render(request, 'doc/dendrogram.html', {"file_path": file_path})


def showDeployLogs(request):
    return render(request, 'doc/Deploy_server_time.html')


def DownloadUnknownDocuments(request):
    return render(request, 'doc/download_unknown_documents.html')


def index(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/index.html', {'countries': country_map})


def knowledgeGraph(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/KnowledgeGraph.html', {'countries': country_map})


def following_document_comments(request):
    return render(request, 'doc/following_document_comments.html')


def notes(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/notes.html', {'countries': country_map})


def GetAllNotesUser(request, username):
    notes = DocumentNote.objects.filter(user__username=username)
    result = []
    for n in notes:
        result.append({"note": n.note, "time": n.time, "document_name": n.document.file_name, "id": n.document.id})
    return JsonResponse({"notes": result})

@unathenticated_user
def signup(request):
    return render(request, "doc/signup.html")


@unathenticated_user
def login(request):
    return render(request, "doc/login.html")


@allowed_users()
def ManageUsersTab(request):
    return render(request, 'doc/manage_admins.html')


@allowed_users('ManualClustering')
def ManualClustering(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/manual_clustering.html', {'countries': country_map})


def ShowMyUserProfile(request):
    return render(request, "doc/myprofile.html", {})


def ShowUserProfile(request):
    return render(request, "doc/userprofile.html", {})


def sentiment_analysis_panel(request):
    return render(request, 'doc/sentiment_analysis.html')


def upload_zip_file(request):
    # documents = ZipFile.objects.filter(uploader=request.user)
    query_set1 = Country.objects.filter()
    query_set2 = ''

    documents = chain(query_set1, query_set2)

    # if request.user.is_superuser:
    FileField(label='Select a file', help_text='max. 10 megabytes')
    # Handle file upload
    file_name = request.POST.get('file_name')
    language = request.POST.get('language')
    if Country.objects.filter(name=file_name):
        return render(request, 'doc/upload.html',
                      {'status': 'File with this name exists', 'color': 'red', 'form': ZipFileForm(),
                       'files': documents})
    if request.method == 'POST':
        if request.POST.get('delete_items') is not None:
            id = request.POST.get('delete_items')
            id = str(id).replace('delete ', '')
            file = Country.objects.get(file_id=id)
            file.delete()
            deleter(file.name, file.file.name, False)
            # documents = Country.objects.filter(uploader=request.user)
            query_set1 = Country.objects.filter()
            query_set2 = ''

            documents = chain(query_set1, query_set2)
            return render(request, 'doc/upload.html',
                          {'status': 'File deleted successfully', 'color': 'green', 'form': ZipFileForm(),
                           'files': documents})
        elif request.POST.get('update_items') is not None:
            id = request.POST.get('update_items')
            id = str(id).replace('update ', '')
            file = Country.objects.get(id=id)
            deleter(file.name, file.file.name, True)
            my_file = file.file.path
            my_file = str(os.path.basename(my_file))
            dot_index = my_file.rfind('.')
            folder_name = my_file[:dot_index]
            # start_automating.apply(folder_name)
            # file.status = "Processing"
            file.save()
            StratAutomating.apply.after_response(folder_name, file)
            # documents = Country.objects.filter(uploader=request.user)
            # query_set1 = Country.objects.filter()
            # query_set2 = en_model.Country.objects.filter()

            documents = Country.objects.filter()
            return render(request, 'doc/upload.html',
                          {'status': 'File updated successfully', 'form': ZipFileForm(), 'files': documents})
        else:
            cur_user = request.user
            cur_file = request.FILES['docfile']
            if '.rar' in str(cur_file):
                return render(request, 'doc/upload.html',
                              {'status': 'You can\'t choose rar files', 'form': ZipFileForm(), 'files': documents})
            founded_file = Country.objects.filter(name=file_name)
            if len(str(file_name)) == 0:
                return render(request, 'doc/upload.html',
                              {'status': 'No named entered', 'form': ZipFileForm(), 'files': documents})
            if len(founded_file) != 0:
                founded_file = Country.objects.get(name=file_name)
                founded_file.delete()
                deleter(founded_file.name, founded_file.file.name, True)
            # newdoc = Country(file=cur_file, name=file_name, status="Processing", uploader=cur_user)
            newdoc = Country(file=cur_file, file_name=cur_file,
                             name=file_name, language=language, status="Processing")
            newdoc.save()
            # zip_extractor.extractor(newdoc)
            extractor.after_response(newdoc, newdoc)
            return render(request, 'doc/upload.html',
                          {'status': 'File uploaded successfully', 'form': ZipFileForm(), 'files': documents})
    else:
        pass

    return render(request, 'doc/upload.html', {'form': ZipFileForm(), 'files': documents})


# upload page link
def detect_level(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsLevelExtractor
    DocsLevelExtractor.apply(None, file)
    return redirect('zip')


def static_data_import_db(request, id, language):
    file = get_object_or_404(Country, id=id)

    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.apply(None, file)

    return redirect('zip')


def docs_clause_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsClauseExtractor
    DocsClauseExtractor.apply(None, file)

    return redirect('zip')


def template_panels_data_import_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.template_panels_to_db()
    return redirect('zip')


def revoked_types_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.revoked_types_to_db(Country)
    return redirect('zip')


def clustering_algorithms_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.clustering_algorithms_to_db(Country)
    return redirect('zip')


def trial_law_import(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsTrialLawExtractor

    DocsTrialLawExtractor.apply(file)
    return redirect('zip')


def document_json_list(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateDocumentsListCubeData
    DocsCreateDocumentsListCubeData.apply(None, file)
    return redirect('zip')


def docs_general_definitions_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsGeneralDefinitionsExtractor
    DocsGeneralDefinitionsExtractor.apply(None, file)
    return redirect('zip')


def docs_subject_area_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsSubjectAreaExtractor
    DocsSubjectAreaExtractor.apply(None, file)
    return redirect('zip')


def docs_actors_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsActorsExtractor4
    DocsActorsExtractor4.apply(None, file)
    return redirect('zip')


def docs_lda_topic_extraction(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import AITopicLDA
    AITopicLDA.apply(None, file)
    return redirect('zip')


def docs_general_actors_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsGeneralActorsExtractor
    DocsGeneralActorsExtractor.apply(None, file)
    return redirect('zip')


def operators_static_data_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.operators_to_db()
    return redirect('zip')


def actors_static_data_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    # StaticDataImportDB.Actors_Insert()
    # StaticDataImportDB.Actor_Graph_Types_Insert()
    StaticDataImportDB.Area_SubArea_Insert()
    StaticDataImportDB.Update_ActorsArea()
    return redirect('zip')


def search_parameters_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.Search_Parameters_Insert(file)
    return redirect('zip')


def subject_area_keywords_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.Subjects_area_Insert(file)
    return redirect('zip')


def insert_subject_keyword_list(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import InsertSubjectKeywords

    InsertSubjectKeywords.apply(None, file)
    return redirect('zip')


@is_login
def Admin(request):
    username = request.COOKIES.get('username')
    user = User.objects.all().get(username=username)
    if user.is_super_user:
        return redirect('manage_users_tab')
    else:
        panels = UserPanels.objects.filter(user=user).order_by('panel__id')
        if panels:
            address = panels[0].panel.panel_english_name
            return redirect(address)
        else:
            return HttpResponse('You are not authorized to view this page')



def create_standards_table(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    StaticDataImportDB.create_standard_table_from_excel(folder_name, file)
    return redirect('zip')


def update_file_name_extention(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    StaticDataImportDB.update_file_name_extention(folder_name, file)
    return redirect('zip')


def FindSubjectComplaint(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import FindSubjectComplaint
    FindSubjectComplaint.apply(None, file)
    return redirect('zip')


def regulators_static_import_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.Regulators_Insert()
    return redirect('zip')


def actors_time_series_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsActorsTimeSeriesDataExtractor
    DocsActorsTimeSeriesDataExtractor.apply(None, file)
    return redirect('zip')



def ARIMA_Prediction_TO_DB(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import ActorsARIMAPrediction
    ActorsARIMAPrediction.apply(None, file)
    return redirect('zip')


def actors_graph_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocActorsGraphExtractor
    DocActorsGraphExtractor.apply(None, file)
    return redirect('zip')


def actors_new_graph_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocActorsGraphExtractor
    DocActorsGraphExtractor.get_similarity_graph(None, file)
    DocActorsGraphExtractor.get_area_actor_graph(None, file)
    return redirect('zip')


def ingest_documents_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestDocumentsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_document_actor_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentActorToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestDocumentActorToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_actor_supervisor_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestActorSupervisorToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestActorSupervisorToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_spatiotemporal_to_index(request, id):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestSpatioTemporalDataToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestSpatioTemporalDataToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_paragraphs_to_index(request, id, language, is_for_ref):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestParagraphsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestParagraphsToElastic.apply(folder_name, file, is_for_ref)
    return redirect('zip')


def ingest_clustering_paragraphs_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestClusteringParagraphsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestClusteringParagraphsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_standard_documents_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestStandardDocumentsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestStandardDocumentsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_standard_documents_to_sim_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentsToSimilarityIndex

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    similarity_list = ['BM25']

    for sim_type in similarity_list:
        IngestDocumentsToSimilarityIndex.apply(folder_name, file, sim_type)
    return redirect('zip')



def ingest_document_collective_members_to_index(request, id):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentCollectiveMembersToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestDocumentCollectiveMembersToElastic.apply(folder_name, file)

    return redirect('zip')


def paragraphs_similarity_calculation(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import ParagraphsSimilarityCalculation

    ParagraphsSimilarityCalculation.apply(None, file)
    return redirect('zip')


def ARIMA_Prediction_TO_DB_2(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import AdvanceARIMAExtractor
    AdvanceARIMAExtractor.apply(None, file)
    return redirect('zip')

def collective_static_data_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.Collective_Actors_Insert()
    return redirect('zip')


def indictment_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import IndictmentToDB
    IndictmentToDB.apply(None, file)
    return redirect('zip')


def docs_collective_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCollectiveActorsExtractor
    DocsCollectiveActorsExtractor.apply(None, file)
    return redirect('zip')


def docs_complete_para_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsExecutiveParagraphsExtractor
    DocsExecutiveParagraphsExtractor.apply(None, file)
    return redirect('zip')


def docs_regulators_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsRegulatorsExtractor3
    DocsRegulatorsExtractor3.apply(None, file)
    return redirect('zip')


def docs_opertators_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsOperatorsExtractor
    DocsOperatorsExtractor.apply(None, file)
    return redirect('zip')


def create_CUBE_Subject_Statistics(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateSubjectStatisticsCubeData
    DocsCreateSubjectStatisticsCubeData.apply(None, file)
    return redirect('zip')


def create_CUBE_Subject(request, id):
    host_url = request.get_host()

    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateSubjectCubeData
    DocsCreateSubjectCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_Votes(request, id):
    host_url = request.get_host()
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateVotesCubeData
    DocsCreateVotesCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_CollectiveActor(request, id):
    host_url = request.get_host()
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateCollectiveActorsCubeData
    DocsCreateCollectiveActorsCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_RegularityLifeCycle(request, id):
    host_url = request.get_host()
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateRegularityLifeCycleCubeData
    DocsCreateRegularityLifeCycleCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_BusinessAdvisor(request, id):
    host_url = request.get_host()
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocCreateBusinessAdvisorCubeData
    DocCreateBusinessAdvisorCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_MandatoryRegulations(request, id):
    host_url = request.get_host()
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateMandatoryRegulationsCubeData
    DocsCreateMandatoryRegulationsCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_Template(request, id, panel_name):
    host_url = request.get_host()

    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateTemplatePanelsCubeData
    DocsCreateTemplatePanelsCubeData.apply(None, file, host_url, panel_name)
    return redirect('zip')


def create_CUBE_Principle(request, id):
    host_url = request.get_host()

    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreatePrinciplesCubeData
    DocsCreatePrinciplesCubeData.apply(None, file, host_url)
    return redirect('zip')


def create_CUBE_MaxMinEffectActorsInArea(request, id):
    host_url = request.get_host()

    Country_Id = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateActorInformationStackChartCubeData
    DocsCreateActorInformationStackChartCubeData.apply(None, Country_Id, host_url)
    return redirect('zip')


def delete_doc(request, id, language):
    file = Country.objects.get(id=id)

    deleter(file.name, file.file.name, False)
    file.delete()
    return redirect('zip')


def get_country_maps(country_objects):
    dataset_map = {}
    # country_objects = country_objects.order_by("-id")
    country_objects = country_objects.order_by("id")
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "فارسی":
            dataset_map[id] = name
    return dataset_map


# views function

def GetDocumentsPredictSubjectLDA(request, country_id, number_of_topic):
    country_id = int(country_id)
    result_without = []
    result_difference = []

    para_id_list = list(AILDAParagraphToTopic.objects.filter(
        country_id=country_id, number_of_topic=number_of_topic).values_list("paragraph_id", flat=True))

    para_list = DocumentParagraphs.objects.filter(document_id__country_id__id=country_id).filter(
        ~Q(id__in=para_id_list)).annotate(
        doc_id=F('document_id__id')).annotate(
        doc_name=F('document_id__name')).annotate(
        approval_reference_name=F('document_id__approval_reference_name')).annotate(
        approval_date=F('document_id__approval_date')).annotate(
        subject_name=F('document_id__subject_name')).annotate(text_len=Length('text')).filter(
        text_len__gt=80)[:300]

    for row in para_list:
        res = {
            'paragraph_id': row.id,
            'paragraph_text': row.text,
            'document_id': row.doc_id,
            'document_name': row.doc_name,
            'subject_name': row.subject_name if row.subject_name != None else 'نامشخص',
            'approval_reference_name': row.approval_reference_name if row.approval_reference_name != None else 'نامشخص',
            'approval_date': row.approval_date if row.approval_date != None else 'نامشخص',
        }
        result_without.append(res)

    filesList = AI_Paragraph_Subject_By_LDA.objects.filter(
        country_id=country_id, number_of_topic=number_of_topic, subject__isnull=False).order_by('-Accuracy').annotate(
        doc_id=F('paragraph__document_id__id')).annotate(
        doc_name=F('paragraph__document_id__name'))[:300]

    for row in filesList:
        res = {
            'doc_id': row.doc_id,
            'doc_name': row.doc_name,
            'paragraph_id': row.paragraph.id,
            'paragraph_text': row.paragraph.text,
            'document_subject': row.subject,
            'document_predict_subject': row.subject_predict,
            'topic_id': row.topic.id,
        }
        result_difference.append(res)

    return JsonResponse(
        {'documentsDifferenceSubjectLDA': result_difference, 'documentsWithoutSubjectLDA': result_without})

def AIGet_Topic_Centers_CahrtData(request, country_id, number_of_topic):
    heatmap_chart_data = AILDAResults.objects.get(
        country__id=country_id, number_of_topic=number_of_topic).heatmap_chart_data["data"]

    topic_list = AIParagraphLDATopic.objects.filter(
        country__id=country_id, number_of_topic=number_of_topic).values()

    cluster_size_chart_data = []

    for topic in topic_list:
        topic_name = topic["topic_name"]
        paragraph_count = topic["paragraph_count"]
        cluster_size_chart_data.append([topic_name, paragraph_count])

    return JsonResponse({'cluster_size_chart_data': cluster_size_chart_data,
                         "heatmap_chart_data": heatmap_chart_data})


def AIGetLDATopic(request, country_id, number_of_topic, username):
    lda_topics = []
    all_para_count = 0

    temp = AIParagraphLDATopic.objects.filter(country__id=country_id, number_of_topic=number_of_topic)

    user_topic_labels = UserLDATopicLabel.objects.filter(
        topic__country__id=country_id,
        topic__number_of_topic=number_of_topic,
        user__username=username).values()

    user_label_dict = {}

    if len(user_topic_labels) > 0:
        for row in user_topic_labels:
            user_label_dict[row['topic_id']] = row['label']

    for record in temp:
        record_id = record.id
        sorted_word_list = [k for k, v in sorted(record.words.items(), reverse=True, key=lambda item: float(item[1]))]
        user_label_value = user_label_dict[record_id] if record_id in user_label_dict else 'بدون برچسب'

        user_label_input = "<div>" + \
                           "<input id ='" + str(
            record_id) + "' class='form-control p-1 text-center d-block w-100' value ='" + user_label_value + "' type= 'text'/>" + \
                           "<button onclick=save_user_labelLDA('" + str(
            record_id) + "') class = 'btn btn-outline-success mt-1 p-0 d-block w-100'>ذخیره</button>" + \
                           "</div>"

        lda_topics.append({
            'id': record.id,
            'topic_id': record.topic_id,
            'topic_name': record.topic_name,
            'words': " - ".join(sorted_word_list),
            'entropy': record.correlation_score,
            'subject': record.dominant_subject_name,
            'paragraph_count': record.paragraph_count,
            'user_label': user_label_input
        })
        all_para_count += record.paragraph_count
    return JsonResponse({'lda_topics': lda_topics, 'all_para_count': all_para_count})

def BoostingSearchParagraph_Column_ES(request, country_id, field_name, field_value, curr_page, result_size):
    res_query = {"bool": {
        "filter": [
            {
                "term": {
                    "type_name.keyword": "قانون"
                }
            },
            {
                "term":
                    {
                        field_name: {
                            "value": field_value
                        }
                    }
            },
            {
                "range": {
                    "attachment.content_length": {
                        "gte": 80
                    }
                }
            }
        ],
        "must": {
            "bool": {
                "should": []
            }
        },
        "must_not": []
    }
    }

    keyword_score_dict = dict(request.POST)

    cluser_keyword_data = keyword_score_dict['cluser_keyword_data'][0].split(',')
    cluster_delete_data = keyword_score_dict['cluster_delete_data'][0].split(',')

    for index in range(0, len(cluser_keyword_data), 2):
        keyword = cluser_keyword_data[index]
        score = int(cluser_keyword_data[index + 1])

        title_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["document_name"],
                "boost": score * 10
            }
        }
        res_query['bool']['must']['bool']['should'].append(title_query)

        word_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
                "boost": score
            }
        }
        res_query['bool']['must']['bool']['should'].append(word_query)

    for delete_keyword in cluster_delete_data:
        delete_title_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["document_name"],
            }
        }
        res_query['bool']['must_not'].append(delete_title_query)

        delete_word_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
            }
        }
        res_query['bool']['must_not'].append(delete_word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
    # index_name = 'doticfull_documentparagraphs_graph'
    # index_name = 'fava_documentparagraphs_graph'

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'paragraph_id', 'attachment.content'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name)['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        "result": result
    }
    return JsonResponse(response_dict)


def BoostingSearchParagraph_ES(request, country_id, curr_page, result_size):
    res_query = {"bool": {
        "filter": [
            {
                "term": {
                    "type_name.keyword": "قانون"
                }
            },
            {
                "range": {
                    "attachment.content_length": {
                        "gte": 80
                    }
                }
            }
        ],
        "must": {
            "bool": {
                "should": []
            }
        },
        "must_not": []
    }
    }

    keyword_score_dict = dict(request.POST)

    cluser_keyword_data = keyword_score_dict['cluser_keyword_data'][0].split(',')
    cluster_delete_data = keyword_score_dict['cluster_delete_data'][0].split(',')

    for index in range(0, len(cluser_keyword_data), 2):
        keyword = cluser_keyword_data[index]
        score = int(cluser_keyword_data[index + 1])

        title_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["document_name"],
                "boost": score * 10
            }
        }
        res_query['bool']['must']['bool']['should'].append(title_query)

        word_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
                "boost": score
            }
        }
        res_query['bool']['must']['bool']['should'].append(word_query)

    for delete_keyword in cluster_delete_data:
        delete_title_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["document_name"],
            }
        }
        res_query['bool']['must_not'].append(delete_title_query)

        delete_word_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
            }
        }
        res_query['bool']['must_not'].append(delete_word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
    # index_name = 'doticfull_documentparagraphs_graph'

    # index_name = 'fava_documentparagraphs_graph'

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },

        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'paragraph_id', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             aggregations=res_agg,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']
    aggregations = response['aggregations']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name)['count']

    response_dict = {
        'total_hits': total_hits,
        'aggregations': aggregations,
        "curr_page": curr_page,
        "result": result
    }
    return JsonResponse(response_dict)

def ChangePassword(request, old_password, new_password):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    check = check_password(old_password, user.password)
    if check:
        user.password = make_password(new_password)
        user.save()
        return JsonResponse({"status": "OK"})
    else:
        return JsonResponse({"status": "wrong password"})


def SaveUserLog(user_id, ip, url):
    date_time = datetime.datetime.now()
    UserLogs.objects.create(user_id_id=user_id, user_ip=ip,
                            page_url=url, visit_time=date_time)

def CheckUserLogin(request, username, password, ip):
    user = User.objects.filter(username=username)

    if user.count() == 0:
        SaveUserLog(None, ip, "username not found")
        return JsonResponse({"status": "not found"})
    elif not check_password(password, user[0].password):
        SaveUserLog(user[0].id, ip, "wrong password")
        return JsonResponse({"status": "wrong password"})
    elif user[0].is_active == 0:
        SaveUserLog(user[0].id, ip, "not active check")
        return JsonResponse({"status": "not active"})
    elif user[0].is_active == -1:
        SaveUserLog(user[0].id, ip, "de active check")
        return JsonResponse({"status": "de active"})
    # elif user[0].is_super_user:
    #     last_login = datetime.datetime.now()
    #     user.update(last_login=last_login)
    #     return JsonResponse({"status": "found admin"})
    else:
        last_login = datetime.datetime.now()
        user.update(last_login=last_login)

        SaveUserLog(user[0].id, ip, "login")

        return JsonResponse({"status": "found user"})


@allowed_users()
def CreateOrDeleteUserPanel(request, panel_name, username):
    CreatePanel(request)
    panel = Panels.objects.all().get(panel_english_name=panel_name)
    user = User.objects.all().get(username=username)
    user_admin_panels = UserPanels.objects.filter(panel=panel, user=user)
    if user_admin_panels:
        UserPanels.objects.get(
            panel=panel,
            user=user
        ).delete()
        return JsonResponse({"status": "deleted"})
    else:
        UserPanels.objects.create(
            panel=panel,
            user=user
        )
        return JsonResponse({"status": "created"})

def CreateReportBug(request, username, report_bug_text, panel_id, branch_id):
    user = User.objects.get(username=username)
    main_panel = MainPanels.objects.all().get(id=panel_id)
    panel = Panels.objects.all().get(id=branch_id)
    Report_Bug2.objects.create(
        user=user,
        panel_id=main_panel,
        branch_id=panel,
        report_bug_text=report_bug_text,
        date=str(jdatetime.strftime(jdatetime.now(), "%H:%M:%S %Y-%m-%d"))
    )
    return JsonResponse({"status": "OK"})

def Excel_Topic_Paragraphs_ES(request, country_id, topic_id, result_size, curr_page, username):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            }
        ],

        "should": []
    }}
    word_score_dict = ClusterTopic.objects.get(id=topic_id).words

    for word, score in word_score_dict.items():
        word = word.strip()
        integer_score = int(float(score) * 10000)
        boost_score = integer_score if integer_score > 0 else 1

        word_query = {
            "match_phrase": {
                "attachment.content": {
                    "query": word,
                    "boost": boost_score
                }
            }
        }

        res_query['bool']['should'].append(word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_name'
                                 , 'attachment.content', 'topic_name',
                                               'score'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size

                             )

    result = response['hits']['hits']

    result_range = str(from_value) + " تا " + str(from_value + len(result))

    paragraph_list = [
        [doc['_source']['document_name']
            , doc['_source']['attachment']['content'],
         doc['_source']['score']] for doc in result]

    cluster_name = ClusterTopic.objects.get(id=topic_id).name.replace('C', 'شماره ')

    try:
        user_topic_label = UserTopicLabel.objects.get(
            topic__id=topic_id,
            user__username=username).label
    except:
        user_topic_label = 'بدون برچسب'

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام سند", "متن پاراگراف", "امتیاز"])

    file_name = country_obj.name + " - " + "احکام خوشه " + cluster_name + \
                " - " + user_topic_label + " - " + result_range + ".xlsx"

    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})


@allowed_users()
def CreatePanel(request):
    for main_panel, panel in AllPanels.items():
        persian_name = panel['persian_name']
        parent = None
        try:
            parent = MainPanels.objects.create(
                panel_persian_name=persian_name,
                panel_english_name=main_panel
            )
        except:
            parent = MainPanels.objects.get(
                panel_persian_name=persian_name,
                panel_english_name=main_panel
            )
        sub_panels = panel['sub_panels']
        for epanel, ppanel in sub_panels.items():
            try:
                Panels.objects.create(
                    parent=parent,
                    panel_persian_name=ppanel,
                    panel_english_name=epanel
                )
            except:
                pass

    panels = Panels.objects.all().order_by('id')
    result = []
    for panel in panels:
        id = panel.id
        persian_name = panel.panel_persian_name
        english_name = panel.panel_english_name

        result.append({
            "id": id,
            "persian_name": persian_name,
            "english_name": english_name,
        })

    # for main_panel,persian_name in Other_Panels.items():
    #     parent = None
    #     try:
    #         parent = MainPanels.objects.create(
    #             panel_persian_name = persian_name,
    #             panel_english_name = main_panel
    #         )
    #     except:
    #         parent = MainPanels.objects.get(
    #             panel_persian_name = persian_name,
    #             panel_english_name = main_panel
    #         )

    #     try:
    #         Panels.objects.create(
    #             parent = parent,
    #             panel_persian_name = persian_name,
    #             panel_english_name = main_panel
    #         )
    #     except:
    #         pass
    return result


def GetAllPanels(request):
    CreatePanel(request)
    main_panels = MainPanels.objects.all().order_by('id')
    ret_res = {'all_panels': []}

    for main_panel in main_panels:
        ret_res['all_panels'].append({'id': main_panel.id,
                                      'english_name': main_panel.panel_english_name,
                                      'persian_name': main_panel.panel_persian_name,
                                      'sub_panels': []})
        sub_panels = Panels.objects.all().filter(parent__id=main_panel.id).order_by('id')
        for panel in sub_panels:
            new_panel = {}
            new_panel['id'] = panel.id
            new_panel['english_name'] = panel.panel_english_name
            new_panel['persian_name'] = panel.panel_persian_name
            ret_res['all_panels'][-1]['sub_panels'].append(new_panel)

    return JsonResponse(ret_res)


@allowed_users()
def GetAcceseToAllUsers(request):
    CreatePanel(request)
    panels = Panels.objects.all()
    users = User.objects.all().filter(is_super_user=False, is_active=1)
    for user in users:
        curr_user = User.objects.all().get(id=user.id)
        for panel in panels:
            curr_panel = Panels.objects.all().get(id=panel.id)
            user_admin_panels = UserPanels.objects.filter(panel=curr_panel, user=curr_user)
            if not user_admin_panels:
                UserPanels.objects.create(
                    panel=panel,
                    user=user
                )
    return JsonResponse({"status": "created"})


@is_login
def GetAllowedPanels(request, username=None):
    if username == None:
        username = request.COOKIES.get('username')
    user = User.objects.all().get(username=username)
    panels = UserPanels.objects.filter(user=user).order_by('panel__id')
    user_panel = []
    for panel in panels:
        panel_name = panel.panel.panel_english_name
        user_panel.append(panel_name)

    ret_res = {'main_panels': {}}

    for main_panel, panel_info in AllPanels.items():
        ret_res['main_panels'][main_panel] = []
        for panel in panel_info['sub_panels'].keys():
            if panel in user_panel:
                ret_res['main_panels'][main_panel].append(panel)

    # temporary ------------------------------------
    if (user.is_super_user and
            'standards_analysis' in ret_res['main_panels'] and
            'books_analysis' in ret_res['main_panels'] and
            'approvals_analysis' in ret_res['main_panels']):
        del ret_res['main_panels']['standards_analysis']
        del ret_res['main_panels']['books_analysis']
    # temporary ------------------------------------

    result = []
    for panel in panels:
        panel_name = panel.panel.panel_english_name
        result.append(panel_name)
    ret_res['panels'] = result

    panels = Panels.objects.all()
    all_panels = []
    for panel in panels:
        english_name = panel.panel_english_name
        # temporary ------------------------------------
        if panel.parent.panel_english_name in ret_res['main_panels']:
            # temporary ------------------------------------

            all_panels.append(english_name)
    ret_res['all_panels'] = all_panels

    all_admin_panels = []
    for panel in AllPanels['admin_panels']['sub_panels'].keys():
        all_admin_panels.append(panel)
    ret_res['all_admin_panels'] = all_admin_panels

    ret_res['is_super_user'] = '0'
    if user.is_super_user:
        ret_res['is_super_user'] = '1'
        ret_res['panels'] = all_panels

    return JsonResponse(ret_res)


@is_login
def GetPermissions(request, username):
    user = User.objects.all().get(username=username)
    panels = UserPanels.objects.filter(user=user).order_by('panel__id')
    user_panel = []
    for panel in panels:
        panel_name = panel.panel.panel_english_name
        user_panel.append(panel_name)

    ret_res = {'all_panels': [], 'user_panels': user_panel}

    for main_panel, panel_info in AllPanels.items():
        ret_res['all_panels'].append(
            {'main_panel': main_panel, 'persian_name': panel_info['persian_name'], 'sub_panels': []})
        for panel in panel_info['sub_panels'].keys():
            new_panel = {}
            new_panel['english_name'] = panel
            new_panel['persian_name'] = panel_info['sub_panels'][panel]
            ret_res['all_panels'][-1]['sub_panels'].append(new_panel)

    return JsonResponse(ret_res)


@is_login
def GetPermissionsExcel(request):
    panels = CreatePanel(request)
    persian_panels = {panel['english_name']: panel['persian_name'] for panel in panels}
    activated_user = User.objects.all().filter(is_active=1, is_super_user=False)
    result = []

    for user in activated_user:
        new_user = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'phone': user.mobile,
        }
        user_admin_panel = UserPanels.objects.all().filter(user_id=user.id)
        user_panels = [panel.panel.panel_english_name for panel in user_admin_panel]
        for panel in panels:
            en_name = panel['english_name']
            if en_name in user_panels:
                new_user[en_name] = '✅'
            else:
                new_user[en_name] = '❌'

        result.append(new_user)

    return JsonResponse({"users": result, "panels": persian_panels})

def Get_Topic_Paragraphs_ES(request, country_id, topic_id, result_size, curr_page, get_paragraphs, get_aggregations):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            }
        ],

        "should": []
    }}
    word_score_dict = ClusterTopic.objects.get(id=topic_id).words

    for word, score in word_score_dict.items():
        word = word.strip()
        integer_score = int(float(score) * 10000)
        boost_score = integer_score if integer_score > 0 else 1

        word_query = {
            "match_phrase": {
                "attachment.content": {
                    "query": word,
                    "boost": boost_score
                }
            }
        }

        res_query['bool']['should'].append(word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },
        "subject-agg": {
            "terms": {
                "field": "keyword_subject.keyword",
                "size": bucket_size
            }
        },
        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name',
                                               'paragraph_id', 'attachment.content',
                                               'topic_id', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations
    }
    if get_paragraphs == 1:
        response_dict["result"] = result

    if get_aggregations == 1:
        response_dict["aggregations"] = aggregations

    return JsonResponse(response_dict)


def GetAllNotesInTimeRange(request, username, time_start, time_end):
    user_notes = DocumentNote.objects.all().filter(user__username=username)

    if time_start != "0" and time_end != "0":
        user_notes = user_notes.filter(time__range=(
            time_start, time_end)).order_by("-time")
    elif time_start == "0" and time_end != "0":
        user_notes = user_notes.filter(time__lte=time_end).order_by("-time")
    elif time_start != "0" and time_end == "0":
        user_notes = user_notes.filter(time__gte=time_start).order_by("-time")
    else:
        user_notes = user_notes.order_by("-time")

    result = []
    hashTags = []
    labels = []
    for n in user_notes:
        result.append(
            {"note": n.note, "time": n.time, "document_name": n.document.name, "id": n.id, "label": n.docLabel,
             "starred": n.starred, "document_id": n.document.id, "document_country_id": n.document.country_id.id,
             "country_name": n.document.country_id.name})
        for ht in n.hash_tags.all():
            if (hashTags.__contains__(ht.hash_tag) == False):
                hashTags.append(ht.hash_tag)
        if (labels.__contains__(n.docLabel) == False):
            labels.append(n.docLabel)
    return JsonResponse({"notes": result, "hashtags": hashTags, "labels": labels})

    # user_logs = user_logs.filter(user_id__isnull=False).order_by("-time")
    # chart_data = {}
    # for log in user_logs:
    #     user_id_id = log.user_id
    #     if user_id_id not in chart_data:
    #         chart_data[user_id_id] = 1
    #     else:
    #         chart_data[user_id_id] += 1
    # chart_data_list = []
    # for user_id_id, count in chart_data.items():
    #     name = user_id_id.first_name + ' ' + user_id_id.last_name
    #     column = [name, count]
    #     chart_data_list.append(column)
    # return JsonResponse({'user_chart_data_list': chart_data_list})



def GetCountryById(request, id):
    country = Country.objects.get(id=id)
    result = {"id": country.id,
              "name": country.name,
              "folder": str(country.file.name.split("/")[-1].split(".")[0]),
              "language": country.language,
              }
    return JsonResponse({'country_information': [result]})


def GetKeywordLDAData(request, country_id, cluster_size, username, keyword):
    lda_topics = []
    all_para_count = 0
    temp = AIParagraphLDATopic.objects.filter(country__id=country_id, number_of_topic=cluster_size)

    user_topic_labels = UserLDATopicLabel.objects.filter(
        topic__country__id=country_id,
        topic__number_of_topic=cluster_size,
        user__username=username).values()

    user_label_dict = {}

    if len(user_topic_labels) > 0:
        for row in user_topic_labels:
            user_label_dict[row['topic_id']] = row['label']

    for record in temp:
        if keyword in record.words:
            record_id = record.id
            sorted_word_list = [k for k, v in
                                sorted(record.words.items(), reverse=True, key=lambda item: float(item[1]))]
            user_label_value = user_label_dict[record_id] if record_id in user_label_dict else 'بدون برچسب'

            user_label_input = "<div>" + \
                               "<input id ='" + str(
                record_id) + "' class='form-control p-1 text-center d-block w-100' value ='" + user_label_value + "' type= 'text'/>" + \
                               "<button onclick=save_user_label('" + str(
                record_id) + "') class = 'btn btn-outline-success mt-1 p-0 d-block w-100'>ذخیره</button>" + \
                               "</div>"

            lda_topics.append({
                'id': record.id,
                'topic_id': record.topic_id,
                'topic_name': record.topic_name,
                'words': " - ".join(sorted_word_list),
                'entropy': record.correlation_score,
                'subject': record.dominant_subject_name,
                'paragraph_count': record.paragraph_count,
                'user_label': user_label_input
            })

            all_para_count += record.paragraph_count
    return JsonResponse({'lda_topics': lda_topics, 'all_para_count': all_para_count})


def GetLDAGraphData(request, country_id, number_of_topic):
    ClusteringGraphData_Object = LDAGraphData.objects.get(country_id=country_id, number_of_topic=number_of_topic)
    Nodes_data, Edges_data = ClusteringGraphData_Object.centroids_nodes_data, ClusteringGraphData_Object.centroids_edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetLDAKeywordGraphData(request, country_id, number_of_topic):
    ClusteringGraphData_Object = LDAGraphData.objects.get(country=country_id, number_of_topic=number_of_topic)
    Nodes_data, Edges_data = ClusteringGraphData_Object.subject_keywords_nodes_data, ClusteringGraphData_Object.subject_keywords_edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetMyUserProfile(request):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    user_expertise = User_Expertise.objects.filter(user_id=user.id)
    expertise = []
    for e in user_expertise:
        expertise.append(e.experise_id.expertise)
    expertise = " - ".join(expertise)

    if expertise == "":
        expertise = 'نامشخص'

    try:
        role = user.role.persian_name
    except:
        role = 'نامشخص'

    return JsonResponse({"profile": {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'mobile': user.mobile,
        'expertise': expertise,
        'role': role,
        'avatar': user.avatar
    }})


def GetNotesInTimeRangeFilterLabelHashtag(request, username, time_start, time_end, label, hashtag):
    user_notes = DocumentNote.objects.all().filter(user__username=username)

    if time_start != "0" and time_end != "0":
        user_notes = user_notes.filter(time__range=(
            time_start, time_end)).order_by("-time")
    elif time_start == "0" and time_end != "0":
        user_notes = user_notes.filter(time__lte=time_end).order_by("-time")
    elif time_start != "0" and time_end == "0":
        user_notes = user_notes.filter(time__gte=time_start).order_by("-time")
    else:
        user_notes = user_notes.order_by("-time")

    if (label != "همه"):
        user_notes = user_notes.filter(docLabel=label)

    if (hashtag != "همه"):
        user_notes = user_notes.filter(hash_tags__in=[hashtag])

    result = []
    # hashTags = []
    # labels = []
    for n in user_notes:
        result.append(
            {"note": n.note, "time": n.time, "document_name": n.document.name, "id": n.id, "label": n.docLabel,
             "starred": n.starred, "document_id": n.document.id, "document_country_id": n.document.country_id.id,
             "country_name": n.document.country_id.name})
        # for ht in n.hash_tags.all():
        #     if (hashTags.__contains__(ht.hash_tag) == False):
        #         hashTags.append(ht.hash_tag)
        # if (labels.__contains__(n.docLabel) == False):
        #     labels.append(n.docLabel)
    return JsonResponse({"notes": result})
    # return JsonResponse({"notes": result , "hashtags":hashTags , "labels":labels})


def GetParagraph_Clusters(request, country_id, algorithm_name, vector_type, cluster_count, ngram_type, username):
    clusters_data = {}

    algorithm_id = ClusteringAlorithm.objects.get(
        name=algorithm_name,
        input_vector_type=vector_type,
        cluster_count=cluster_count,
        ngram_type=ngram_type
    ).id

    try:

        algorithm_result_data = CUBE_Clustering_TableData.objects.get(country__id=country_id,
                                                                      algorithm__id=algorithm_id)

        clusters_data = algorithm_result_data.clusters_data
        table_data = algorithm_result_data.table_data['data']
        dict_table_data = algorithm_result_data.dict_table_data['data']

        user_topic_labels = UserTopicLabel.objects.filter(
            topic__algorithm__id=algorithm_id,
            topic__country__id=country_id,
            user__username=username).values()

        final_table_data = []

        if len(user_topic_labels) > 0:

            for row in user_topic_labels:
                topic_id = row['topic_id']
                table_row = dict_table_data[topic_id]
                table_row['user_label'] = table_row['user_label'].replace('بدون برچسب', row['label'])

            for topic_id, table_row in dict_table_data.items():
                final_table_data.append(table_row)

        else:
            final_table_data = table_data

    except:
        final_table_data = []
    return JsonResponse({
        "table_data": final_table_data,
        "clusters_data": clusters_data,
        'clustering_algorithm_id': algorithm_id
    })


def getNeighbourforNode(node_id, edge_data, node_parents, edge_count_limit):
    edge_list = list(filter(lambda x: (x["source"] == node_id or x["target"] == node_id) and
                                      (x["source"] not in node_parents or x["target"] not in node_parents), edge_data))

    if edge_list.__len__() > edge_count_limit:
        return sorted(edge_list, key=lambda k: k['weight'], reverse=True)[:edge_count_limit]
    elif edge_list.__len__() > 0:
        return sorted(edge_list, key=lambda k: k['weight'], reverse=True)[:edge_count_limit]
    else:
        return []


def exact_search_text(res_query, place, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'keyword':
        keyword_query = {
            "match_phrase": {
                "keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = keyword_query
        else:
            res_query['bool']['must'].append(keyword_query)

    elif place == 'keyword-term':
        keyword_query = {
            "term": {
                "keyword.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = keyword_query
        else:
            res_query['bool']['must'].append(keyword_query)

    elif place == 'عنوان':
        text_list = text.split("__")
        if text_list.__len__() == 1:
            title_query = {
                "match_phrase": {
                    "name": text
                }
            }
        else:
            title_query = {
                "terms": {
                    "name.keyword": text_list
                }
            }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)


    elif place == 'متن':
        content_query = {
            "match_phrase": {
                "attachment.content": text
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)


    elif place == 'شماره دادنامه':
        text = "*" + text + "*"
        judgment_number_query = {
            "wildcard": {
                "judgment_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = judgment_number_query
        else:
            res_query['bool']['must'].append(judgment_number_query)

    elif place == 'ICS':
        text = "*" + text + "*"
        ICS_query = {
            "wildcard": {
                "ICS.keyword": text
            }
        }
        if ALL_FIELDS:
            res_query = ICS_query
        else:
            res_query['bool']['must'].append(ICS_query)

    elif place == 'standard_number':
        text = "*" + text + "*"
        standard_number_query = {
            "wildcard": {
                "standard_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = standard_number_query
        else:
            res_query['bool']['must'].append(standard_number_query)


    else:
        title_content_query = {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "name": text
                        }
                    },
                    {
                        "match_phrase": {
                            "attachment.content": text
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)
    return res_query


def boolean_search_text(res_query, place, text, operator, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'عنوان':
        title_query = {
            "match": {
                "name": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif place == 'متن':
        content_query = {
            "match": {
                "attachment.content": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)


    elif place == 'شماره دادنامه':
        text = "*" + text + "*"
        judgment_number_query = {
            "wildcard": {
                "judgment_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = judgment_number_query
        else:
            res_query['bool']['must'].append(judgment_number_query)

    elif place == 'ICS':
        text = "*" + text + "*"
        ICS_query = {
            "wildcard": {
                "ICS.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = ICS_query
        else:
            res_query['bool']['must'].append(ICS_query)

    elif place == 'standard_number':
        text = "*" + text + "*"
        standard_number_query = {
            "wildcard": {
                "standard_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = standard_number_query
        else:
            res_query['bool']['must'].append(standard_number_query)

    else:
        title_content_query = {
            "bool": {

                "should": [
                    {
                        "match": {
                            "name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    },
                    {
                        "match": {
                            "attachment.content": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)

    return res_query

def GetUserExpertise(request):
    expertise = UserExpertise.objects.all()
    result = []
    for e in expertise:
        result.append({'id': e.id, 'expertise': e.expertise})
    return JsonResponse({"result": result})


def GetUserProfile(request, id):
    user = User.objects.get(id=id)
    user_expertise = User_Expertise.objects.filter(user_id=id)

    expertise = []
    for e in user_expertise:
        expertise.append(e.experise_id.expertise)
    expertise = " - ".join(expertise)

    if expertise == "":
        expertise = 'نامشخص'

    try:
        role = user.role.persian_name
    except:
        role = 'نامشخص'

    return JsonResponse({"profile": {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'email': user.email,
        'expertise': expertise,
        'role': role,
        'avatar': user.avatar
    }})


def GetUserRole(request):
    roles = UserRole.objects.filter(persian_name__isnull=False)
    result = []
    for role in roles:
        id = role.id
        persian_name = role.persian_name

        result.append({
            "id": id,
            "name": persian_name
        })
    return JsonResponse({"user_roles": result})


@allowed_users()
def ManageUsers(request):
    panels = CreatePanel(request)
    activated_user = User.objects.all().filter(is_active=1)
    result = []

    for user in activated_user:
        new_user = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'phone': user.mobile,
            'panels': []
        }
        user_admin_panel = UserPanels.objects.all().filter(user_id=user.id)
        for panel in user_admin_panel:
            panel_name = panel.panel.panel_english_name
            new_user['panels'].append(panel_name)

        result.append(new_user)

    return JsonResponse({"admins": result, "main_panels": AllPanels, "panels": panels})


def Recommendations(request, first_name, last_name, email, recommendation_text, rating_value):
    Recommendation.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        recommendation_text=recommendation_text,
        rating_value=rating_value,
    )
    return JsonResponse({"status": "OK"})


def save_lda_topic_label(request, topic_id, username, label):
    result_response = ""

    user = User.objects.get(username=username)
    topic = AIParagraphLDATopic.objects.get(id=topic_id)

    try:

        user_topic_label = UserLDATopicLabel.objects.get(
            topic=topic,
            user=user)

        user_topic_label.label = label
        user_topic_label.save()
        result_response = ".برچسب موضوع تغییر یافت"

    except:
        UserLDATopicLabel.objects.create(
            topic=topic,
            user=user,
            label=label)
        result_response = ".برچسب جدید ایجاد شد"

    return JsonResponse({
        "result_response": result_response
    })


def save_topic_label(request, topic_id, username, label):
    result_response = ""

    user = User.objects.get(username=username)
    topic = ClusterTopic.objects.get(id=topic_id)

    try:

        user_topic_label = UserTopicLabel.objects.get(
            topic=topic,
            user=user)

        user_topic_label.label = label
        user_topic_label.save()
        result_response = ".برچسب موضوع تغییر یافت"

    except:
        UserTopicLabel.objects.create(
            topic=topic,
            user=user,
            label=label)
        result_response = ".برچسب جدید ایجاد شد"

    return JsonResponse({
        "result_response": result_response
    })


def SaveUser(request, firstname, lastname, nationalcode, email, phonenumber, role, username, password, ip, expertise):
    print("************", nationalcode, "**************")
    user_nationalcode = User.objects.filter(national_code=nationalcode)
    user_username = User.objects.filter(username=username)
    user_email = User.objects.filter(email=email)
    if nationalcode != "0" and user_nationalcode.count() > 0:
        return JsonResponse({"status": "duplicated national code"})
    elif user_username.count() > 0:
        return JsonResponse({"status": "duplicated username"})
    elif user_email.count() > 0:
        return JsonResponse({"status": "duplicated email"})
    else:
        hashed_pwd = make_password(password)
        last_login = datetime.datetime.now()
        user = User.objects.create(first_name=firstname, last_name=lastname, national_code=nationalcode, email=email,
                                   role_id=role,
                                   mobile=phonenumber, username=username, password=hashed_pwd, last_login=last_login,
                                   is_super_user=0, is_active=0)

        for e in expertise.split(','):
            User_Expertise.objects.create(user_id_id=user.id, experise_id_id=e)
        SaveUserLog(user.id, ip, "signup")

    return JsonResponse({"status": "OK"})


def SetMyUserProfile(request):
    if request.method != 'POST':
        return JsonResponse({"status": "Method not supported"})

    data = json.loads(request.body)
    firstname = data["firstname"]
    lastname = data["lastname"]
    email = data["email"]
    phonenumber = data["phonenumber"]
    role = data["role"]
    avatar = data["avatar"]

    username = request.COOKIES.get('username')
    user_email = User.objects.filter(email=email).exclude(username=username)
    role = UserRole.objects.get(id=role)

    if user_email.count() > 0:
        return JsonResponse({"status": "duplicated email"})
    else:
        User.objects.filter(username=username).update(
            first_name=firstname,
            last_name=lastname,
            email=email,
            mobile=phonenumber,
            role=role, avatar=avatar)

    return JsonResponse({"status": "OK"})


def ToggleNoteStar(request, note_id):
    starred = DocumentNote.objects.get(id=note_id)
    if (starred.starred == True):
        starred.starred = False
    else:
        starred.starred = True
    starred.save()
    return JsonResponse({
        'starred': starred.starred
    })


def UserLogSaved(request, username, url, sub_url='0', ip='0'):
    # print(request.POST)

    user_id = User.objects.get(username=username).id
    date_time = datetime.datetime.now()

    if url == "0":
        url = None

    paeg_url = url

    if sub_url != "0":
        paeg_url = url + "/" + sub_url

    UserLogs.objects.create(user_id_id=user_id, user_ip=ip,
                            page_url=paeg_url, visit_time=date_time, detail_json=request.POST)

    return JsonResponse({"status": "OK"})


def UserDeployLogSaved(request, username, detail):
    user_id = User.objects.get(username=username).id
    date_time = datetime.datetime.now()

    DeployServer.objects.create(user_id_id=user_id, deploy_time=date_time, detail=detail)

    return JsonResponse({"status": "OK"})

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return [jy, jm, jd]


def getUserChartLogs(request, user_id, time_start, time_end):
    if time_start != "0" and time_end != "0":
        user_logs = UserLogs.objects.all().filter(visit_time__range=(
            time_start, time_end)).order_by("-visit_time")

    elif time_start == "0" and time_end != "0":
        user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

    elif time_start != "0" and time_end == "0":
        user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

    else:
        user_logs = UserLogs.objects.all().order_by("-visit_time")

    user_logs = user_logs.filter(user_id__isnull=False).order_by("-visit_time")

    chart_data = {}
    for log in user_logs:
        user_id_id = log.user_id
        if user_id_id not in chart_data:
            chart_data[user_id_id] = 1
        else:
            chart_data[user_id_id] += 1

    chart_data_list = []
    for user_id_id, count in chart_data.items():
        name = user_id_id.first_name + ' ' + user_id_id.last_name
        column = [name, count]
        chart_data_list.append(column)

    return JsonResponse({'user_chart_data_list': chart_data_list})


def GetDocumentCommentVoters(request, document_comment_id, agreed):
    if agreed == "true":
        agreed = True
    else:
        agreed = False
    votes = DocumentCommentVote.objects.filter(document_comment=document_comment_id, agreed=agreed)
    result = []
    for v in votes:
        created_at = str(jdatetime.strftime(jdatetime.utcfromtimestamp(v.created_at.timestamp()), "%H:%M:%S %Y-%m-%d"))
        modified_at = str(
            jdatetime.strftime(jdatetime.utcfromtimestamp(v.modified_at.timestamp()), "%H:%M:%S %Y-%m-%d"))
        result.append({"first_name": v.user.first_name, "last_name": v.user.last_name, "created_at": created_at
                          , "modified_at": modified_at})
    return JsonResponse({"result": result})


@allowed_users('admin_accept_user_comments')
def changeCommentState(request, comment_id, state):
    comment = DocumentComment2.objects.get(pk=comment_id)

    if state == "accepted":
        comment.is_accept = 1
    elif state == "rejected":
        comment.is_accept = -1

    comment.save()

    return JsonResponse({"status": state})


@allowed_users('admin_waiting_user', 'admin_accepted_user')
def changeUserState(request, user_id, state):
    if state == "accepted":
        accepted_user = User.objects.get(pk=user_id)
        accepted_user.is_active = 1
        accepted_user.save()

        return JsonResponse({"status": "accepted"})

    elif state == "rejected":
        accepted_user = User.objects.get(pk=user_id)
        accepted_user.is_active = -1
        accepted_user.save()

        return JsonResponse({"status": "rejected"})


def DeleteUser(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return JsonResponse({"status": "deleted"})


def getChartLogs(request, user_id, time_start, time_end):
    if user_id == 0:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end)).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().order_by("-visit_time")
    else:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end), user_id=user_id).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end,
                                                      user_id=user_id).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start,
                                                      user_id=user_id).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().filter(
                user_id=user_id).order_by("-visit_time")

    convert_month = {1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد',
                     6: 'شهریور', 7: 'مهر', 8: 'آبان', 9: 'آذر', 10: 'دی',
                     11: 'بهمن', 12: 'اسفند'}

    month_chart_data = {}
    hour_chart_data = {}
    for log in user_logs:
        time = log.visit_time
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = int(time[11:13])
        jalali = gregorian_to_jalali(year, month, day)

        month_name = convert_month[jalali[1]]
        if month_name not in month_chart_data:
            month_chart_data[month_name] = 1
        else:
            month_chart_data[month_name] += 1

        if hour not in hour_chart_data:
            hour_chart_data[hour] = 1
        else:
            hour_chart_data[hour] += 1

    month_chart_data_list = []
    for month, count in month_chart_data.items():
        column = [month, count]
        month_chart_data_list.append(column)

    hour_chart_data_list = []
    for hour, count in hour_chart_data.items():
        column = [hour, count]
        hour_chart_data_list.append(column)

    chart_data = {}
    for log in user_logs:
        url = log.page_url
        if url == None:
            url = 'home'
        if url not in chart_data:
            chart_data[url] = 1
        else:
            chart_data[url] += 1

    chart_data_list = []
    for url, count in chart_data.items():
        column = [url, count]
        chart_data_list.append(column)

    panels = {'search': {'chart_dict': {}, 'chart_list': []},
              'graph': {'chart_dict': {}, 'chart_list': []}
              }

    for panel in panels:
        panel_chart_data = panels[panel]['chart_dict']

        if user_id == 0:
            user_logs = UserLogs.objects.all().filter(
                page_url=panel).order_by("-visit_time")
        else:
            user_logs = UserLogs.objects.all().filter(
                page_url=panel, user_id=user_id).order_by("-visit_time")

        for log in user_logs:
            detail_type = log.detail_json['detail_type']
            if detail_type not in panel_chart_data:
                panel_chart_data[detail_type] = 1
            else:
                panel_chart_data[detail_type] += 1

        for detail_type, count in panel_chart_data.items():
            column = [detail_type, count]
            panels[panel]['chart_list'].append(column)

        panels[panel]['result_data'] = panels[panel]['chart_list']

    # 'chart_data_information': panels['information']['chart_list'],
    return JsonResponse({'chart_data_list': chart_data_list, 'chart_data_search': panels['search']['chart_list'],
                         'chart_data_graph': panels['graph']['chart_list'],
                         'month_chart_data_list': month_chart_data_list, 'hour_chart_data_list': hour_chart_data_list})


def getTableUserLogs(request, user_id, time_start, time_end):
    if user_id == 0:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end)).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().order_by("-visit_time")
    else:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end), user_id=user_id).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end,
                                                      user_id=user_id).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start,
                                                      user_id=user_id).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().filter(
                user_id=user_id).order_by("-visit_time")

    keyword_table_data = {}
    for log in user_logs:
        if log.page_url == "search":
            if log.detail_json['detail_type'] == "نتایج جست و جو":
                keyword = log.detail_json['search_text']
                if keyword not in keyword_table_data:
                    keyword_table_data[keyword] = 1
                else:
                    keyword_table_data[keyword] += 1

    keyword_table_data_list = []
    i = 1
    for keyword_name, count in keyword_table_data.items():
        column = [i, keyword_name, count]
        keyword_table_data_list.append(column)
        i += 1

    return JsonResponse({'keyword_table_data_list': keyword_table_data_list})


def getUserLogs(request, user_id, time_start, time_end):
    if user_id == 0:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end)).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().order_by("-visit_time")
    else:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end), user_id=user_id).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end,
                                                      user_id=user_id).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start,
                                                      user_id=user_id).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().filter(
                user_id=user_id).order_by("-visit_time")

    user_logs = user_logs.filter(user_id__isnull=False).order_by("-visit_time")[:100]

    result = []
    for log in user_logs:
        id = log.id
        name = log.user_id.first_name + ' ' + log.user_id.last_name
        url = log.page_url
        if url == None:
            url = 'home'
        time = log.visit_time
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hours = time[11:19]
        jalali = gregorian_to_jalali(year, month, day)
        Date = str(jalali[0]) + '/' + str(jalali[1]) + '/' + str(jalali[2]) + ' ' + hours

        detail = log.detail_json

        result.append({
            "id": id,
            "name": name,
            'url': url,
            'time': Date,
            'detail': detail
        })

    return JsonResponse({'user_logs': result})


@allowed_users('admin_user_report_bug')
def ChangeReportBugCheckStatus(request, report_bug_id):
    report_bug = Report_Bug2.objects.get(id=report_bug_id)
    if report_bug.checked == False:
        report_bug.checked = True
    else:
        report_bug.checked = False
    report_bug.save()

    return JsonResponse({"status": "OK"})



@allowed_users('admin_user_report_bug')
def GetReportBugByFilter(request, panel_id, branch_id, status):
    if status == "T":
        status = True
    elif status == "F":
        status = False
    reports = Report_Bug2.objects.all().order_by('checked', 'date')
    if panel_id != "all":
        panel_id = int(panel_id)
        reports = reports.filter(panel_id=panel_id)
    if branch_id != "all":
        branch_id = int(branch_id)
        reports = reports.filter(branch_id=branch_id)
    if status != "all":
        reports = reports.filter(checked=status)

    report_bug = []
    branches = {}
    for report in reports:
        report_bug.append({
            'id': report.id,
            'first_name': report.user.first_name,
            'last_name': report.user.last_name,
            'email': report.user.email,
            'panel_name': report.panel_id.panel_persian_name,
            'branch_name': report.branch_id.panel_persian_name,
            'report_bug_text': report.report_bug_text,
            'date': report.date,
            'checked': report.checked,
        })
        branch = branches.get(report.branch_id.panel_persian_name)
        if branch:
            branches[report.branch_id.panel_persian_name] += 1
        else:
            branches[report.branch_id.panel_persian_name] = 1

    return JsonResponse({'report_bug': report_bug, 'branches_count': branches})



def AILDADocFromTopic(request, topic_id):
    topic_paragraphs = []
    temp = AILDAParagraphToTopic.objects.filter(topic__id=topic_id).order_by('-score').values()[:100]
    keywords = AIParagraphLDATopic.objects.get(id=topic_id).words
    sorted_word_list = [k for k, v in sorted(keywords.items(), reverse=True, key=lambda item: float(item[1]))]
    keywords = " - ".join(sorted_word_list)
    for record in temp:
        paragraph_id = record['paragraph_id']
        paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
        try:
            subjects_name = ParagraphsSubject.objects.get(paragraph__id=paragraph_id, version__id=12)

            topic_paragraphs.append({

                "paragraph_text": paragraph.text,
                "paragraph_id": paragraph.id,
                "document_id": paragraph.document_id.id,
                "document_name": paragraph.document_id.name,
                "subject1_name": subjects_name.subject1_name,
                "subject2_name": subjects_name.subject2_name,
                "subject3_name": subjects_name.subject3_name,
                "score": record['score']
            })
        except:
            topic_paragraphs.append({
                "paragraph_text": paragraph.text,
                "paragraph_id": paragraph.id,

                "document_id": paragraph.document_id.id,
                "document_name": paragraph.document_id.name,
                "subject1_name": 0,
                "subject2_name": None,
                "subject3_name": None,
                "score": record['score']
            })

    return JsonResponse({'topic_paragraphs': topic_paragraphs, 'keywords': keywords})


def AILDAWordCloudTopic(request, topic_id):
    Could_data = []
    keywords = AIParagraphLDATopic.objects.get(id=topic_id)

    for key, value in keywords.words.items():
        Could_data.append({"x": key, "value": value})

    return JsonResponse({'Could_data': Could_data})


def AILDASubjectChartTopic(request, topic_id):
    data = AIParagraphLDATopic.objects.get(id=topic_id)

    chart_data = data.subjects_list_chart_data_json['data']
    paragraph_count = data.paragraph_count
    dominant_subject_name = data.dominant_subject_name
    correlation_score = data.correlation_score

    return JsonResponse({'chart_data': chart_data,
                         'paragraph_count': paragraph_count,
                         'dominant_subject_name': dominant_subject_name,
                         'correlation_score': correlation_score})


def GetLDAForDocByID(request, document_id):
    doc = Document.objects.get(id=document_id)
    language = Country.objects.get(id=doc.country_id.id).language
    if language == 'کتاب':
        book = Book.objects.get(document_id=doc.id)
    elif language == 'استاندارد':
        sta = Standard.objects.get(document_id=doc.id)
    topics = AILDATopic.objects.filter(country__id=doc.country_id.id)
    topic_documents = []

    for i in range(len(topics)):
        temp = AILDADocToTopic.objects.filter(topic__id=topics[i].id, document__id=document_id)
        if len(temp) > 0:
            topic_words = ""
            for j in topics[i].words.items():
                topic_words += j[0] + "، "

            topic_documents.append({
                "topic_id": topics[i].id,
                "topic_words": topic_words[:-2],
                "score": temp[0].score
            })
            # else:
            #     topic_documents.append({
            #         "topic_id": topics[i].id,
            #         "topic_words": topics[i].words,
            #         "score": 0
            #     })

            others_doc_with_this_topic = []

            sub_temp = AILDADocToTopic.objects.filter(topic__id=topics[i].id)
            for j in range(len(sub_temp)):
                if sub_temp[j].document.id != document_id:
                    others_doc_with_this_topic.append({
                        "document_id": sub_temp[j].document.id,
                        "document_name": sub_temp[j].document.name,
                        "score": sub_temp[j].score
                    })

            others_doc_with_this_topic = sorted(others_doc_with_this_topic, key=lambda k: k['score'], reverse=True)
            topic_documents[-1]['others_doc_with_this_topic'] = others_doc_with_this_topic

    topic_documents = sorted(topic_documents, key=lambda k: k['score'], reverse=True)

    for i in range(len(topic_documents)):
        topic_documents[i]['topic_name'] = 'موضوع ' + str(i + 1)

    _id = None
    _name = None
    if language == "کتاب":
        _id = book.id
        _name: book.name
    elif language == "استاندارد":
        _id = sta.id
        _name: sta.subject
    return JsonResponse({
        "document_id": doc.id,
        "document_name": doc.name,
        "_id": _id,
        "_name": _name,
        'topic_documents': topic_documents
    })

def get_stopword_list(file_name):
    stop_words = []

    stop_words_file = str(Path(config.PERSIAN_PATH, file_name))
    with open(stop_words_file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            stop_words.append(line)
    f.close()
    return stop_words


def GetKeywordsGeneralDefinitionByDocumentId(request, document_id, word):
    keyword_result = DocumentGeneralDefinition.objects.get(keyword=word, document_id=document_id)
    keyword_information = {}

    keyword_information['doc_id'] = keyword_result.document_id.id
    keyword_information['doc_name'] = keyword_result.document_id.name

    keyword_information['croped_text'] = keyword_result.keyword + ': ' + keyword_result.text

    return JsonResponse({'keyword_information': keyword_information})


def GetDocumentById(request, id):
    document = Document.objects.get(id=id)

    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_id.name

    approval_date = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date

    communicated_date = "نامشخص"
    if document.communicated_date != None:
        communicated_date = document.communicated_date

    type_name = "سایر"
    if document.type_id != None:
        type_name = document.type_id.name

    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_id.name

    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_id.name

    validation_type = document.revoked_type_name

    revoked_size = ""
    revoked_clauses = ""

    if validation_type != 'معتبر':
        try:
            revoked_doc = RevokedDocument.objects.get(dest_document__id=id)
            revoked_size = revoked_doc.revoked_size
            revoked_clauses = revoked_doc.revoked_clauses
        except:
            pass

    document_actors_chart_data = []
    if document.actors_chart_data != None:
        document_actors_chart_data = document.actors_chart_data['data']

    result = {"id": document.id,
              "name": document.name,
              "file_name": document.file_name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "level": level_name,
              "subject": subject_name,
              "type": type_name,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "communicated_date": communicated_date,
              "validation_type": validation_type,
              "revoked_size": revoked_size,
              "revoked_clauses": revoked_clauses,
              "word_count": document.word_count,
              "distinct_word_count": document.distinct_word_count,
              "stopword_count": document.stopword_count,
              "actors_chart_data": document_actors_chart_data
              }
    return JsonResponse({'document_information': [result]})


def GetReferences2Doc(request, document1_id, document2_id):
    doc1_name = Document.objects.get(id=document1_id).name
    doc2_name = Document.objects.get(id=document2_id).name

    query_ref_form_doc1 = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document1_id
                }
            },
            "must": {"match_phrase": {"attachment.content": doc2_name}}
        }
    }
    query_ref_form_doc2 = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document2_id
                }
            },
            "must": {"match_phrase": {"attachment.content": doc1_name}}
        }
    }

    index_name = standardIndexName(Document.objects.get(id=document1_id).country_id,
                                   DocumentParagraphs.__name__) + "_graph"

    response_ref_form_doc1 = client.search(index=index_name,
                                           _source_includes=['document_id', 'paragraph_id', 'attachment.content'],
                                           request_timeout=40,
                                           query=query_ref_form_doc1,
                                           size=5000,
                                           highlight={
                                               "order": "score",
                                               "fields": {
                                                   "attachment.content":
                                                       {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                                        "number_of_fragments": 0
                                                        }
                                               }}
                                           )['hits']['hits']

    response_ref_form_doc2 = client.search(index=index_name,
                                           _source_includes=['document_id', 'paragraph_id', 'attachment.content'],
                                           request_timeout=40,
                                           query=query_ref_form_doc2,
                                           size=5000,
                                           highlight={
                                               "order": "score",
                                               "fields": {
                                                   "attachment.content":
                                                       {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                                        "number_of_fragments": 0
                                                        }
                                               }}
                                           )['hits']['hits']

    result_text1 = ""
    for row in response_ref_form_doc1:
        print(row)
        if 'highlight' in row:
            result_text1 += row["highlight"]["attachment.content"][0] + "\n"

    result_text2 = ""
    for row in response_ref_form_doc2:
        if 'highlight' in row:
            result_text2 += row["highlight"]["attachment.content"][0] + "\n"

    return JsonResponse({'references_from_doc1': result_text1, 'references_from_doc2': result_text2})


def GetCommonWords2Doc(request, document1_id, document2_id):
    document1_word = DocumentWords.objects.filter(
        document_id_id=document1_id).values("word")
    CommonWords = DocumentWords.objects.filter(
        document_id_id=document2_id, word__in=document1_word).values("word")
    CommonWords = CommonWords.annotate(text_len=Length(
        'word')).filter(text_len__gte=2).values("word")
    result1 = []
    for word in CommonWords:
        result1.append(word["word"])
    result1 = list(set(result1))

    document1_keyword = DocumentKeywords.objects.filter(
        document_id_id=document1_id).values("keyword_id")
    CommonKeyWords = DocumentKeywords.objects.filter(
        document_id_id=document2_id, keyword_id__in=document1_keyword).values("keyword_id__word")
    CommonKeyWords = CommonKeyWords.annotate(text_len=Length(
        'keyword_id__word')).filter(text_len__gte=2).values('keyword_id__word')
    result2 = []
    for word in CommonKeyWords:
        result2.append(word['keyword_id__word'])
    result2 = list(set(result2))

    return JsonResponse({'common_words': result1, 'common_keywords': result2})


def getUserDeployLogs(request):
    user_logs = DeployServer.objects.all().order_by("-deploy_time")

    result = []
    for log in user_logs:
        time = log.deploy_time
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = time[11:13]
        minute = time[14:16]
        jalali = gregorian_to_jalali(year, month, day)

        Date = str(jalali[0]) + '/' + str(jalali[1]) + '/' + str(jalali[2])
        name = log.user_id.first_name + ' ' + log.user_id.last_name
        time = hour + ':' + minute

        result.append({
            "id": log.id,
            "name": name,
            'date': Date,
            'time': time,
            'detail': log.detail
        })

    return JsonResponse({'user_logs': result})



def GetUnknownDocuments(request):
    docs = Document.objects.filter(level_id=None)
    result = []
    for d in docs:
        doc = {"name": d.name,
               "reference": d.approval_reference_name,
               "reference_date": d.approval_date
               }
        if not d.type_id is None:
            doc["type"] = d.type_id.name
        else:
            doc["type"] = '-'

        if not d.subject_id is None:
            doc["subject"] = d.subject_id.name
        else:
            doc["subject"] = '-'

        if not d.country_id is None:
            doc["collection"] = d.country_id.name
        else:
            doc["collection"] = '-'

        result.append(doc)
    return JsonResponse({"result": result})


def GetSearchParameters(request, country_id):
    search_parameters = SearchParameters.objects.filter(country__id=country_id)
    parameters_result = {}

    for param in search_parameters:
        para_name = param.parameter_name
        options = param.parameter_values["options"]
        parameters_result[para_name] = options

    country = Country.objects.get(id=country_id)
    sub_areas = SubjectSubArea.objects.filter(subject_area_id__language=country.language).values('id', 'name',
                                                                                                 'subject_area_id__id',
                                                                                                 'subject_area_id__name')

    subject_area = {}
    for sub_area in sub_areas:
        if str(sub_area['subject_area_id__id']) + "#" + sub_area['subject_area_id__name'] in subject_area.keys():
            subject_area[str(sub_area['subject_area_id__id']) + "#" + sub_area['subject_area_id__name']]. \
                append((sub_area['id'], sub_area['name']))
        else:
            subject_area[str(sub_area['subject_area_id__id']) + "#" + sub_area['subject_area_id__name']] = [
                (sub_area['id'], sub_area['name'])]

    parameters_result['revoked_size'] = "<option value='جزئی' >جزئی</option>" + "<option value='کلی' >کلی</option>"

    return JsonResponse({"parameters_result": parameters_result, 'subject_area': subject_area}, )


def GetTypeByCountryId(request, country_id):
    type_list = Type.objects.all().order_by("id")
    result = []
    for row in type_list:
        type_id = row.id
        type_name = row.name
        type_color = row.color
        res = {
            "id": type_id,
            "type": type_name,
            "color": type_color.replace("\n", "")
        }
        result.append(res)
    return JsonResponse({'documents_type_list': result})


def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def filter_doc_fields(res_query, level_id, subject_id, type_id, approval_reference_id,
                      from_year, to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                      revoked_type_id, organization_type_id):
    if approval_reference_id != 0:
        approval_reference_name = ApprovalReference.objects.get(id=approval_reference_id).name
        approval_reference_name = arabic_preprocessing(approval_reference_name)
        approval_ref_query = {
            "term": {
                "approval_reference_name.keyword": approval_reference_name
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if level_id != 0:
        level_name = Level.objects.get(id=level_id).name
        level_query = {
            "term": {
                "level_name.keyword": level_name
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if subject_id != 0:
        subject_name = Subject.objects.get(id=subject_id).name
        subject_query = {
            "term": {
                "subject_name.keyword": subject_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if type_id != 0:
        type_name = Type.objects.get(id=type_id).name

        type_name = Local_preprocessing(type_name)

        type_query = {
            "term": {
                "type_name.keyword": type_name
            }
        }
        res_query['bool']['filter'].append(type_query)

    # ---------------------------------------------------------
    if revoked_type_id != 0:
        revoked_type_name = RevokedType.objects.get(id=revoked_type_id).name
        revoked_type_name_query = {
            "term": {
                "revoked_type_name.keyword": revoked_type_name
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    # ---------------------------------------------------------
    if organization_type_id != '0':
        organization_type_name = organization_type_id
        organization_type_name_query = {
            "match_phrase": {
                "organization_type_name": organization_type_name
            }
        }
        res_query['bool']['filter'].append(organization_type_name_query)

    # ----------------------------------------------------------

    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "approval_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    # ----------------------------------------------------------

    if from_advisory_opinion_count != 0:
        advisory_opinion_count_query = {
            "range": {
                "advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    return res_query


def SearchDocument_ES(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                      from_advisory_opinion_count,
                      from_interpretation_rules_count, revoked_type_id, place, text, search_type, curr_page):
    organization_type_id = '0'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                      to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                      revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    # print('search_query')
    # print(res_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)
    # index_name = "doticfull_document"

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },
        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "type-agg": {
            "terms": {
                "field": "type_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        },
        "appr-agg": {
            "multi_terms": {
                "terms": [{
                    "field": "approval_year"
                }, {
                    "field": "subject_name.keyword"
                }]
            }
        }
    }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date',
                                               'subject_name',
                                               "level_name", 'type_name', 'approval_year', 'communicated_date',
                                               'raw_file_name',
                                               'advisory_opinion_count', 'interpretation_rules_count',
                                               'revoked_type_name'],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=search_result_size

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query
                             )
    max_score = response['hits']['hits'][0]['_score'] if total_hits > 0 else 1
    max_score = max_score if max_score > 0 else 1

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        'max_score': max_score,
        "curr_page": curr_page,
        'aggregations': aggregations})


def filter_doc_actor_fields(res_query, level_id, subject_id, type_id, approval_reference_id,
                            from_year, to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                            revoked_type_id, organization_type_id):
    if approval_reference_id != 0:
        approval_reference_name = ApprovalReference.objects.get(id=approval_reference_id).name
        approval_reference_name = arabic_preprocessing(approval_reference_name)
        approval_ref_query = {
            "term": {
                "document_approval_reference_name.keyword": approval_reference_name
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if level_id != 0:
        level_name = Level.objects.get(id=level_id).name
        level_query = {
            "term": {
                "document_level_name.keyword": level_name
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if subject_id != 0:
        subject_name = Subject.objects.get(id=subject_id).name
        subject_query = {
            "term": {
                "document_subject_name.keyword": subject_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if type_id != 0:
        type_name = Type.objects.get(id=type_id).name

        type_name = Local_preprocessing(type_name)

        type_query = {
            "term": {
                "document_type_name.keyword": type_name
            }
        }
        res_query['bool']['filter'].append(type_query)

    # ---------------------------------------------------------
    if revoked_type_id != 0:
        revoked_type_name = RevokedType.objects.get(id=revoked_type_id).name
        revoked_type_name_query = {
            "term": {
                "document_revoked_type_name.keyword": revoked_type_name
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    # ---------------------------------------------------------
    if organization_type_id != '0':
        organization_type_name = organization_type_id
        organization_type_name_query = {
            "match_phrase": {
                "document_organization_type_name": organization_type_name
            }
        }
        res_query['bool']['filter'].append(organization_type_name_query)

    # ----------------------------------------------------------

    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "document_approval_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    # ----------------------------------------------------------

    if from_advisory_opinion_count != 0:
        advisory_opinion_count_query = {
            "range": {
                "document_advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "document_interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    return res_query

def exact_search_text_doc_actor(res_query, place, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'عنوان':
        title_query = {
            "match_phrase": {
                "document_name": text
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif place == 'متن':
        content_query = {
            "match_phrase": {
                "attachment.content": text
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)

    else:
        title_content_query = {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "document_name": text
                        }
                    },
                    {
                        "match_phrase": {
                            "attachment.content": text
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)

    return res_query



def boolean_search_text_doc_actor(res_query, place, text, operator, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'عنوان':
        title_query = {
            "match": {
                "document_name": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif place == 'متن':
        content_query = {
            "match": {
                "attachment.content": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)


    else:
        title_content_query = {
            "bool": {

                "should": [
                    {
                        "match": {
                            "document_name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    },
                    {
                        "match": {
                            "attachment.content": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)

    return res_query



def entropy(numbers):
    s = sum(numbers)
    if s > 0:
        probabilities = [n / s for n in numbers]
    else:
        probabilities = [0] * len(numbers)
    etp = 0
    for p in probabilities:
        try:
            etp -= (p * math.log2(p))
        except:
            continue
    return round(etp, 2)


def chart_entropy(chart_data):
    # if len(chart_data) == 0:
    #     return {'sum_columns':[0]}, {'sum_columns':['صفر']}, {'sum_columns':[0]}, {'sum_columns':[0]}
    chart_entropies, chart_parallelism, chart_mean, chart_std, chart_normal_entropies = {
                                                                                            'sum_columns': []}, {}, {}, {}, {}
    for instance in chart_data:
        instance_sum = 0
        for j in range(1, len(instance)):
            instance_sum += instance[j]
            try:
                chart_entropies['column_' + str(j)].append(instance[j])
            except:
                chart_entropies['column_' + str(j)] = [instance[j]]

        chart_entropies['sum_columns'].append(instance_sum)

    temp = math.log2(len(chart_data))
    for key, value in chart_entropies.items():
        e = entropy(value)
        chart_mean[key] = round(np.mean(value), 2)
        chart_std[key] = round(np.std(value), 2)
        try:
            normal_e = round(e / temp, 2)
        except:
            normal_e = 0
        chart_normal_entropies[key] = normal_e
        if normal_e > 0.8:
            plr = 'خیلی زیاد'
        elif normal_e > 0.6:
            plr = 'زیاد'
        elif normal_e > 0.4:
            plr = 'متوسط'
        elif normal_e > 0.2:
            plr = 'کم'
        elif normal_e > 0.0:
            plr = 'خیلی کم'
        elif normal_e == 0.0:
            plr = 'صفر'
        chart_parallelism[key] = plr
        chart_entropies[key] = e

    return chart_entropies, chart_parallelism, chart_mean, chart_std, chart_normal_entropies


def GetActorsChartData_ES_2(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year,
                            to_year, from_advisory_opinion_count,
                            from_interpretation_rules_count, revoked_type_id, place, text, search_type):
    organization_type_id = '0'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_actor_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                            to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                            revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text_doc_actor(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text_doc_actor(res_query, place, text, search_type, ALL_FIELDS)

    # print('chart_query')
    # print(res_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    res_agg = {
        "actor-name-agg": {
            "multi_terms": {
                "terms": [{
                    "field": "actor_name.keyword",
                },
                    {
                        "field": "actor_id",
                    }],
                "size": bucket_size
            },
            "aggs": {
                "actor-type-name-agg": {
                    "terms": {
                        "field": "actor_type_name.keyword",
                        "size": bucket_size
                    }
                },
            },
        },
    }

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id'],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             # from_=from_value,
                             size=0,
                             # track_total_hits=True,
                             )

    aggregations = response['aggregations']

    # Calculate role frequency of actors
    actors_chart_data = []
    for actor in aggregations['actor-name-agg']['buckets']:
        actor_id = actor["key"][1]
        actor_name = actor["key"][0]
        roles = actor["actor-type-name-agg"]['buckets']
        motevali_count = 0
        hamkar_count = 0
        salahiat_count = 0

        for item in roles:
            if item['key'] == 'متولی اجرا':
                motevali_count = item['doc_count']
            elif item['key'] == 'همکار':
                hamkar_count = item['doc_count']
            elif item['key'] == 'دارای صلاحیت اختیاری':
                salahiat_count = item['doc_count']

        column_data = [actor_name, motevali_count, hamkar_count, salahiat_count]
        actors_chart_data.append(column_data)

    if len(actors_chart_data) < 1:
        temp = {'sum_columns': 0, 'column_1': 0, 'column_2': 0, 'column_3': 0}
        entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = temp, \
                                                                                   {'sum_columns': 'صفر',
                                                                                    'column_1': 'صفر',
                                                                                    'column_2': 'صفر',
                                                                                    'column_3': 'صفر'}, \
                                                                                   temp, temp, temp
    else:
        entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = chart_entropy(actors_chart_data)

    return JsonResponse({"actors_chart_data": actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })


def SearchGeneralDocumentsDefinition(request, country_id, mode, text):
    words = arabic_preprocessing(text).split(" ")
    if mode.lower() == 'or':
        document_definitions = DocumentGeneralDefinition.objects.filter(
            reduce(operator.or_, (Q(keyword__icontains=word) for word in words)),
            document_id__country_id__id=country_id)

    elif mode.lower() == 'and':
        document_definitions = DocumentGeneralDefinition.objects.filter(
            reduce(operator.and_, (Q(keyword__icontains=word) for word in words)),
            document_id__country_id__id=country_id)
    else:
        document_definitions = DocumentGeneralDefinition.objects.filter(keyword__icontains=text,
                                                                        document_id__country_id__id=country_id)

    keywords_information = {}

    for d in document_definitions:
        keyword = d.keyword
        doc_id = d.document_id.id
        doc_name = d.document_id.name
        doc_info = {'id': doc_id, 'name': doc_name}

        if keyword not in keywords_information:
            keywords_information[keyword] = [doc_info]
        else:
            document_list = keywords_information[keyword]
            document_list.append(doc_info)
            keywords_information[keyword] = document_list
    return JsonResponse({'keywords_information': keywords_information})



def Get_Documents_RefGraph_ES(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year,
                              to_year, from_advisory_opinion_count,
                              from_interpretation_rules_count, revoked_type_id, place, text, search_type, curr_page):
    organization_type_id = '0'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                      to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                      revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    response = client.search(index=index_name,
                             _source_includes=['document_id'],
                             request_timeout=40,
                             query=res_query,
                             size=500

                             )

    documents_id_list = [row['_id'] for row in response['hits']['hits']]

    graph_edge_list = Graph.objects.filter(
        src_document_id__id__in=documents_id_list, dest_document_id__id__in=documents_id_list)

    nodes_list = []
    added_node = []
    edges_list = []
    added_edge = []

    for edge in graph_edge_list:

        src_id = str(edge.src_document_id_id)
        src_name = edge.src_document_id.name
        src_color = str(edge.src_document_id.type_id.color) if edge.src_document_id.type_id is not None else "#000000"

        src_node = {"id": src_id, "name": src_name, "style": {"fill": src_color}}

        dest_id = str(edge.dest_document_id_id)
        dest_name = edge.dest_document_id.name
        dest_color = str(
            edge.dest_document_id.type_id.color) if edge.dest_document_id.type_id is not None else "#000000"

        dest_node = {"id": dest_id, "name": dest_name, "style": {"fill": dest_color}}

        weight = edge.weight

        if src_id not in added_node:
            nodes_list.append(src_node)
            added_node.append(src_id)

        if dest_id not in added_node:
            nodes_list.append(dest_node)
            added_node.append(dest_id)

        edge_obj = {"source": src_id, "source_name": src_name,
                    "target": dest_id, "target_name": dest_name,
                    "weight": weight}

        if [dest_id, src_id] not in added_edge and src_id != dest_id:
            edges_list.append(edge_obj)
            added_edge.append([src_id, dest_id])

    return JsonResponse({"Nodes_data": nodes_list, "Edges_data": edges_list})

def filter_doc_fields_COLUMN(res_query, level_name, subject_name, type_name, approval_reference_name,
                             from_year, to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                             revoked_type_name, organization_type_name):
    if approval_reference_name != "همه":
        approval_reference_name = arabic_preprocessing(approval_reference_name)
        approval_ref_query = {
            "term": {
                "approval_reference_name.keyword": approval_reference_name
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if level_name != "همه":
        level_query = {
            "term": {
                "level_name.keyword": level_name
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if subject_name != "همه":
        subject_query = {
            "term": {
                "subject_name.keyword": subject_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if type_name != "همه":
        type_name = Local_preprocessing(type_name)

        type_query = {
            "term": {
                "type_name.keyword": type_name
            }
        }
        res_query['bool']['filter'].append(type_query)

    # ---------------------------------------------------------
    if revoked_type_name != "همه":
        revoked_type_name_query = {
            "term": {
                "revoked_type_name.keyword": revoked_type_name
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    # ---------------------------------------------------------
    if organization_type_name != 'همه':
        organization_type_name_query = {
            "match_phrase": {
                "organization_type_name": organization_type_name
            }
        }
        res_query['bool']['filter'].append(organization_type_name_query)

    # ----------------------------------------------------------

    First_Year = 1000
    Last_Year = 1403

    if from_year != "همه" or to_year != "همه":
        from_year = int(from_year) if from_year != "همه" else First_Year
        to_year = int(to_year) if to_year != "همه" else Last_Year

        year_query = {
            "range": {
                "approval_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    # ----------------------------------------------------------

    if from_advisory_opinion_count != 0:
        advisory_opinion_count_query = {
            "range": {
                "advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    return res_query


def SearchDocuments_Column_ES(request, country_id, level_name, subject_name, type_name, approval_reference_name,
                              from_year, to_year, from_advisory_opinion_count,
                              from_interpretation_rules_count, revoked_type_name, place, text, search_type, curr_page):
    organization_type_name = 'همه'

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = False

    res_query['bool']['filter'] = []
    res_query = filter_doc_fields_COLUMN(res_query, level_name, subject_name, type_name, approval_reference_name,
                                         from_year, to_year, from_advisory_opinion_count,
                                         from_interpretation_rules_count, revoked_type_name, organization_type_name)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date',
                                               'subject_name',
                                               "level_name", 'type_name', 'raw_file_name'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=search_result_size

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page})



def GetActorsDict(request):
    actorsDict = {}
    actors = Actor.objects.all().values('id', 'name',
                                        'actor_category_id__id',
                                        'actor_category_id__name',
                                        'forms')

    for actor in actors:
        actorsDict[actor['id']] = {
            'name': actor['name'],
            'category_id': actor['actor_category_id__id'],
            'category_name': actor['actor_category_id__name'],
            'forms': actor['forms'].split('/')
        }

    return JsonResponse({"actorsDict": actorsDict})



def GetActorsList(request):
    actorsList = []
    actors = Actor.objects.all().values('forms')

    for actor in actors:
        forms_list = actor['forms'].split('/')
        for actor_form in forms_list:
            actorsList.append(actor_form)

    return JsonResponse({"actorsList": actorsList})


def filter_document_actor_fields(res_query, role_ids=None, area_id=0, actor_id=0, actor_ids=None, actor_name='',
                                 role_name='', doc_year=0):
    if role_ids is not None:
        role_ids = [int(item) for item in role_ids]
    if actor_ids is not None:
        actor_ids = [int(item) for item in actor_ids]

    if role_ids is not None and 0 not in role_ids:
        approval_ref_query = {
            "terms": {
                "actor_type_id": role_ids
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if area_id != 0:
        level_query = {
            "term": {
                "actor_area_id": area_id
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if doc_year != 0:
        year_query = {
            "term": {
                "document_approval_year": doc_year
            }
        }
        res_query['bool']['filter'].append(year_query)

    # ---------------------------------------------------------
    if actor_id != 0:
        actor_query = {
            "term": {
                "actor_id": actor_id
            }
        }
        res_query['bool']['filter'].append(actor_query)

    # ---------------------------------------------------------
    if actor_ids is not None and 0 not in actor_ids:
        subject_query = {
            "terms": {
                "actor_id": actor_ids
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if actor_name != '':
        actor_name_query = {
            "term": {
                "actor_name.keyword": actor_name
            }
        }
        res_query['bool']['filter'].append(actor_name_query)

    # ---------------------------------------------------------
    if role_name != '' and role_name != 'برآیند نقش\u200cها':
        role_name_query = {
            "term": {
                "actor_type_name.keyword": role_name
            }
        }
        res_query['bool']['filter'].append(role_name_query)

    return res_query



def GetColumnParagraphsByActorRoleName_Modal_es_2(request, actor_name, role_name, curr_page,
                                                  country_id, level_id, subject_id, type_id, approval_reference_id,
                                                  from_year, to_year, from_advisory_opinion_count,
                                                  from_interpretation_rules_count, revoked_type_id, place,
                                                  text, search_type):
    organization_type_id = '0'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    detail_result_size = 10
    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_name=role_name,
        actor_name=actor_name)

    if not all(field == 0 for field in fields):
        res_query = filter_doc_actor_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                            to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                            revoked_type_id, organization_type_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text_doc_actor(res_query, place,
                                                    text, 'filter' not in res_query['bool'])
        else:
            res_query = boolean_search_text_doc_actor(res_query, place,
                                                      text,
                                                      search_type, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * detail_result_size

    # print(res_query)

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id',
                                               'actor_name',
                                               'actor_name',
                                               'document_id',
                                               "document_name",
                                               'attachment.content',
                                               'actor_type_name',
                                               'current_actor_form',
                                               'general_definition_text',
                                               'ref_paragraph_text'],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             from_=from_value,
                             size=detail_result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             },
                             # size=0,
                             # track_total_hits=True,
                             )

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    max_page = ((total_hits - 1) // detail_result_size) + 1

    # print(response['hits']['hits'][0]['highlight'])

    actor_paragraphs_result = {}
    for res in response['hits']['hits']:
        # highlight =
        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if (
                text == "empty" or 'highlight' not in res.keys()) else res["highlight"]["attachment.content"][0]
        paragraph_actor_role = res["_source"]["actor_type_name"]
        paragraph_actor_form = res["_source"]["current_actor_form"]
        paragraph_actor_name = res["_source"]["actor_name"]

        ref_text = ''
        para_ref_to_general_def_text = ''
        if res["_source"]["general_definition_text"] != 'نامشخص':
            para_ref_to_general_def_text = res["_source"]["general_definition_text"]
            ref_text = para_ref_to_general_def_text

        para_ref_to_para_text = ''
        if res["_source"]["ref_paragraph_text"] != 'نامشخص':
            para_ref_to_para_text = res["_source"]["ref_paragraph_text"]
            ref_text = para_ref_to_para_text

        is_ref_actor = (para_ref_to_general_def_text != 'نامشخص' or para_ref_to_para_text != 'نامشخص')

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'actor_name': paragraph_actor_name,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        if paragraph_id not in actor_paragraphs_result:
            actor_paragraphs_result[paragraph_id] = paragraph_info

    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result,
                         'max_page': max_page})


def GetSearchDetails_ES_2(request, document_id, search_type, text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)

    local_index = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    # local_index = "doticfull_documentparagraphs_graph"

    result_text = ''
    place = 'متن'

    res_query = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document_id
                }
            }
        }
    }

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, False)
        else:
            if search_type == "and":
                search_type = "or"
            res_query = boolean_search_text(res_query, place, text, search_type, False)

    response = client.search(index=local_index,
                             _source_includes=['document_id', 'paragraph_id', 'document_name', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<span class='text-primary fw-bold'>"], "post_tags": ["</span>"],
                                          "number_of_fragments": 0
                                          }
                                 }}
                             )

    print("======= res query =============")
    print(res_query)
    result = response['hits']['hits']

    return JsonResponse({"result": result})



def GetAllUsers_Commented(reauest, user_name, user_type):
    all_other_users = User.objects.filter(is_active=1).exclude(username=user_name).values(
        'id').distinct()

    followed_users = UserFollow.objects.filter(follower__username=user_name,
                                               follower__is_active=1).values('following__id').distinct()

    un_followed_users = User.objects.filter(is_active=1).exclude(
        username=user_name).exclude(id__in=followed_users).values('id').distinct()

    if user_type == 'دنبال شده':
        other_users = User.objects.filter(id__in=followed_users)

    elif user_type == 'دنبال نشده':
        other_users = User.objects.filter(id__in=un_followed_users)

    else:
        other_users = User.objects.filter(id__in=all_other_users)

    other_users = other_users.exclude(username=user_name)

    other_user_result = []

    for user in other_users:
        user_info = {
            "id": user.id,
            "user_name": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        other_user_result.append(user_info)

    return JsonResponse({"other_users_info": other_user_result})


def GetAllUserCommentHashtags(request):
    tags = DocumentCommentHashTag.objects.all()
    result = []
    for t in tags:
        result.append({"id": t.id, "name": t.hash_tag})
    return JsonResponse({"hash_tags": result})


def follow(request, follower_username, following_user_id):
    try:
        follow_info = UserFollow.objects.get(follower__username=follower_username, following__id=following_user_id)
        return JsonResponse({"status": "already followed!"})
    except:
        follower = User.objects.get(username=follower_username)
        following = User.objects.get(id=following_user_id)
        UserFollow.objects.create(follower=follower, following=following)
        return JsonResponse({"status": "follow_request_sent!"})



def unfollow(request, follower_username, following_user_id):
    try:
        follow_info = UserFollow.objects.get(follower__username=follower_username, following__id=following_user_id)
        follow_info.delete()
        return JsonResponse({"status": "successfully unfollowed!"})
    except:
        return JsonResponse({"status": "already unfollowed!"})


def GetUserComments(request, user_id, hashtag_id):
    username = request.COOKIES.get('username')

    result = []

    if user_id == 0 and hashtag_id == 0:
        return JsonResponse({"comments": result})

    if hashtag_id == 0:
        follow = UserFollow.objects.get(follower__username=username, following__id=user_id)
        if follow.accepted:
            comments = DocumentComment2.objects.filter(is_accept=1, show_info=True, user__id=user_id)
    elif user_id == 0:
        comments = DocumentComment2.objects.filter(is_accept=1, show_info=True, hash_tags__id=hashtag_id)
    else:
        follow = UserFollow.objects.get(follower__username=username, following__id=user_id)
        if follow.accepted:
            comments = DocumentComment2.objects.filter(is_accept=1, show_info=True, user__id=user_id,
                                                       hash_tags__id=hashtag_id)

    for c in comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()
        result.append({"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
                       "agreed_count": agreed_count, "disagreed_count": disagreed_count, "time": c.time,
                       "user_id": c.user.id,
                       "document_name": c.document.name, "document_id": c.document.id})
    return JsonResponse({"comments": result})


def get_pending_followers(request):
    username = request.COOKIES.get('username')
    followers = UserFollow.objects.filter(following__username=username, accepted=False)
    result = []
    for f in followers:
        result.append({'id': f.id, 'user_id': f.follower.id, 'first_name': f.follower.first_name,
                       'last_name': f.follower.last_name})
    return JsonResponse({'result': result})


def accept_follower(request, id):
    u = UserFollow.objects.get(id=id)
    u.accepted = True
    u.save()
    return JsonResponse({})


def reject_follower(request, id):
    u = UserFollow.objects.get(id=id)
    u.delete()
    return JsonResponse({})


def self(request):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    return JsonResponse({"name": user.first_name + ' ' + user.last_name + ' '})


def GetGraphSimilarityMeasureByCountry(request, country_id):
    graph_list = Graph_Cube.objects.filter(country_id_id=country_id).values('measure_id').distinct()
    result = []
    for row in graph_list:
        measure_id = row["measure_id"]
        measure_name = Measure.objects.get(id=measure_id).persian_name
        res = {"id": measure_id, "name": measure_name}
        result.append(res)
    return JsonResponse({'measure_list': result})



def GetGraphDistribution(request, country_id, measure_id):
    graph_cube = Graph_Distribution_Cube.objects.filter(country_id_id=country_id, measure_id_id=measure_id)
    result = []
    for row in graph_cube:
        res = {"similarity": row.threshold, "count": row.edge_count}
        result.append(res)

    return JsonResponse({'graph_distribution': result})


def GetSubjectsByCountryId(request, country_id):
    documents_subjects_list = Subject.objects.all().order_by("id")

    result = []
    for row in documents_subjects_list:
        subject_id = row.id
        subject_name = row.name
        res = {
            "id": subject_id,
            "subject": subject_name
        }
        result.append(res)
    return JsonResponse({'documents_subject_list': result})


def GetGraphNodesEdges(request, country_id, measure_id, minimum_weight):
    Graph_Cube_OBJ = Graph_Cube.objects.get(country_id_id=country_id, measure_id__id=measure_id,
                                            threshold=float(minimum_weight))

    Nodes_data = Graph_Cube_OBJ.nodes_data
    Edges_data = Graph_Cube_OBJ.edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetDocumentsByCountryId_Modal(request, country_id=None, start_index=None, end_index=None):
    data = list(CUBE_DocumentJsonList.objects.filter(country_id__id=country_id)
                .values_list('json_text', flat=True))
    doc_count = data.__len__()
    if end_index > 0:
        data = data[start_index: end_index]

    return JsonResponse({'documentsList': data, 'document_count': doc_count})



def GetPersianDefinitionByDocumentId(request,
                                     document_id):  #######################  بخش تعاریف و اصطلاحات - کلید واژه‌های نهایی
    document_definition = DocumentDefinition.objects.get(
        document_id_id=document_id)
    definition_text = document_definition.text
    definition_keywords = ""
    if definition_text != None:
        keyword_list = ExtractedKeywords.objects.filter(
            definition_id=document_definition)
        for keyword in keyword_list:
            definition_keywords += keyword.word + " - "
        definition_keywords = definition_keywords[:-3]
    else:
        definition_text = "بخش تعاریف و اصطلاحات برای این سند توسط سامانه پیدا نشد."

    if definition_keywords == "":
        definition_keywords = "هیچ کلمه کلیدی برای این سند توسط سامانه پیدا نشد."

    result = {"id": document_definition.id,
              "text": definition_text,
              "keywords": definition_keywords
              }
    return JsonResponse({'documents_definition': [result]})


def GetGeneralDefinition(request, document_id):  ######################  بخش تعاریف کلی
    general_definitions = DocumentGeneralDefinition.objects.filter(document_id=document_id)
    result = []
    for general_definition in general_definitions:
        word = general_definition.keyword
        definition = general_definition.text
        is_abbreviation = general_definition.is_abbreviation
        result.append({'word': word, 'definition': definition, 'is_abbreviation': is_abbreviation})

    return JsonResponse({'result': result})


def GetGeneralDefinition2(request, document_id):
    result = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)
    black_list = ["سوم", "از قبیل", "از جمله", "مرحله", "پیوست", "تبصره", "ماده", "اصل", "تاریخ", "عبارتند از", "بخش",
                  "فصل"]
    for paragraph in paragraphs:
        paragraph_text = paragraph.text
        paragraph_index = paragraph_text.index(paragraph_text)

        for i in range(paragraph_index, len(paragraph_text)):
            if paragraph_text[i] == ':' and i != (len(paragraph_text) - 1):
                word = paragraph_text[paragraph_index: i]
                for j in range(paragraph_index, len(word)):
                    if word[j] == '-' or word[j] == '–' or word[j] == 'ـ' or word[j] == '.':
                        word = word[j + 2:len(word)]
                        break

                if len(word) < 4 or len(word) > 50 or any(x in word for x in black_list):
                    continue
                definition = ''
                word_index = paragraph_text.find(':')
                for j in range(word_index, len(paragraph_text)):
                    definition = paragraph_text[word_index + 1: j + 1]

                result.append({'word': word, 'definition': definition})

    return JsonResponse({'result': result})


def GetTFIDFByDocumentId(request, document_id):
    documents_tfidf_list = DocumentTFIDF.objects.filter(
        document_id_id=document_id).order_by('-weight')[:50]
    result = []
    for row in documents_tfidf_list:
        res = {"id": row.id,
               "word": row.word,
               "count": row.count,
               "weight": row.weight,
               }
        result.append(res)
    return JsonResponse({'documents_tfidf_list': result})


def GetNGramByDocumentId(request, document_id, gram):
    document_ngram_list = DocumentNgram.objects.filter(
        document_id_id=document_id, gram=gram).order_by('-score', '-count')[:50]
    result = []
    for row in document_ngram_list:
        res = {"id": row.id,
               "text": row.text,
               "count": row.count,
               "score": row.score,
               }
        result.append(res)
    return JsonResponse({'document_ngram_list': result})



def GetReferencesByDocumentId(request, document_id, type):
    if type == 1:
        document_refrences_list = Graph.objects.filter(src_document_id_id=document_id, measure_id_id=2).order_by(
            '-weight')
        result = []
        for row in document_refrences_list:
            Type = "-"
            if row.dest_document_id.type_id:
                Type = row.dest_document_id.type_id.name
            res = {"id": row.id,
                   "doc_id": row.dest_document_id_id,
                   "doc_name": row.dest_document_id.name,
                   "weight": row.weight,
                   "doc_level": row.dest_document_id.level_name,
                   "doc_type_name": Type,
                   "doc_approval_date": row.dest_document_id.approval_date,
                   "doc_approval_reference_name": row.dest_document_id.approval_reference_name
                   }
            result.append(res)
    else:  # type == 2
        document_citation_list = Graph.objects.filter(dest_document_id_id=document_id, measure_id_id=2).order_by(
            '-weight')
        result = []
        for row in document_citation_list:
            Type = "-"
            # if row.dest_document_id.type_id:
            #     Type = row.dest_document_id.type_id.name
            if row.src_document_id.type_id:
                Type = row.src_document_id.type_id.name
            res = {"id": row.id,
                   "doc_id": row.src_document_id_id,
                   "doc_name": row.src_document_id.name,
                   "weight": row.weight,
                   # "doc_level": row.dest_document_id.level_name,
                   "doc_level": row.src_document_id.level_name,
                   "doc_type_name": Type,
                   # "doc_approval_date": row.dest_document_id.approval_date,
                   "doc_approval_date": row.src_document_id.approval_date,
                   # "doc_approval_reference_name": row.dest_document_id.approval_reference_name
                   "doc_approval_reference_name": row.src_document_id.approval_reference_name
                   }
            result.append(res)

    return JsonResponse({'document_references_list': result})



def GetSubjectByDocumentId(request, document_id, measure_id):
    result = []
    document_name = Document.objects.get(id=document_id).name

    document_subject_list = DocumentSubject.objects.filter(document_id_id=document_id,
                                                           measure_id_id=measure_id).order_by('-weight')
    for row in document_subject_list:
        subject_keywords = DocumentSubjectKeywords.objects.filter(document_id=row.document_id,
                                                                  subject_keyword_id__subject_id=row.subject_id).order_by(
            '-count')
        keywords_text = ""
        keywords_title = ""
        special_references = ""

        for key in subject_keywords:
            keyword = key.subject_keyword_id.word
            if key.place == "متن":
                if keyword not in keywords_text:
                    keywords_text += keyword + \
                                     " ( " + str(key.count) + " ) " + " - "
            elif key.place == "عنوان":
                if keyword not in keywords_title:
                    keywords_title += keyword + \
                                      " ( " + str(key.count) + " ) " + " - "
            elif keyword not in special_references:
                special_references += keyword + " - "

        weight = row.id
        if special_references == "":
            weight = min(weight, 1)
        else:
            weight = min(weight, 2)

        keywords_text = keywords_text[:-3]
        keywords_title = keywords_title[:-3]
        special_references = special_references[:-3]

        res = {"id": row.id,
               "subject": row.subject_id.name,
               "weight": row.weight,
               "keywords_text": keywords_text,
               "keywords_title": keywords_title,
               "special_references": special_references,
               }
        result.append(res)

    return JsonResponse({'document_subject_list': result, 'document_name': document_name})



def GetActorsPararaphsByDocumentId(request, document_id):
    document_motevali_ejra_paragraphs = {}
    document_salahiat_ekhtiar_paragraphs = {}
    document_hamkaran_paragraphs = {}

    role_info_list = [
        {'role_name': 'متولی اجرا',
         'result_dict': document_motevali_ejra_paragraphs
         },
        {'role_name': 'همکار',
         'result_dict': document_hamkaran_paragraphs
         },
        {'role_name': 'دارای صلاحیت اختیاری',
         'result_dict': document_salahiat_ekhtiar_paragraphs
         }
    ]

    for role_info in role_info_list:

        role_name = role_info['role_name']
        result_dict = role_info['result_dict']

        actor_paragraphs = DocumentActor.objects.filter(document_id__id=document_id,
                                                        actor_type_id__name=role_name)

        for para_info in actor_paragraphs:
            para_id = para_info.paragraph_id.id
            para_text = para_info.paragraph_id.text
            para_actor_name = para_info.actor_id.name
            para_actor_form = para_info.current_actor_form

            para_ref_to_general_def = para_info.ref_to_general_definition

            para_ref_to_general_def_text = ''
            if para_ref_to_general_def:
                para_ref_to_general_def_text = para_info.general_definition_id.text

            para_ref_to_paragraph = para_info.ref_to_paragraph
            para_ref_to_para_text = ''

            if para_ref_to_paragraph:
                para_ref_to_para_text = para_info.ref_paragraph_id.text

            is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

            ref_text = ''

            if para_ref_to_general_def:
                ref_text = para_ref_to_general_def_text
            elif para_ref_to_paragraph:
                ref_text = para_ref_to_para_text

            result_dict[para_id] = {
                'text': para_text,
                'actor_name': para_actor_name,
                'actor_form': para_actor_form,
                'actor_role': role_name,
                'ref_to_general_def': para_ref_to_general_def,
                'ref_general_text': para_ref_to_general_def_text,

                'ref_to_paragraph': para_ref_to_paragraph,
                'ref_para_text': para_ref_to_para_text,

                'is_ref_actor': is_ref_actor,
                'ref_text': ref_text

            }

    actors_paragraphs = {
        'document_motevali_ejra_paragraphs': document_motevali_ejra_paragraphs,
        'document_salahiat_ekhtiar_paragraphs': document_salahiat_ekhtiar_paragraphs,
        'document_hamkaran_paragraphs': document_hamkaran_paragraphs
    }
    return JsonResponse({"actors_paragraphs": actors_paragraphs})



def GetBM25Similarity(request, document_id):
    sim_docs = []
    # index_name = Document.objects.get(id = document_id).country_id.name.replace(' ','_')
    country_obj = Document.objects.get(id=document_id).country_id
    index_name = standardIndexName(country_obj, Document.__name__)

    sim_query = {
        "more_like_this": {
            "analyzer": "persian_custom_analyzer",
            "fields": ["attachment.content"],
            "like": [
                {
                    "_index": index_name,
                    "_id": "{}".format(document_id),

                }

            ],
            "min_term_freq": 50,
            "max_query_terms": 100000
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_date', 'approval_reference_name'],
                             request_timeout=40,
                             query=sim_query
                             )

    sim_docs = response['hits']['hits']

    return JsonResponse({'docs': sim_docs})


def GetSimilarParagraphs_ByParagraphID(request, paragraph_id):
    similar_paragraphs = []
    para_obj = DocumentParagraphs.objects.get(id=paragraph_id)
    document_id = para_obj.document_id.id
    country_obj = para_obj.document_id.country_id
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__)
    # index_name = "doticfull_documentparagraphs"

    sim_query = {
        "bool": {
            "must_not": [
                {
                    "term": {
                        "document_id": str(document_id)
                    }
                }
            ],
            "filter": [
                {
                    "more_like_this": {
                        "analyzer": "persian_custom_analyzer",
                        "fields": [
                            "attachment.content"
                        ],
                        "like": [
                            {
                                "_index": index_name,
                                "_id": str(paragraph_id)
                            }
                        ],
                        "min_term_freq": 2,
                        "max_query_terms": 400,
                        "min_word_length": 4,
                        "min_doc_freq": 2,
                        "minimum_should_match": "55%"
                    }
                }
            ]
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'attachment.content'],
                             request_timeout=40,
                             query=sim_query
                             )

    similar_paragraphs = response['hits']['hits']

    return JsonResponse({'similar_paragraphs': similar_paragraphs})


def GetDocActorParagraphs_Column_Modal(request, document_id, actor_name, role_name):
    actor_paragraphs = {}
    result_paragraphs = DocumentActor.objects.filter(
        document_id__id=document_id,
        actor_id__name=actor_name,
        actor_type_id__name=role_name
    )

    for para_info in result_paragraphs:
        para_id = para_info.paragraph_id.id
        para_text = para_info.paragraph_id.text
        para_actor_name = para_info.actor_id.name
        para_actor_form = para_info.current_actor_form

        para_ref_to_general_def = para_info.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = para_info.general_definition_id.text

        para_ref_to_paragraph = para_info.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = para_info.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        actor_paragraphs[para_id] = {
            'text': para_text,
            'actor_name': para_actor_name,
            'actor_form': para_actor_form,
            'actor_role': role_name,
            'ref_to_general_def': para_ref_to_general_def,
            'ref_general_text': para_ref_to_general_def_text,

            'ref_to_paragraph': para_ref_to_paragraph,
            'ref_para_text': para_ref_to_para_text,

            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text

        }

    return JsonResponse({"actor_paragraphs": actor_paragraphs})


def UpdateNgramScore(request, document_id, gram, gram_ids):
    DocumentNgram.objects.filter(
        document_id_id=document_id, gram=gram, score=1).update(score=0)

    if gram_ids != "-1":
        gram_ids = gram_ids.split("__")
        for gram_id in gram_ids:
            DocumentNgram.objects.filter(id=gram_id).update(score=1)

    return JsonResponse({"status": "OK"})


def InsertNgram(request, document_id, gram, texts):
    texts = texts.split("__")
    for txt in texts:
        ngram = DocumentNgram.objects.filter(
            document_id_id=document_id, text=txt, gram=gram)
        if ngram.count() > 0:
            count = ngram.update(score=2)
        else:
            DocumentNgram.objects.create(
                document_id_id=document_id, text=txt, gram=gram, score=2, count=0)

    return JsonResponse({"status": "OK"})


def DeleteNgram(request, gram_id):
    DocumentNgram.objects.filter(id=gram_id).update(score=-1)
    return JsonResponse({"status": "OK"})


def GetDocumentContent(request, document_id):
    document_paragraphs = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)

    for paragraph in paragraphs:
        document_name = paragraph.document_id.name
        paragraph_text = paragraph.text
        paragraph_id = paragraph.id
        paragraph_subject = ParagraphsSubject.objects.filter(paragraph=paragraph)
        if paragraph_subject.count() > 0:
            paragraph_subject = paragraph_subject[0].subject1_name
        else:
            paragraph_subject = ""
        document_paragraphs.append(
            {'paragraph_text': paragraph_text, 'paragraph_id': paragraph_id, 'document_name': document_name,
             'subject_name': paragraph_subject})

    return JsonResponse({'document_paragraphs': document_paragraphs})


def GetDocumentSubjectContent(request, document_id, version_id):
    document_paragraphs = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)

    for paragraph in paragraphs:
        document_name = paragraph.document_id.name
        paragraph_text = paragraph.text
        paragraph_subject = ParagraphsSubject.objects.filter(paragraph=paragraph, version_id=version_id)

        if paragraph_subject.count() > 0:
            subject1_name = paragraph_subject[0].subject1_name
            subject1_score = round(paragraph_subject[0].subject1_score, 3)
            subject1_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                            dict(paragraph_subject[0].subject1_keywords).items()])

            subject1_row = "<tr>" + "<td  class ='subject_table_cell'>1</td>" + \
                           "<td class ='subject_table_cell'>" + subject1_name + "</td>" + \
                           "<td class ='subject_table_cell'>" + str(subject1_score) + "</td>" + \
                           "<td class ='subject_table_cell'>" + subject1_keywords + "</td></tr>"

            subject2_row = ""
            if paragraph_subject[0].subject2_name is not None:
                subject2_name = paragraph_subject[0].subject2_name
                subject2_score = round(paragraph_subject[0].subject2_score, 3)
                subject2_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                                dict(paragraph_subject[0].subject2_keywords).items()])
                subject2_row = "<tr>" + "<td class ='subject_table_cell'>2</td>" + \
                               "<td class ='subject_table_cell'>" + subject2_name + "</td>" + \
                               "<td class ='subject_table_cell'>" + str(subject2_score) + "</td>" + \
                               "<td class ='subject_table_cell'>" + subject2_keywords + "</td></tr>"

            subject3_row = ""
            if paragraph_subject[0].subject3_name is not None:
                subject3_name = paragraph_subject[0].subject3_name
                subject3_score = round(paragraph_subject[0].subject3_score, 3)
                subject3_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                                dict(paragraph_subject[0].subject3_keywords).items()])
                subject3_row = "<tr>" + "<td class ='subject_table_cell'>3</td>" + \
                               "<td class ='subject_table_cell'>" + subject3_name + "</td>" + \
                               "<td class ='subject_table_cell'>" + str(subject3_score) + "</td>" + \
                               "<td class ='subject_table_cell'>" + subject3_keywords + "</td></tr>"

            subject_row = subject1_row + subject2_row + subject3_row
            subject_table = '<table class="table-striped" style="margin: auto;width: 100%;">' \
                            '<thead>' \
                            '<tr>' \
                            '<th class="col-1 subject_table_cell">ردیف</th>' \
                            '<th class="col-3 subject_table_cell">موضوع</th>' \
                            '<th class="col-2 subject_table_cell">امتیاز (نرمال)</th>' \
                            '<th class="col-6 subject_table_cell">کلیدواژه (امتیاز)</th>' \
                            '</tr>' \
                            '</thead>' \
                            '<tbody>' + subject_row + '</tbody>' \
                                                      '</table>'
        else:
            subject_table = ""
        document_paragraphs.append(
            {'paragraph_text': paragraph_text, 'document_name': document_name, 'subject_name': subject_table})

    return JsonResponse({'document_paragraphs': document_paragraphs})



def SearchDocument_ES2(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                       from_advisory_opinion_count,
                       from_interpretation_rules_count, revoked_type_id, place, text, search_type):
    organization_type_id = 0

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year, from_advisory_opinion_count,
              from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                      to_year,
                                      from_advisory_opinion_count, from_interpretation_rules_count,
                                      revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    # index_name = Country.objects.get(id = country_id).name
    # index_name = index_name.replace(' ','_')
    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date',
                                               'subject_name',
                                               "level_name", 'type_name', 'approval_year', 'communicated_date',
                                               'advisory_opinion_count', 'interpretation_rules_count'],
                             request_timeout=40,
                             query=res_query,
                             size=1300

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits})


def CreateDocumentComment(request, document, comment, username, comment_show_info, time):
    user = User.objects.filter(username=username).first()
    doc = Document.objects.filter(id=document).first()
    show_info = False
    if comment_show_info == 'true':
        show_info = True
    comment = DocumentComment2.objects.create(document=doc, comment=comment, user=user, show_info=show_info,
                                              time=str(jdatetime.strftime(jdatetime.now(), "%H:%M:%S %Y-%m-%d")))

    return JsonResponse({"comment_id": comment.id})


def CreateHashTagForDocumentComment(request, comment_id, hash_tag):
    # createdDocumentComment = DocumentComment2.objects.get(id=comment_id)
    try:
        ht = DocumentCommentHashTag.objects.get(hash_tag=hash_tag)

    except:
        ht = DocumentCommentHashTag.objects.create(hash_tag=hash_tag)

    # createdDocumentComment.hash_tags.add(ht)
    # createdDocumentComment.save()
    DocumentComment2.objects.filter(id=comment_id).update(hash_tags=ht)

    return JsonResponse({"hash_tags": ht.hash_tag})


def CreateDocumentNote(request, document, note, username, time, label):
    user = User.objects.filter(username=username).first()
    doc = Document.objects.filter(id=document).first()
    DocumentNote.objects.create(document=doc, note=note, user=user, time=time, docLabel=label)
    createdNote = DocumentNote.objects.last()
    # createdNote = DocumentNote.objects.create(document=doc, note=note, user=user,time =time , docLabel = label)

    return JsonResponse({"note_id": createdNote.id})


def CreateHashTagForNote(request, note_id, hash_tag):
    createdNote = DocumentNote.objects.filter(id=note_id).first()
    # createdNote = DocumentNote.objects.last()
    ht = NoteHashTag(hash_tag=hash_tag)
    ht.save()
    createdNote.hash_tags.add(ht)
    createdNote.save()

    return JsonResponse({"hash_tags": createdNote.hash_tags.last().hash_tag})
    # return JsonResponse({})


def GetDocumentComments(request, document, username):
    followings = UserFollow.objects.filter(follower__username=username)
    follows = {}
    for f in followings:
        if f.accepted:
            follows[f.following.id] = 1
        else:
            follows[f.following.id] = -1

    user_comments = DocumentComment2.objects.filter(document=document, user__username=username)
    other_user_comments = DocumentComment2.objects.filter(document=document, is_accept=1).exclude(
        user__username=username)
    result = []
    for c in other_user_comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()

        if c.show_info:
            # not followed
            followed = 0
            if c.user.id in follows:
                followed = follows[c.user.id]
            result.append(
                {"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
                 "agreed_count": agreed_count, "disagreed_count": disagreed_count, "time": c.time, "user_id": c.user.id,
                 "followed": followed})
        else:
            result.append(
                {"comment": c.comment, "id": c.id, "first_name": '*', "last_name": '*', "agreed_count": agreed_count,
                 "disagreed_count": disagreed_count, "time": c.time})

    for c in user_comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()
        result.append({"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
                       "agreed_count": agreed_count, "disagreed_count": disagreed_count, "time": c.time,
                       "user_id": c.user.id, "accepted": c.is_accept})
    return JsonResponse({"comments": result})


def GetDocumentNotes(request, document, username):
    notes = DocumentNote.objects.filter(document=document, user__username=username)
    result = []
    for n in notes:
        result.append({"note": n.note, "time": n.time, "label": n.docLabel, "starred": n.starred, "id": n.id,
                       "document_name": n.document.name})
    return JsonResponse({"notes": result})



def changeVoteState(request, username, document_comment, state):
    agreed = False
    if state == "agree":
        agreed = True
    # voted or not yet?
    try:
        vote = DocumentCommentVote.objects.get(user__username=username, document_comment=document_comment)
        vote.agreed = agreed
        vote.modified_at = datetime.datetime.utcnow()
        vote.save()
    except:
        user = User.objects.filter(username=username).first()
        document_comment = DocumentComment2.objects.filter(id=document_comment).first()
        DocumentCommentVote.objects.create(user=user,
                                           document_comment=document_comment,
                                           agreed=agreed)
    return JsonResponse({})



def GetFollowings(request, follower_username):
    followings = UserFollow.objects.filter(follower__username=follower_username, accepted=True)
    follows = {}
    for f in followings:
        follows[f.following.id] = {"first_name": f.following.first_name, "last_name": f.following.last_name,
                                   "id": f.following.id}
    return JsonResponse({"follows": list(follows.values())})



def GetGraphEdgesForDocument(request, measure_id, document_id):
    graph_edge_list = Graph.objects.filter(Q(src_document_id=document_id) | Q(dest_document_id=document_id),
                                           measure_id__id=measure_id)

    result = []
    for edge in graph_edge_list:

        src_id = edge.src_document_id_id
        src_name = edge.src_document_id.name
        src_color = "#0"
        if edge.src_document_id.type_id != None:
            src_color = edge.src_document_id.type_id.color

        dest_id = edge.dest_document_id_id
        dest_name = edge.dest_document_id.name
        dest_color = "#0"
        if edge.dest_document_id.type_id != None:
            dest_color = edge.dest_document_id.type_id.color

        weight = edge.weight

        res = {
            "src_id": src_id,
            "src_name": src_name,
            "src_color": src_color,
            "dest_id": dest_id,
            "dest_name": dest_name,
            "dest_color": dest_color,
            "weight": weight,
        }

        result.append(res)

    graph_type = Measure.objects.get(id=measure_id).type

    return JsonResponse({'graph_edge_list': result, "graph_type": graph_type})



def GetAllKnowledgeGraphList(request, username):
    KnowledgeGraphVersionList = KnowledgeGraphVersion.objects.filter(Q(username=username) | Q(username="default"))
    result = []
    for row in KnowledgeGraphVersionList:
        id = row.id
        name = row.name
        username = row.username
        result.append({"id": id, "name": name, "username": username})

    return JsonResponse({"knowledge_graph_list": result})


def GetKnowledgeGraphData(request, version_id):
    graph_data = KnowledgeGraphData.objects.get(version_id=version_id)

    Nodes_data, Edges_data = graph_data.nodes, graph_data.edges

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def SaveKnowledgeGraph(request, graph_name, username, graph_id):
    nodes_data = np.array(request.POST.get('nodes_data').split(",")).reshape(-1, 4)
    edges_data = np.array(request.POST.get('edges_data').split(",")).reshape(-1, 7)

    nodes_list = []
    for row in nodes_data:
        res = {"id": row[0], "name": row[1], "EN_name": row[2], "weight": row[3], "label": row[1]}
        nodes_list.append(res)

    edges_list = []
    for row in edges_data:
        res = {"source": row[0], "source_name": row[1], "source_En_name": row[2],
               "target": row[3], "target_name": row[4], "target_EN_name": row[5],
               "weight": row[6], "label": row[6]}
        edges_list.append(res)

    if graph_id == 0:
        version = KnowledgeGraphVersion.objects.create(name=graph_name, username=username)
        KnowledgeGraphData.objects.create(version=version, nodes=nodes_list, edges=edges_list)
        return JsonResponse({'version_id': version.id})
    else:
        version = KnowledgeGraphVersion.objects.get(id=graph_id)
        KnowledgeGraphVersion.objects.filter(id=graph_id).update(name=graph_name)
        KnowledgeGraphData.objects.filter(version=version).update(nodes=nodes_list, edges=edges_list)
        return JsonResponse({'version_id': 0})


def DeleteKnowledgeGraph(request, graph_id):
    KnowledgeGraphVersion.objects.filter(id=graph_id).delete()
    return JsonResponse({'responce': "OK"})


def BoostingSearchKnowledgeGraph_ES(request, country_id, field_name, field_value, language, search_type, curr_page,
                                    result_size):
    country_obj = Country.objects.get(id=country_id)
    keyword_score_dict = dict(request.POST)
    cluser_keyword_data = np.array(keyword_score_dict['cluser_keyword_data'][0].split(',')).reshape(-1, 3)

    if language == "IRI":

        cluser_keyword_data = cluser_keyword_data[:, [0, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = standardIndexName(country_obj, Document.__name__)
            result_field = ['document_id', 'name', 'attachment.content']

    if language == "UK":

        cluser_keyword_data = cluser_keyword_data[:, [1, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = "uk-full-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = "uk-full-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = "uk-full-fixed_document"
            result_field = ['document_id', 'name', 'attachment.content']

    if language == "US":

        cluser_keyword_data = cluser_keyword_data[:, [1, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = "us-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = "us-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = "us-fixed_document"
            result_field = ['document_id', 'name', 'attachment.content']

    res_query = {"bool": {
        "filter": [
            {
                "range": {
                    "attachment.content_length": {
                        "gte": 2
                    }
                }
            }
        ],
        "must": {
            "bool": {
                search_type: []
            }
        }
    }}

    if field_name != "0":
        res_query["bool"]["filter"].append({"term": {field_name: {"value": field_value}}})

    for row in cluser_keyword_data:
        keyword = row[0]
        score = row[1]

        word_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
                "boost": score
            }
        }
        res_query['bool']['must']['bool'][search_type].append(word_query)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },

        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=result_field,
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             aggregations=res_agg,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }
                             )

    result = response['hits']['hits']
    aggregations = response['aggregations']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name)['count']

    response_dict = {
        'total_hits': total_hits,
        'aggregations': aggregations,
        "curr_page": curr_page,
        "result": result
    }
    return JsonResponse(response_dict)



def GetChartSloganAnalysis(request, country_id, slogan_year):
    slogan_map = SloganAnalysis.objects.filter(country_id_id=country_id, sloganYear=slogan_year).order_by('docYear')
    res1 = []
    res2 = []
    for s in slogan_map:
        res1.append([s.docYear, s.number_per_doc])
        res2.append([s.docYear, s.number_per_len])
    # return JsonResponse({"slogan_analysis1": res1, "slogan_analysis2":res2})
    slogan_map_synonym = SloganAnalysisUsingSynonymousWords.objects.filter(country_id_id=country_id,
                                                                           sloganYear=slogan_year).order_by('docYear')
    res3 = []
    for s in slogan_map_synonym:
        res3.append([s.docYear, s.number_per_doc])
    return JsonResponse({"slogan_analysis1": res1, "slogan_analysis2": res2, "slogan_analysis3": res3})



def GetInfoChartSloganAnalysis(request, country_id, slogan_year):
    result_data = CUBE_SloganAnalysis_ChartData.objects.filter(country_id__id=country_id, sloganYear=slogan_year) \
        .values('subject_chart_data', 'level_chart_data', 'approval_reference_chart_data')

    if result_data.exists():
        for res in result_data:
            subject_chart_data = res['subject_chart_data']['data']
            approval_reference_chart_data = res['approval_reference_chart_data']['data']
            level_chart_data = res['level_chart_data']['data']
    else:
        subject_chart_data = []
        approval_reference_chart_data = []
        level_chart_data = []

    return JsonResponse({'subject_chart_data': subject_chart_data,
                         'approval_references_chart_data': approval_reference_chart_data,
                         'level_chart_data': level_chart_data,
                         })



def GetActorsByDocumentIdActorType(document_id, actor_type_name):
    actor_dict = {}

    document_actors = DocumentActor.objects.filter(document_id_id=document_id,
                                                   actor_type_id__name=actor_type_name).annotate(
        actor_name=F('actor_id__name')).values('actor_name')

    # fill actor dict
    for actor in document_actors:
        actor_name = actor['actor_name']

        if actor_name not in actor_dict:
            actor_dict[actor_name] = 1
        else:
            actor_dict[actor_name] += 1

    return actor_dict


def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)
    document_actors = {}

    motevalian_dict = GetActorsByDocumentIdActorType(id, 'متولی اجرا')
    hamkaran_dict = GetActorsByDocumentIdActorType(id, 'همکار')
    salahiat_dict = GetActorsByDocumentIdActorType(id, 'دارای صلاحیت اختیاری')

    document_actors['motevalian'] = motevalian_dict
    document_actors['hamkaran'] = hamkaran_dict
    document_actors['salahiat'] = salahiat_dict

    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_name

    approval_date = "نامشخص"
    approval_year = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date
        approval_year = approval_date[0:4]

    communicated_date = "نامشخص"
    if document.communicated_date != None:
        communicated_date = document.communicated_date

    type_name = "سایر"
    if document.type_id != None:
        type_name = document.type_name

    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_name

    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_name

    result = {"id": document.id,
              "name": document.name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "level_id": document.level_id_id,
              "level": level_name,
              "subject_id": document.subject_id_id,
              "subject": subject_name,
              "type_id": document.type_id_id,
              "type": type_name,
              "approval_reference_id": document.approval_reference_id_id,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "approval_year": approval_year,
              "communicated_date": communicated_date,
              "word_count": document.word_count,
              "distinct_word_count": document.distinct_word_count,
              "stopword_count": document.stopword_count,
              "actors": document_actors
              }
    return result


def GetDetailChartSloganAnalysis(request, country_id, slogan_year, chart_type, column_name):
    document_result = CUBE_SloganAnalysis_FullData.objects.filter(country_id__id=country_id, sloganYear=slogan_year)

    document_list = []

    if chart_type == 'subject_chart_data':
        document_result = document_result.filter(subject_name=column_name)

    if chart_type == 'level_chart_data':
        document_result = document_result.filter(level_name=column_name)

    if chart_type == 'approval_reference_chart_data':
        document_result = document_result.filter(approval_reference_name=column_name)

    if chart_type == 'chart_container':
        result = SloganAnalysis.objects.filter(country_id__id=country_id, sloganYear=slogan_year,
                                               docYear=column_name).values('doc_ids')
        for ids in result:
            document_result = ids['doc_ids'].strip('][').split(', ')

    for res in document_result:
        if chart_type == 'chart_container':
            doc = GetDocumentById_Local(res)
            print(doc)
            doc_info = {'document_id': res, 'document_name': doc['name'],
                        'subject_name': doc['subject'],
                        'level_name': doc['level'], 'approval_reference_name': doc['approval_reference'],
                        'approval_date': doc['approval_date']}
        else:
            doc_info = {'document_id': res.document_id.id, 'document_name': res.document_name,
                        'subject_name': res.subject_name,
                        'level_name': res.level_name, 'approval_reference_name': res.approval_reference_name,
                        'approval_date': res.approval_date}
        document_list.append(doc_info)

    return JsonResponse({'document_list': document_list})




def Get_Clustering_Vocabulary(request, country_id, vector_type, ngram_type):
    res_features = ParagraphsFeatures.objects.get(country__id=country_id,
                                                  feature_extractor=vector_type,
                                                  ngram_type=ngram_type).features

    table_data = []
    i = 0
    for feature in res_features:
        i += 1
        term = feature[0],
        IDF = feature[1]
        row = {'index': i, 'term': term, "IDF": IDF}
        table_data.append(row)

    return JsonResponse({
        'table_data': table_data
    })


def Get_ClusterCenters_ChartData(request, country_id, algorithm_name, vector_type, cluster_count, ngram_type):
    algorithm_id = ClusteringAlorithm.objects.get(
        name=algorithm_name,
        input_vector_type=vector_type,
        cluster_count=cluster_count,
        ngram_type=ngram_type
    ).id

    try:

        heatmap_chart_data = ClusteringResults.objects.get(
            country__id=country_id,
            algorithm__id=algorithm_id
        ).heatmap_chart_data["data"]

        cluster_size_chart_data = ClusteringResults.objects.get(
            country__id=country_id,
            algorithm__id=algorithm_id
        ).cluster_size_chart_data["data"]

    except:
        heatmap_chart_data = []
        cluster_size_chart_data = []

    return JsonResponse({
        'heatmap_chart_data': heatmap_chart_data,
        'cluster_size_chart_data': cluster_size_chart_data
    })


def Get_ClusteringAlgorithm_DiscriminatWords_ChartData(request, country_id, algorithm_name, vector_type, cluster_count,
                                                       ngram_type):
    algorithm_id = ClusteringAlorithm.objects.get(
        name=algorithm_name,
        input_vector_type=vector_type,
        cluster_count=cluster_count,
        ngram_type=ngram_type
    ).id

    try:

        anova_chart_data = FeatureSelectionResults.objects.get(
            country__id=country_id,
            c_algorithm__id=algorithm_id,
            f_algorithm__name="ANOVA"
        ).important_words_chart_data["data"]

        decision_tree_chart_data = FeatureSelectionResults.objects.get(
            country__id=country_id,
            c_algorithm__id=algorithm_id,
            f_algorithm__name="DecisionTree"
        ).important_words_chart_data["data"]

    except:

        anova_chart_data = []
        decision_tree_chart_data = []

    return JsonResponse({
        'anova_chart_data': anova_chart_data,
        'decision_tree_chart_data': decision_tree_chart_data
    })



def Get_ClusteringEvaluation_Silhouette_ChartData(request, country_id, algorithm_name, vector_type, ngram_type):
    eval_result = ClusteringEvaluationResults.objects.get(
        country__id=country_id,
        name=algorithm_name,
        input_vector_type=vector_type,
        ngram_type=ngram_type
    )

    silhouette_score_chart_data = eval_result.silhouette_score_chart_data
    elbow_inertia_chart_data = eval_result.elbow_inertia_chart_data

    return JsonResponse({
        'silhouette_score_chart_data': silhouette_score_chart_data,
        "elbow_inertia_chart_data": elbow_inertia_chart_data
    })



def Get_ANOVA_Word_Paragraphs_Column_ES(request, country_id, topic_id, word, curr_page, result_size):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            },
            {
                "bool": {
                    "should": [
                        {
                            "match_phrase": {
                                "attachment.content": {
                                    "query": word
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "preprocessed_text": {
                                    "query": word
                                }
                            }
                        }
                    ]
                }
            }
        ]
    }}

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name',
                                               'paragraph_id', 'attachment.content',
                                               'topic_id', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        "result": result
    }

    return JsonResponse(response_dict)


def Export_ANOVA_Word_Paragraphs_Column_ES(request, country_id, topic_id, word, username, curr_page, result_size):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            },
            {
                "match_phrase": {
                    "attachment.content": {
                        "query": word
                    }
                }
            }
        ]
    }}

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['document_name', 'paragraph_id',
                                               'attachment.content', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,

                             )

    result = response['hits']['hits']

    result_range = str(from_value) + " تا " + str(from_value + len(result))

    paragraph_list = [
        [doc['_source']['document_name']
            , doc['_source']['attachment']['content'],
         doc['_source']['score']] for doc in result]

    cluster_name = ClusterTopic.objects.get(id=topic_id).name.replace('C', 'شماره ')

    try:
        user_topic_label = UserTopicLabel.objects.get(
            topic__id=topic_id,
            user__username=username).label
    except:
        user_topic_label = 'بدون برچسب'

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام سند", "متن پاراگراف", "امتیاز"])

    file_name = country_obj.name + " - " + "واژه: " + word + " در " + "احکام خوشه " + cluster_name + \
                " - " + user_topic_label + " - " + result_range + ".xlsx"

    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})


def Get_Topic_Paragraphs_Column_ES(request, country_id, topic_id, field_name, field_value, curr_page, result_size):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            },
            {
                "term":
                    {
                        field_name: {
                            "value": field_value
                        }
                    }
            }
        ],

        "should": []
    }}
    word_score_dict = ClusterTopic.objects.get(id=topic_id).words

    for word, score in word_score_dict.items():
        word = word.strip()
        integer_score = int(float(score) * 10000)
        boost_score = integer_score if integer_score > 0 else 1

        word_query = {
            "match_phrase": {
                "attachment.content": {
                    "query": word,
                    "boost": boost_score
                }
            }
        }

        res_query['bool']['should'].append(word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name',
                                               'paragraph_id', 'paragraph_id',
                                               'topic_id', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        "result": result
    }

    return JsonResponse(response_dict)



def Get_Topic_Anova_ChartData(request, country_id, topic_id):
    discriminant_words_chart_data = TopicDiscriminantWords.objects.get(
        country__id=country_id,
        f_algorithm__name="ANOVA",
        topic__id=topic_id
    ).discriminant_words_chart_data["data"]

    return JsonResponse({
        "discriminant_words_chart_data": discriminant_words_chart_data
    })



def Get_Topic_TagCloud_ChartData(request, country_id, topic_id):
    tag_cloud_chart_data = []

    word_dict = ClusterTopic.objects.get(
        country__id=country_id,
        id=topic_id
    ).words

    for word, score in word_dict.items():
        tag_cloud_chart_data.append({"x": word, "value": score})

    return JsonResponse({
        "tag_cloud_chart_data": tag_cloud_chart_data
    })


def GetClusteringGraphData(request, country_id, algorithm_name, algorithm_vector_type, cluster_size, ngram_type):
    algorithm = ClusteringAlorithm.objects.get(name=algorithm_name, input_vector_type=algorithm_vector_type,
                                               cluster_count=cluster_size, ngram_type=ngram_type)

    try:

        ClusteringGraphData_Object = ClusteringGraphData.objects.get(country_id=country_id, algorithm=algorithm)
        Nodes_data, Edges_data = ClusteringGraphData_Object.centroids_nodes_data, ClusteringGraphData_Object.centroids_edges_data
    except:
        Nodes_data, Edges_data = [], []

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetClusterKeywordGraphData(request, country_id, algorithm_name, algorithm_vector_type, cluster_size, ngram_type):
    algorithm = ClusteringAlorithm.objects.get(name=algorithm_name, input_vector_type=algorithm_vector_type,
                                               cluster_count=cluster_size, ngram_type=ngram_type)

    try:
        ClusteringGraphData_Object = ClusteringGraphData.objects.get(country_id=country_id, algorithm=algorithm)
        Nodes_data, Edges_data = ClusteringGraphData_Object.subject_keywords_nodes_data, ClusteringGraphData_Object.subject_keywords_edges_data
    except:
        Nodes_data, Edges_data = [], []
    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetKeywordClustersData(request, country_id, algorithm_name, algorithm_vector_type, cluster_size, keyword):
    algorithm_id = ClusteringAlorithm.objects.get(
        name=algorithm_name,
        input_vector_type=algorithm_vector_type,
        cluster_count=cluster_size
    ).id

    algorithm_result_data = CUBE_Clustering_TableData.objects.get(country__id=country_id, algorithm__id=algorithm_id)
    table_data = algorithm_result_data.table_data['data']

    result_table_data = []
    for row in table_data:
        if keyword in row["word_list"].split(" - "):
            result_table_data.append(row)

    return JsonResponse({
        "table_data": result_table_data
    })



def GetSearchDetails_ES(request, document_id, search_type, text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)
    language = country.language

    local_index = standardIndexName(country, Document.__name__)

    if language == 'کتاب':
        local_index = book_index_name

    if language == 'استاندارد':
        local_index = standardIndexName(country, Standard.__name__)

    result_text = ''
    place = 'متن'

    res_query = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document_id
                }
            }
        }
    }

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, False)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, False)

    # local_index = "doticfull_document"
    response = client.search(index=local_index,
                             _source_includes=['document_id', 'name', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          #   "fragment_size":100000
                                          # "boundary_scanner" : "word"
                                          # "type":"plain"
                                          }
                                 }}

                             )

    if len(response['hits']['hits']) > 0:
        result_text = response['hits']['hits'][0]["highlight"]["attachment.content"][0]
    else:
        response = client.get(index=local_index, id=document_id,
                              _source_includes=['document_id', 'name', 'attachment.content']
                              )
        result_text = response['_source']['attachment']['content']

    return JsonResponse({
        "result": result_text})



def ingest_full_profile_analysis_to_elastic(request, id):
    file = get_object_or_404(Country, id=id)
    from es_scripts import IngestFullProfileAnalysisToElastic
    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestFullProfileAnalysisToElastic.apply(folder_name, file)
    return redirect('zip')


def GetParagraphBy_ID(request, paragraph_id):
    paragraph_text = DocumentParagraphs.objects.get(id=paragraph_id).text
    country_name = DocumentParagraphs.objects.get(id=paragraph_id).document_id.country_id.name
    return JsonResponse({"paragraph_text": str(paragraph_text), "country_name": country_name})


def GetParagraphSubjectContent(request, paragraph_id, version_id):
    para_obj = DocumentParagraphs.objects.get(id=paragraph_id)
    para_text = para_obj.text
    document_id = para_obj.document_id.id
    document_name = para_obj.document_id.name

    paragraph_subject = ParagraphsSubject.objects.filter(paragraph=para_obj, version_id=version_id)

    if paragraph_subject.count() > 0:
        subject1_name = paragraph_subject[0].subject1_name
        subject1_score = round(paragraph_subject[0].subject1_score, 3)
        subject1_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                        dict(paragraph_subject[0].subject1_keywords).items()])

        subject1_row = "<tr>" + "<td  class ='subject_table_cell'>1</td>" + \
                       "<td class ='subject_table_cell'>" + subject1_name + "</td>" + \
                       "<td class ='subject_table_cell'>" + str(subject1_score) + "</td>" + \
                       "<td class ='subject_table_cell'>" + subject1_keywords + "</td></tr>"

        subject2_row = ""
        if paragraph_subject[0].subject2_name is not None:
            subject2_name = paragraph_subject[0].subject2_name
            subject2_score = round(paragraph_subject[0].subject2_score, 3)
            subject2_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                            dict(paragraph_subject[0].subject2_keywords).items()])
            subject2_row = "<tr>" + "<td class ='subject_table_cell'>2</td>" + \
                           "<td class ='subject_table_cell'>" + subject2_name + "</td>" + \
                           "<td class ='subject_table_cell'>" + str(subject2_score) + "</td>" + \
                           "<td class ='subject_table_cell'>" + subject2_keywords + "</td></tr>"

        subject3_row = ""
        if paragraph_subject[0].subject3_name is not None:
            subject3_name = paragraph_subject[0].subject3_name
            subject3_score = round(paragraph_subject[0].subject3_score, 3)
            subject3_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                            dict(paragraph_subject[0].subject3_keywords).items()])
            subject3_row = "<tr>" + "<td class ='subject_table_cell'>3</td>" + \
                           "<td class ='subject_table_cell'>" + subject3_name + "</td>" + \
                           "<td class ='subject_table_cell'>" + str(subject3_score) + "</td>" + \
                           "<td class ='subject_table_cell'>" + subject3_keywords + "</td></tr>"

        subject_row = subject1_row + subject2_row + subject3_row
        subject_table = '<table dir="rtl" class="table-striped" style="margin: auto;width: 100%;">' \
                        '<thead>' \
                        '<tr>' \
                        '<th class="col-1 subject_table_cell">ردیف</th>' \
                        '<th class="col-3 subject_table_cell">موضوع</th>' \
                        '<th class="col-2 subject_table_cell">امتیاز (نرمال)</th>' \
                        '<th class="col-6 subject_table_cell">کلیدواژه (امتیاز)</th>' \
                        '</tr>' \
                        '</thead>' \
                        '<tbody>' + subject_row + '</tbody>' \
                                                  '</table>'
    else:
        subject_table = ""

    return JsonResponse(
        {'paragraph_text': para_text,
         'document_name': document_name,
         'document_id': document_id,
         'subject_name': subject_table}
    )
    
# --------------------------------

def GetSimiGraphEdgesByDocumentsList_Standard(request, measure_name):
    documents_id_list = [int(id) for id in request.POST.get('documents_id_list').split(',')]

    graph_edge_list = DocumentSimilarity.objects.filter(
        doc1__id__in=documents_id_list, doc2__id__in=documents_id_list,
        similarity_type__name=measure_name
    )

    Nodes_data = []
    Edges_data = []
    addedNode = []
    addedEdge = []
    for edge in graph_edge_list:

        src_id = str(edge.doc1.id)
        src_name = edge.doc1.name

        dest_id = str(edge.doc2.id)
        dest_name = edge.doc2.name

        weight = edge.similarity

        node1 = {"id": src_id, "name": src_name}
        if src_id not in addedNode:
            Nodes_data.append(node1)
            addedNode.append(src_id)

        node2 = {"id": dest_id, "name": dest_name}
        if dest_id not in addedNode:
            Nodes_data.append(node2)
            addedNode.append(dest_id)

        if [dest_id, src_id] not in addedEdge and [src_id, dest_id] not in addedEdge:
            edge_dict = {
                "source": src_id,
                "source_name": src_name,
                "target": dest_id,
                "target_name": dest_name,
                "weight": weight,
            }
            addedEdge.append([src_id, dest_id])

            Edges_data.append(edge_dict)

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


@allowed_users('standard_information')
def standard_information(request):
    country_list = Country.objects.all()
    country_map = get_standard_maps(country_list)
    return render(request, "doc/standard_information.html", {'countries': country_map})


@allowed_users('standard_search')
def standard_search(request):
    country_list = Country.objects.all()
    country_map = get_standard_maps(country_list)
    return render(request, "doc/standard_search.html", {'countries': country_map})


@allowed_users('standard_graph')
def standard_graph(request):
    country_list = Country.objects.all()
    country_map = get_standard_maps(country_list)
    return render(request, "doc/standard_graph.html", {'countries': country_map})


@allowed_users('standard_graph_v2')
def standard_graph_v2(request):
    country_list = Country.objects.all()
    country_map = get_standard_maps(country_list)
    return render(request, "doc/standard_graph_v2.html", {'countries': country_map})


def GetStandardDocumentById(request, document_id):
    document = Document.objects.get(id=document_id)
    sta = Standard.objects.get(document_id=document)

    subject = "نامشخص"
    if sta.subject != None:
        subject = sta.subject

    standard_number = "نامشخص"
    if sta.standard_number != None:
        standard_number = sta.standard_number

    branch = "نامشخص"
    if sta.branch != None:
        branch = sta.branch.name

    approval_year = "نامشخص"
    if sta.approval_year != None:
        approval_year = sta.approval_year

    ICS = "نامشخص"
    if sta.approval_year != None:
        ICS = sta.ICS

    file_name_with_extention = "نامشخص"
    if sta.file_name_with_extention != None:
        file_name_with_extention = sta.file_name_with_extention

    result = {"document_id": document.id,
              "subject": subject,
              "standard_number": standard_number,
              "branch": branch,
              "approval_year": approval_year,
              "ICS": ICS,
              "file_name_with_extention": file_name_with_extention
              }
    return JsonResponse({'standard_information': [result]})


def GetStandardsSearchParameters(request, country_id):
    search_parameters = StandardSearchParameters.objects.filter(country__id=country_id)
    parameters_result = {}

    for param in search_parameters:
        para_name = param.parameter_name
        options = param.parameter_values["options"]
        parameters_result[para_name] = options

    return JsonResponse({"parameters_result": parameters_result})


def filter_standard_fields(res_query, branch, subject_category, status, from_year, to_year):
    if branch != 0:
        branch_name = Standard_Branch.objects.get(id=branch).name
        branch_query = {
            "term": {
                "branch.keyword": branch_name
            }
        }
        res_query['bool']['filter'].append(branch_query)
    # ---------------------------------------------------------

    if subject_category != 0:
        branch_name = Standard_Branch.objects.get(id=subject_category).name

        subject_category = branch_name.replace('کمیته ملی', '').strip()

        subject_category_query = {
            "term": {
                "subject_category.keyword": subject_category
            }
        }
        res_query['bool']['filter'].append(subject_category_query)
    # ---------------------------------------------------------
    if status != 0:
        status_name = Standard_Status.objects.get(id=status).name
        status_query = {
            "term": {
                "status.keyword": status_name
            }
        }
        res_query['bool']['filter'].append(status_query)

    # ----------------------------------------------------------
    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "approval_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    return res_query


def SearchDocument_ES_Standard(request, country_id, branch, subject_category, status, from_year, to_year, place, text,
                               search_type):
    fields = [branch, subject_category, status, from_year, to_year]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_standard_fields(res_query, branch, subject_category, status, from_year, to_year)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Standard.__name__)

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'branch', 'subject_category',
                                               'status', 'standard_number', 'ICS', 'appeal_number', 'Description',
                                               'approval_year',
                                               'file_name_with_extention'],
                             request_timeout=40,
                             query=res_query,
                             size=100

                             )

    # print("Got %d Hits:" % response['hits']['total']['value'])
    total_hits = response['hits']['total']['value']

    return JsonResponse({
        "result": response['hits']['hits'],
        'total_hits': total_hits})

def GetStandardTypeByCountryId(request, country_id):
    type_list = StandardGraphType.objects.filter(country_id_id=country_id)
    result = []
    for t in type_list:
        res = {"id": t.id, "name": t.name, "color": t.color, "is_checked": t.is_checked}
        result.append(res)
    return JsonResponse({"type_list": result})

def GetStandardGraphNodesEdges(request, country_id, selected_type):
    selected_type = selected_type.split("_")
    nodes_list = StandardGraphNodesCube.objects.filter(country_id_id=country_id, type_id__in=selected_type)
    edges_list = StandardGraphEdgesCube.objects.filter(country_id_id=country_id, src_type_id__in=selected_type,
                                                       target_type__in=selected_type)

    nodes_result = []
    for n in nodes_list:
        nodes_result += list(n.nodes)

    edges_result = []
    for e in edges_list:
        edges_result += list(e.edges)

    return JsonResponse({"Nodes_data": nodes_result, "Edges_data": edges_result})



def remove_unknown_standard_doc(request, country_id):
    doc_count = Document.objects.filter(country_id__id=country_id, name__icontains="نامشخص").count()
    Document.objects.filter(country_id__id=country_id, name__icontains="نامشخص").delete()

    return JsonResponse({'count': doc_count})


def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return JsonResponse({"status": "ok"})


def GetBookSimilarityMeasureByCountry(request, country_id):
    graph_list = DocumentSimilarity_Distribution_Cube.objects.filter(country_id_id=country_id).values(
        'similarity_type').distinct()
    result = []
    for row in graph_list:
        measure_id = row["similarity_type"]
        measure_name = SimilarityType.objects.get(id=measure_id).name
        res = {"id": measure_id, "name": measure_name}
        result.append(res)
    return JsonResponse({'measure_list': result})

def GetBookGraphDistribution(request, country_id, measure_id):
    graph_cube = DocumentSimilarity_Distribution_Cube.objects.filter(country_id_id=country_id,
                                                                     similarity_type_id=measure_id)
    result = []
    for row in graph_cube:
        res = {"similarity": row.threshold, "count": row.edge_count}
        result.append(res)

    return JsonResponse({'graph_distribution': result})