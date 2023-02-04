from html import entities
import re
import operator
from functools import reduce

from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
import os
from django.forms import FileField
from doc.forms import ZipFileForm
from en_doc.models import *
from scripts import ZipFileExtractor, StratAutomating
from abdal import config, es_config
import shutil
import after_response
import json
from pathlib import Path
from django.http import JsonResponse
from scripts.English import Preprocessing
from django.db.models import Max, Min, Count, Sum, F, Q, IntegerField
from django.db.models.functions import Substr, Cast, Length
from urllib.parse import urlparse
from django.core.files.storage import FileSystemStorage
import docx2txt
from collections import Counter
from elasticsearch import Elasticsearch
from scripts.Persian.Preprocessing import standardIndexName

# elastic configs
es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)
book_index_name = es_config.Book_Index

def get_country_maps(country_objects):
    dataset_map = {}
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "انگلیسی":
            dataset_map[id] = name
    return dataset_map


def index(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/index.html', {'countries': country_map})


def information(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/information.html', {'countries': country_map})


def graph(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/graph.html', {'countries': country_map})


def comparison(request):
    return render(request, 'en_doc/comparison.html')


def search(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/search.html', {'countries': country_map})

def es_search(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/ES_Search.html', {'countries': country_map})

def subject(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/subject.html', {'countries': country_map})


def subject_statistics(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/subject_statistics.html', {'countries': country_map})


def votes_analysis(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/vote_analysis.html', {'countries': country_map})


def adaptation(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/adaptation.html', {'countries': country_map})


def subject_graph(request):
    return render(request, 'en_doc/subject_graph.html')


def en_upload(request):
    return render(request, 'en_doc/admin_upload.html')


def named_entities(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/named_entities.html', {'countries': country_map})


# ---------------- query ------------------------

def GetCountryById(request, id):
    country = Country.objects.get(id=id)
    result = {"id": country.id,
              "name": country.name,
              "folder": str(country.file.name.split("/")[-1].split(".")[0]),
              "language": country.language,
              }
    return JsonResponse({'country_information': [result]})


def GetDocumentById(request, id):
    document = Document.objects.get(id=id)

    approval_ref = "Unknown"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_id.name

    approval_date = "Unknown"
    if document.approval_date != None:
        approval_date = document.approval_date

    communicated_date = "Unknown"
    if document.communicated_date != None:
        communicated_date = document.communicated_date

    level_name = "Unknown"
    if document.level_id != None:
        level_name = document.level_id.name

    result = {"id": document.id,
              "name": document.name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "level": level_name,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "communicated_date": communicated_date,
              "word_count": document.word_count,
              "distinct_word_count": document.distinct_word_count,
              "stopword_count": document.stopword_count,
              }
    return JsonResponse({'document_information': [result]})


def GetDocumentsByCountryId_Modal(request, country_id=None, start_index=None, end_index=None):
    data = list(CUBE_DocumentJsonList.objects.filter(country_id__id=country_id)
                .values_list('json_text', flat=True))
    doc_count = data.__len__()
    data = sorted(data, key=lambda d: d['id'])
    if end_index > 0:
        data = data[start_index: end_index]

    return JsonResponse({'documentsList': data, 'document_count': doc_count})


def GetLevelByCountryId(request, country_id):
    documents_level_list = Document.objects.filter(country_id_id=country_id).values("level_id").order_by(
        "level_id").distinct()
    result = []
    for row in documents_level_list:
        level_id = row["level_id"]
        if level_id is not None:
            level = Level.objects.get(id=level_id)
            level_name = level.name
            res = {
                "id": level_id,
                "level": level_name
            }
            result.append(res)
    return JsonResponse({'documents_level_list': result})


def GetTypeByCountryId(request, country_id):
    documents_type_list = Document.objects.filter(country_id_id=country_id).values("type_id").order_by(
        "-type_id").distinct()
    result = []
    for row in documents_type_list:
        type_id = row["type_id"]
        if type_id is not None:
            type = Type.objects.get(id=type_id)
            type_name = type.name
            type_color = type.color
            res = {
                "id": type_id,
                "type": type_name,
                "color": type_color.replace("\n", "")
            }
            result.append(res)
    return JsonResponse({'documents_type_list': result})


def GetApprovalReferencesByCountryId(request, country_id):
    documents_approval_list = Document.objects.filter(country_id_id=country_id).values(
        "approval_reference_id").order_by("approval_reference_id__name").distinct()
    result = []
    for row in documents_approval_list:
        approval_reference_id = row["approval_reference_id"]
        if approval_reference_id is not None:
            approval_reference = ApprovalReference.objects.get(
                id=approval_reference_id)
            approval_reference_name = approval_reference.name
            res = {
                "id": approval_reference_id,
                "approval_reference": approval_reference_name
            }
            result.append(res)
    return JsonResponse({'documents_approval_list': result})


def GetYearsBoundByCountryId(request, country_id):
    documents_list = Document.objects.filter(
        country_id_id=country_id, approval_date__isnull=False)
    if documents_list.count() > 0:
        max_year = documents_list.aggregate(Max('approval_date'))[
                       "approval_date__max"][0:4]
        min_year = documents_list.aggregate(Min('approval_date'))[
                       "approval_date__min"][0:4]
        return JsonResponse({'documents_approval_list': [int(min_year) - 1, int(max_year) + 1]})
    else:
        return JsonResponse({'documents_approval_list': [-1, -1]})


def GetDocumentsWithoutSubject(request, country_id=None, measure_id=1):
    country_id = int(country_id)
    filesList = Document.objects.filter(
        country_id_id=country_id, subject_id__isnull=True).order_by('name')
    result = []
    for doc in filesList:
        document_information = GetDocumentById_Local(doc.id)
        res = {
            'id': doc.id,
            'document_name': doc.name,
            'document_approval_reference': document_information['approval_reference'],
            'document_approval_date': document_information['approval_date'],
            'document_level': document_information['level']
        }
        result.append(res)

    return JsonResponse({'documentsWithoutSubject': result})


def GetSubjectKeywords(request, subject_id):
    subject_keywords_list = SubjectKeyWords.objects.filter(
        subject_id=subject_id).values('word')
    result = []
    for keyword in subject_keywords_list:
        result.append(keyword['word'])

    result = ' - '.join(result)

    return JsonResponse({'subject_keywords_list': result})


def GetTFIDFByDocumentId(request, document_id):
    documents_tfidf_list = DocumentTFIDF.objects.filter(document_id_id=document_id).order_by('-weight')
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
    document_ngram_list = DocumentNgram.objects.filter(document_id_id=document_id, gram=gram).order_by('-score',
                                                                                                       '-count')
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
            res = {"id": row.id,
                   "doc_id": row.dest_document_id_id,
                   "doc_name": row.dest_document_id.name,
                   "weight": row.weight
                   }
            result.append(res)
    else:
        document_citation_list = Graph.objects.filter(dest_document_id_id=document_id, measure_id_id=2).order_by(
            '-weight')
        result = []
        for row in document_citation_list:
            res = {"id": row.id,
                   "doc_id": row.src_document_id_id,
                   "doc_name": row.src_document_id.name,
                   "weight": row.weight
                   }
            result.append(res)

    return JsonResponse({'document_references_list': result})


def GetSubjectByDocumentId(request, document_id, measure_id):
    result = []
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
            if key.place == "Text":
                if keyword not in keywords_text:
                    keywords_text += keyword + " ( " + str(key.count) + " ) " + " - "
            elif key.place == "Title":
                if keyword not in keywords_title:
                    keywords_title += keyword + " ( " + str(key.count) + " ) " + " - "
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
               "subject_id": row.subject_id.id,
               "weight": row.weight,
               "keywords_text": keywords_text,
               "keywords_title": keywords_title,
               "special_references": special_references,
               }
        result.append(res)

    return JsonResponse({'document_subject_list': result})


def GetDocumentsByCountrySubject(request, country_id=None, subjects_id=None):
    subjects_id = subjects_id.split("__")
    all_subject_flag = False

    if '0' in subjects_id:
        all_subject_flag = True
        subjects_id = []
        all_subjects = DocumentSubject.objects.filter(document_id__country_id=country_id).values(
            'subject_id__id').distinct()
        for subject in all_subjects:
            subjects_id.append(subject['subject_id__id'])

    documents_list = Document.objects.filter(
        country_id_id=country_id, subject_id_id__in=subjects_id)

    result = []
    for doc in documents_list:

        doc_subject = DocumentSubject.objects.filter(
            document_id=doc).order_by("-weight")
        status = True

        if not all_subject_flag:
            for i in range(subjects_id.__len__()):
                subjectid = str(doc_subject[i].subject_id_id)
                if subjectid not in subjects_id or doc_subject[i].weight == 0:
                    status = False

        if status == True:
            subject_keywords = DocumentSubjectKeywords.objects.filter(
                document_id=doc, subject_keyword_id__subject_id_id__in=subjects_id) \
                .order_by('subject_keyword_id__subject_id_id', '-count')

            weight = DocumentSubject.objects.filter(
                document_id=doc, subject_id_id__in=subjects_id).values("document_id_id").annotate(sum=Sum('weight'))[0][
                "sum"]

            keywords_text = ""
            keywords_title = ""
            special_references = ""

            for key in subject_keywords:
                keyword = key.subject_keyword_id.word
                if key.place == "Text":
                    if keyword not in keywords_text:
                        keywords_text += keyword + " - "
                elif key.place == "Title":
                    if keyword not in keywords_title:
                        keywords_title += keyword + " - "
                elif keyword not in special_references:
                    special_references += keyword + " - "

            weight = round(weight, 2)
            if special_references == "":
                weight = min(weight, 1)
            else:
                weight = min(weight, 2)

            keywords_text = keywords_text[:-3]
            keywords_title = keywords_title[:-3]
            special_references = special_references[:-3]

            res = {
                "document_id": doc.id,
                "document_name": doc.name,
                # "document_level": doc_level,
                # "approval_reference": approval_references,
                # "approval_date": approval_date,
                "subject": doc.subject_id.name,
                "weight": weight,
                "keywords_text": keywords_text,
                "keywords_title": keywords_title,
                "special_references": special_references,
            }
            result.append(res)

    result.sort(key=lambda x: x['weight'], reverse=True)

    return JsonResponse({'documentsList': result})


def get_subject_detail(request, document_id, subject_id):
    paragraphs = []
    keyword_list = SubjectKeyWords.objects.filter(subject_id_id=subject_id)
    for key in keyword_list:
        keyword = key.word

        # keyword in Title
        docs_list = Document.objects.filter(Q(id=document_id) & (
                Q(name__icontains=" " + keyword + " ") | Q(name__istartswith=keyword) | Q(name__iendswith=keyword)))
        if docs_list.count() > 0:
            paragraphs.insert(0, docs_list[0].name)

        # Keyword in Text
        docs_list = DocumentParagraphs.objects.filter(Q(document_id_id=document_id) & (
                Q(text__icontains=" " + keyword + " ") | Q(text__istartswith=keyword) | Q(text__iendswith=keyword)))
        paragraphs += [x.text for x in docs_list]

    return JsonResponse({
        "paragraphs": paragraphs, 'keywords': [x.word for x in keyword_list]})


def GetReferences2Doc(request, document1_id, document2_id):
    references_from_doc2 = ReferencesParagraphs.objects.filter(document_id_id=document1_id,
                                                               paragraph_id__document_id=document2_id).order_by(
        "paragraph_id__number")
    references_from_doc1 = ReferencesParagraphs.objects.filter(document_id_id=document2_id,
                                                               paragraph_id__document_id=document1_id).order_by(
        "paragraph_id__number")

    result1 = []
    for reference in references_from_doc1:
        result1.append(reference.paragraph_id.text)

    result2 = []
    for reference in references_from_doc2:
        result2.append(reference.paragraph_id.text)

    return JsonResponse({'references_from_doc1': result1, 'references_from_doc2': result2})


def UpdateNgramScore(request, document_id, gram, gram_ids):
    DocumentNgram.objects.filter(document_id_id=document_id, gram=gram, score=1).update(score=0)

    if gram_ids != "-1":
        gram_ids = gram_ids.split("__")
        for gram_id in gram_ids:
            DocumentNgram.objects.filter(id=gram_id).update(score=1)

    return JsonResponse({"status": "OK"})


def InsertNgram(request, document_id, gram, texts):
    texts = texts.split("__")
    for txt in texts:
        ngram = DocumentNgram.objects.filter(document_id_id=document_id, text=txt, gram=gram)
        if ngram.count() > 0:
            count = ngram.update(score=2)
        else:
            DocumentNgram.objects.create(document_id_id=document_id, text=txt, gram=gram, score=2, count=0)

    return JsonResponse({"status": "OK"})


def DeleteNgram(request, gram_id):
    DocumentNgram.objects.filter(id=gram_id).update(score=-1)
    return JsonResponse({"status": "OK"})


def GetGraphSimilarityMeasureByCountry(request, country_id):
    graph_list = Graph.objects.filter(src_document_id__country_id_id=country_id).values('measure_id').distinct()
    result = []
    for row in graph_list:
        measure_id = row["measure_id"]
        measure_name = Measure.objects.get(id=measure_id).english_name
        res = {"id": measure_id,
               "name": measure_name
               }
        result.append(res)
    return JsonResponse({'measure_list': result})


def GetGraphDistribution(request, country_id, measure_id):
    graph_weights = Graph.objects.filter(src_document_id__country_id_id=country_id, measure_id_id=measure_id)
    max_weight = graph_weights.aggregate(Max('weight'))["weight__max"]
    slice_count = 10
    step = round(max_weight / slice_count, 1)
    result = []
    minsimilarity = 0
    for i in range(0, slice_count):
        edge_count = Graph.objects.filter(src_document_id__country_id_id=country_id, measure_id_id=measure_id,
                                          weight__gte=minsimilarity).count()
        res = {"similarity": minsimilarity,
               "count": edge_count,
               }
        result.append(res)
        minsimilarity = round(minsimilarity + step, 1)

    return JsonResponse({'graph_distribution': result})


def GetDocumentByCountryTypeSubject_Modal(request, country_id, type_id, subject_id, tag):
    documents_list = Document.objects.filter(country_id_id=country_id)

    # type id Handle
    if type_id == -1:
        documents_list = documents_list.filter(type_id=None)
    elif type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    # type id Handle
    if subject_id == -1:
        documents_list = documents_list.filter(subject_id=None)
    elif subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    filesList = documents_list.order_by('name')
    result_list = []
    i = 1
    for doc in filesList:
        id = doc.id
        name = doc.name
        function = "SelectDocFunction('" + str(id) + "','" + tag + "')"
        button_tag = '<button ' \
                     'type="button" ' \
                     'class="btn modal_btn" ' \
                     'data-bs-toggle="modal" ' \
                     'onclick="' + function + '"' \
                                              '/>' + 'انتخاب' + '</button>'
        result_list.append({"id": i, "document_name": name, "tag": button_tag, "document_id": id})
        i += 1

    return JsonResponse({'documents_type_subject_list': result_list})


def GetDocumentByCountryTypeSubject(request, country_id, type_id, subject_id):
    documents_list = Document.objects.filter(country_id_id=country_id)
    # type id Handle
    if type_id == -1:
        documents_list = documents_list.filter(type_id=None)
    elif type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)
    # type id Handle
    if subject_id == -1:
        documents_list = documents_list.filter(subject_id=None)
    elif subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)
    filesList = documents_list.order_by('name')
    result_list = []
    for doc in filesList:
        id = doc.id
        result_list.append(id)

    return result_list


def GetGraphEdgesByDocumentIdMeasure(request, country_id, src_type_id, src_subject_id
                                    , dest_type_id, dest_subject_id, measure_id, weight):
    # Filter Documents Source
    src_document_list = GetDocumentByCountryTypeSubject(request, country_id, src_type_id, src_subject_id)

    # Filter Documents Destination
    dest_document_list = GetDocumentByCountryTypeSubject(request, country_id, dest_type_id, dest_subject_id)

    # Select Graph by Measure and weight
    graph_edge_list = Graph.objects.filter(src_document_id__in=src_document_list,
                                           dest_document_id__in=dest_document_list,
                                           measure_id__id=measure_id, weight__gte=float(weight))

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


def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)

    approval_ref = "Unknown"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_id.name

    approval_date = "Unknown"
    if document.approval_date != None:
        approval_date = document.approval_date

    communicated_date = "Unknown"
    if document.communicated_date != None:
        communicated_date = document.communicated_date

    level_name = "Unknown"
    if document.level_id != None:
        level_name = document.level_id.name

    result = {"id": document.id,
              "name": document.name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "level_id": document.level_id_id,
              "level": level_name,
              "approval_reference_id": document.approval_reference_id_id,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "communicated_date": communicated_date
              }
    return result


def SearchDocumentAnd(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                      place, text):
    # Filter Documents
    documents_list = Document.objects.filter(country_id_id=country_id)

    if level_id > 0:
        documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    documents_list = documents_list.annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))
    if from_year > 0:
        documents_list = documents_list.filter(approval_year__gte=from_year)

    if to_year > 0:
        documents_list = documents_list.filter(approval_year__lte=to_year)

    # preprocess and split search text
    words = Preprocessing.Preprocessing(text, removeSW=False)

    # Search
    if place in ("عنوان", "متن"):
        for word in words:
            documents_list = DocumentWords.objects.filter(
                document_id__in=documents_list, place=place, word=word).values("document_id").distinct()

    elif place == "تعاریف":
        words = text.split(" ")
        documents_list = DocumentDefinition.objects.filter(
            reduce(operator.and_, (Q(text__icontains=word) for word in words)),
            document_id__country_id_id=country_id).values(
            "document_id", "text").annotate(
            count=Count('text'), sum_count=Count('text')).order_by("-count")
        # unique documents
        result = {}
        for doc in documents_list:
            if not (doc["document_id"] in result):
                result[doc["document_id"]] = doc
        documents_list = result.values()

        list_id = []
        count_id = []
        for id in documents_list:
            list_id.append(id['document_id'])
            count_id.append(id['sum_count'])

    else:
        for word in words:
            documents_list = DocumentWords.objects.filter(
                document_id__in=documents_list, word=word).values("document_id").distinct()

    # ---------- Generate Data -------------
    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    documents_information_result = []

    for doc in documents_list:
        document_id = doc["document_id"]
        if place in ("عنوان", "متن"):
            word_count = DocumentWords.objects.filter(
                document_id=document_id, place=place, word__in=words)
        else:
            word_count = DocumentWords.objects.filter(
                document_id=document_id, word__in=words)

        word_count = word_count.values("document_id").annotate(
            sum_count=Min('count'))[0]["sum_count"]

        document_information = GetDocumentById_Local(document_id)
        document_information["count"] = word_count
        documents_information_result.append(document_information)

        # Generate chart Data
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]

        doc_approval_year = document_information["approval_date"]
        if doc_approval_year != "unknown":
            doc_approval_year = document_information["approval_date"][0:4]

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    documents_information_result = sorted(
        documents_information_result, key=lambda i: i['count'], reverse=True)
    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         })


def SearchDocumentOR(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                     place, text):
    # Filter Documents

    documents_list = Document.objects.filter(country_id_id=country_id, )

    if level_id > 0:
        documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    documents_list = documents_list.annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))
    if from_year > 0:
        documents_list = documents_list.filter(approval_year__gte=from_year)

    if to_year > 0:
        documents_list = documents_list.filter(approval_year__lte=to_year)

    # preprocess and split search text
    words = Preprocessing.Preprocessing(text, removeSW=False)
    # Search
    if place in ("عنوان", "متن"):
        documents_list = DocumentWords.objects.filter(
            document_id__in=documents_list, place=place, word__in=words)
        documents_list = documents_list.values("document_id").annotate(
            sum_count=Max('count')).order_by("-sum_count")

    elif place == "تعاریف":
        words = text.split(" ")
        documents_list = DocumentDefinition.objects.filter(
            reduce(operator.or_, (Q(text__icontains=word) for word in words)),
            document_id__in=documents_list).values(
            "document_id", "text").annotate(
            count=Count('text'), sum_count=Count('text')).order_by("-count")
        # show unique documents in result
        result = {}
        for doc in documents_list:
            if not (doc["document_id"] in result):
                result[doc["document_id"]] = doc
        documents_list = result.values()

    else:
        documents_list = DocumentWords.objects.filter(
            document_id__in=documents_list, word__in=words)

        documents_list = documents_list.values("document_id").annotate(
            sum_count=Max('count')).order_by("-sum_count")

    # ---------- Generate Data -------------

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    documents_information_result = []
    for doc in documents_list:

        # Generate Document List Table Data
        document_id = doc["document_id"]
        word_count = doc["sum_count"]
        document_information = GetDocumentById_Local(document_id)
        document_information["count"] = word_count
        documents_information_result.append(document_information)

        # Generate chart Data
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]

        doc_approval_year = document_information["approval_date"]
        if doc_approval_year != "unknown":
            doc_approval_year = document_information["approval_date"][0:4]

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         })


def GetDefinitionByDocumentId(request, document_id):
    regexes = [
        r'[“"].*?[”"] means [\s\S]*?[\.;]',
        r'[“"].*?[”"] \(.*?\) means [\s\S]*?[\.;]',
        r'[“"].*?[”"] has the meaning [\s\S]*?[\.;]',
        r'[“"].*?[”"] \(.*?\) has the meaning [\s\S]*?[\.;]',
    ]
    document_definition = DocumentDefinition.objects.filter(document_id_id=document_id)

    if document_definition.count() > 0:
        document_definition = document_definition[0]
        definition_text = document_definition.text
        definition_keywords = ""
        keywords = []
        definitions = []
        if definition_text != "":
            keyword_list = ExtractedKeywords.objects.filter(definition_id=document_definition)
            for keyword in keyword_list:
                definition_keywords += keyword.word + " - "
            definition_keywords = definition_keywords[:-3]

            for regex in regexes:
                pair = re.compile(regex)
                search__ = pair.findall(definition_text)
                for search_ in search__:
                    if "means" in search_:
                        temp = search_.split("means")
                        definition_ = temp[1]
                        keyword = temp[0]
                    else:
                        temp = search_.split("has the meaning")
                        definition_ = temp[1]
                        keyword = temp[0]
                    if definition_.startswith("-"):
                        definition_ = definition_[1:]
                    if definition_.startswith("—"):
                        definition_ = definition_.replace("—", "", 1)
                    if keyword != "" and len(keyword) < 1000:
                        keywords.append(keyword.replace("“", " ").replace("”", " ").replace('"', " ").strip())
                        definitions.append(definition_)
        else:
            definition_text = "Couldn't find any Definition in this Document."

        if definition_keywords == "":
            definition_keywords = "There is no keyword in this Document."

        result = {"id": document_definition.id,
                  "text": definition_text,
                  "keywords": definition_keywords
                  }

        return JsonResponse({'documents_definition': [result], 'keywords': keywords, 'definitions': definitions})

    else:
        result = {"id": 0, "text": "", "keywords": ""}
        return JsonResponse({'documents_definition': [result], 'keywords': [], 'definitions': []})


def GetAbbreviationsByDocumentId(request, document_id):
    document_paragraphs = DocumentParagraphs.objects.filter(document_id_id=document_id)
    document_abbreviations = {}
    for paragraph in document_paragraphs:
        temp = paragraph.text
        temp = re.sub('[^a-zA-Z]', ' ', temp)
        temp = temp.split(' ')
        for word in temp:
            count_uppers = sum(1 for c in word if c.isupper())
            if count_uppers > 1:
                if word in document_abbreviations.keys():
                    document_abbreviations[word]['frequency'] += 1
                    document_abbreviations[word]['abbreviation_paragraphs'].append(paragraph.text)
                else:
                    document_abbreviations[word] = {'frequency': 1,
                                                    'abbreviation_paragraphs': [paragraph.text]}
    return JsonResponse({'document_abbreviations': document_abbreviations})


def GetSearchCountExact(document_id, _text, place):
    count = 0
    print(document_id,_text,place)
    if 'عنوان' in place:
        document_name = Document.objects.get(id=document_id).name
        count += document_name.count(_text)

    if 'متن' in place:
        document_paragraphs = DocumentParagraphs.objects.filter(
            document_id_id=document_id, text__icontains=_text)

        for paragraph in document_paragraphs:
            paragraph_text = paragraph.text
            count += paragraph_text.count(_text)

    if 'تعاریف' in place:
        count += DocumentDefinition.objects.filter(document_id__id=document_id,
                                                   text__icontains=_text).count()

    return count



def SearchDocumentExact(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                        place, text):
    # Filter Documents
    documents_list = Document.objects.filter(country_id_id=country_id, )

    if level_id > 0:
        documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    if from_year > 0:
        documents_list = documents_list

    if to_year > 0:
        documents_list = documents_list

    # preprocess and split search text
    text = text.replace("  ", " ")

    if place == "عنوان":
        documents_list = documents_list.filter(name__icontains=text).annotate(
            document_id=F('id')).values("document_id")

    elif place == "متن":
        documents_list = DocumentParagraphs.objects.filter(
            document_id__in=documents_list, text__icontains=text).values("document_id")

    elif place == "تعاریف":
        documents_list = DocumentDefinition.objects.filter(
            (Q(text__startswith=text + " ") | Q(text__icontains=" " + text + " ") | Q(
                text__endswith=" " + text)) & Q(document_id__in=documents_list)).values("document_id")


    else:
        documents_list_title = documents_list.filter(name__icontains=text).annotate(
            document_id=F('id')).values("document_id")
        documents_list_text = DocumentParagraphs.objects.filter(
            document_id__in=documents_list, text__icontains=text).values("document_id")
        documents_list = documents_list_title.union(documents_list_text)

    documents_list = documents_list.distinct()
    # ---------- Generate Data -------------

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    documents_information_result = []
    for doc in documents_list:

        # Generate Document List Table Data
        document_id = doc["document_id"]
        word_count = str(GetSearchCountExact(document_id, text, place))
        document_information = GetDocumentById_Local(document_id)
        document_information["count"] = word_count
        document_information["searched_word"] = text
        document_information["keywords_count"] = 1
        documents_information_result.append(document_information)

        # Generate chart Data
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]
        doc_approval_year = document_information["approval_date"]

        if doc_approval_year != "unknown":
            doc_approval_year = document_information["approval_date"][0:4]

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         })


def SearchDocumentWithoutText(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year,
                              to_year):
    # Filter Documents
    documents_list = Document.objects.filter(country_id_id=country_id, )

    if level_id > 0:
        documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    documents_list = documents_list.annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))
    if from_year > 0:
        documents_list = documents_list.filter(approval_year__gte=from_year)

    if to_year > 0:
        documents_list = documents_list.filter(approval_year__lte=to_year)

    # ---------- Generate Data -------------

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    documents_information_result = []
    for doc in documents_list:

        # Generate Document List Table Data
        document_id = doc.id
        word_count = "-"
        document_information = GetDocumentById_Local(document_id)
        document_information["count"] = word_count
        documents_information_result.append(document_information)

        # Generate chart Data
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]
        doc_approval_year = document_information["approval_date"]

        if doc_approval_year != "unknown":
            doc_approval_year = document_information["approval_date"][0:4]

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         })


def GetSearchDetailsAndOR(request, document_id, text, where, mode):
    words = text.split(" ")
    if where == 'تعاریف':
        if mode == 'OR':
            document_definitions = DocumentGeneralDefinition.objects.filter(
                reduce(operator.or_, (Q(text__icontains=word) for word in words)), document_id=document_id)
            document_name = document_definitions[0].document_id.name
        else:
            document_definitions = DocumentDefinition.objects.filter(
                reduce(operator.and_, (Q(text__icontains=word) for word in words)), document_id=document_id)
            print(document_definitions)
            document_name = document_definitions[0].document_id.name

        paragraph_result = [d.text for d in document_definitions]

    else:
        document_paragraphs = DocumentParagraphs.objects.filter(
            document_id_id=document_id).order_by("number")
        document_name = document_paragraphs[0].document_id.name
        paragraph_result = []

        for paragraph in document_paragraphs:
            paragraph_text = paragraph.text
            for word in words:
                if paragraph_text.__contains__(word):
                    paragraph_result.append(paragraph_text)
                    break

    document_paragraph_result = list(set(paragraph_result))
    return JsonResponse({'document_paragraphs_result': document_paragraph_result, "document_name": [document_name],
                         "preprocess_text": [text]})


def GetSearchDetailsExact(request, document_id, text, where):
    if where == 'تعاریف':
        document_definitions = DocumentDefinition.objects.filter(text__icontains=text,
                                                                 document_id=document_id)
        document_name = document_definitions[0].document_id.name
        paragraph_result = [d.text for d in document_definitions]
    else:
        document_paragraphs = DocumentParagraphs.objects.filter(
            document_id_id=document_id, text__icontains=text).order_by("number")
        document_name = document_paragraphs[0].document_id.name
        paragraph_result = []
        for paragraph in document_paragraphs:
            paragraph_text = paragraph.text
            paragraph_result.append(paragraph_text)

    document_paragraph_result = list(set(paragraph_result))

    return JsonResponse({'document_paragraphs_result': document_paragraph_result, "document_name": [document_name],
                         "preprocess_text": [text]})


def GetGraphEdgesByDocumentsList(request, measure_id):
    documents_id_list = [int(id) for id in request.POST.get('documents_id_list').split(',')]
    # Select Graph by Measure and weight
    graph_edge_list = Graph.objects.filter(src_document_id__in=documents_id_list,
                                           dest_document_id__in=documents_id_list,
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


def GetDocumentEntities(request, document_id):
    named_entities_objects = AINamedEntities.objects.filter(paragraph_id__document_id__id=document_id)
    document_name = Document.objects.get(id=document_id).name
    documents_paragraphs_info = {}
    for object in named_entities_objects:
        paragraph_id = object.paragraph_id.id
        paragraph_text = object.paragraph_id.text
        paragraph_entities = object.entities
        paragraph_info = {"text": paragraph_text, "entities": paragraph_entities}
        documents_paragraphs_info[paragraph_id] = paragraph_info

    return JsonResponse({'document_paragraphs_info': documents_paragraphs_info, "document_name": document_name})


def GetDocumentsWithEntitiesByCountry(request, country_id):
    documents_id = AINamedEntities.objects.filter(
        document_id__country_id__id=country_id).exclude(entities=None).values("document_id__id")

    documents_list = Document.objects.filter(
        id__in=documents_id)

    result = []
    for doc in documents_list:
        res = {
            "document_id": doc.id,
            "document_name": doc.name,
            "document_entities_count": CountDocumentEntities(doc.id)
            # "document_level": doc_level,
            # "approval_reference": approval_references,
            # "approval_date": approval_date,
            # "subject": doc.subject_id.name,

        }
        result.append(res)
    return JsonResponse({'documentsList': result})


def CountDocumentEntities(document_id):
    doc_entities = AINamedEntities.objects.filter(document_id=document_id)
    entities_list = []
    for object in doc_entities:
        paragraph_entities = object.entities
        for ent in paragraph_entities:
            entities_list.append(ent)
    count = len(set(entities_list))
    return count


def leadership_slogan(request):
    country_list = Country.objects.all()
    slogan_list = []
    country_map = get_country_maps(country_list)
    slogan_map = {i.year: f"{i.year} - {i.content}" for i in slogan_list}
    slogan_map_keyword = {i.year: i.keywords for i in slogan_list}
    return render(request, 'en_doc/leadership_slogan.html',
                  {'countries': country_map, 'slogans': slogan_map, 'slogan_keyword': slogan_map_keyword})


def portal_analysis(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/portal_analysis.html', {'countries': country_map})


def definition(request):
    country = Country.objects.all()
    country_map = get_country_maps(country)
    return render(request, 'en_doc/definition.html', {'countries': country_map})


def legal_literature_adaptation(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/legal_literature_adaptation.html', {'countries': country_map})


def search_actors(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/search_actors.html', {'countries': country_map})


def show_actors(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/show_actors.html', {'countries': country_map})


def collective_actors(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/collective_actors.html', {'countries': country_map})


def executive_regulations_analysis(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/executive_regulations_analysis.html', {'countries': country_map})


def executive_regulations_supervision(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/executive_regulations_supervision.html', {'countries': country_map})


def principles_analysis(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/principles_analysis.html', {'countries': country_map})


def regularity(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/regularity.html', {'countries': country_map})


def window_unit(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/window_unit.html', {'countries': country_map})


def business_advisor(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/business_advisor.html', {'countries': country_map})


def official_references(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/official_references.html', {'countries': country_map})


def regularity_life_cycle(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/regularity_life_cycle.html', {'countries': country_map})


def AI_topics(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'en_doc/AI_topics.html', {'countries': country_map})


def recommendation(request):
    return render(request, 'en_doc/recommendation.html')


def compare_document(request):
    return render(request, 'en_doc/compare_document.html')
    # ---------------- query ------------------------


def GetDocumentContent(request, document_id):
    document_paragraphs = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)

    for paragraph in paragraphs:
        document_name = paragraph.document_id.name
        paragraph_text = paragraph.text
        document_paragraphs.append(
            {'paragraph_text': paragraph_text + '\n', 'document_name': document_name})

    return JsonResponse({'document_paragraphs': document_paragraphs})


def SearchDocumentByname(request, country_id, text):
    document_list = Document.objects.filter(country_id_id=country_id, name__icontains=text)

    data = list(CUBE_DocumentJsonList.objects.filter(document_id__in=document_list).values_list('json_text', flat=True))
    document_count = data.__len__()

    return JsonResponse({'documentsList': data, 'document_count': document_count})


def document_json_list(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.English import DocsCreateDocumentsListCubeData
    DocsCreateDocumentsListCubeData.apply(None, file)
    return redirect('zip')


def GetActorsList(request):
    document_actors = DocumentActor.objects.all().values("actor_id_id").distinct()
    document_list = Actor.objects.filter(id__in=document_actors).order_by("name")

    actors_list = []

    for actor in document_list:
        actor_dict = [actor.id, actor.name]
        actors_list.append(actor_dict)

    return JsonResponse({'Actors_List': actors_list})

def dict2Array(dictionary):
    result = []
    for key, value in dictionary.items():
        result.append([key, value])
    return result

def GetDocumentActorsList(request, country_id, actors_list):
    actors_list = [int(actor_id) for actor_id in actors_list.split("_")]

    Result_Doc_List = None
    if 0 in actors_list:
        Result_Doc_List = DocumentActor.objects.filter(document_id__country_id_id=country_id).values("document_id").annotate(
            count=Count("document_id")).order_by("-count")
    else:
        Result_Doc_List = DocumentActor.objects.filter(document_id__country_id_id=country_id, actor_id_id__in=actors_list).values(
            "document_id").annotate(count=Count("document_id")).order_by("-count")

    Result = []
    index = 1

    level_list = []
    approval_reference_list = []
    approval_date_list = []

    for value in Result_Doc_List:
        document_id = value["document_id"]
        count = value["count"]

        doc_information = GetDocumentById_Local(document_id)

        document_name = doc_information["name"]
        approval_date = doc_information["approval_date"]
        approval_reference = doc_information["approval_reference"]

        approval_date_list.append(doc_information["approval_date"])
        approval_reference_list.append(doc_information["approval_reference"])
        level_list.append(doc_information["level"])

        detail_function = "DetailFunction(" + str(document_id) + ")"

        detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" ' + ' onclick="' + detail_function + '" data-bs-target="#detailModal">Detail</button>'

        res = {"id": index,
               "name": document_name,
               "approval_date": approval_date,
               "approval_reference": approval_reference,
               "count": count,
               "detail": detail}

        Result.append(res)

        index += 1

    approval_date_chart_data = dict2Array(dict(Counter(approval_date_list)))
    approval_reference_chart_data = dict2Array(dict(Counter(approval_reference_list)))
    level_chart_data = dict2Array(dict(Counter(level_list)))

    return JsonResponse({'Document_Information': Result,
                         "approval_date_chart_data": approval_date_chart_data,
                         "approval_reference_chart_data": approval_reference_chart_data,
                         "level_chart_data": level_chart_data
                         })


def GetActorsChartData(request, document_id):

    ChartData = DocumentActor.objects.filter(document_id_id=document_id).values("actor_id__name").annotate(count=Count("actor_id__name")).order_by("count")

    result = []

    for row in ChartData:
        res = [row["actor_id__name"], row["count"]]
        result.append(res)

    return JsonResponse({'Actor_ChartData': result})

def GetActorsParagraphs(request, document_id, actor_name):
    actor_id = Actor.objects.get(name=actor_name)
    paragraph_id_list = list(DocumentActor.objects.filter(actor_id=actor_id, document_id_id = document_id).values_list('paragraph_id_id', flat=True))
    paragraph_text_list = DocumentParagraphs.objects.filter(id__in = paragraph_id_list).order_by("number")

    result = []
    for row in paragraph_text_list:
        result.append(row.text)

    return JsonResponse({'Paragraph_Text': result})

def GetDocumentActorsParagraphs(request, document_id, actors_list):
    actors_list = [int(actor_id) for actor_id in actors_list.split("_")]

    if 0 in actors_list:
        Result_Paragraph_List = list(DocumentActor.objects.filter(document_id_id=document_id).values_list('paragraph_id_id', flat=True))
    else:
        Result_Paragraph_List = list(DocumentActor.objects.filter(document_id_id=document_id, actor_id_id__in=actors_list).values_list('paragraph_id_id', flat=True))

    paragraph_text_list = DocumentParagraphs.objects.filter(id__in=Result_Paragraph_List).order_by("number")

    result = []
    for row in paragraph_text_list:
        result.append(row.text)

    return JsonResponse({'Paragraph_Text': result})

def GetActorsListById(request, actors_list):
    actors_list = [int(actor_id) for actor_id in actors_list.split("_")]
    if 0 in actors_list:
        actors_name = Actor.objects.all()
    else:
        actors_name = Actor.objects.filter(id__in=actors_list)

    result = []
    for row in actors_name:
        result.append(row.name)

    return JsonResponse({'Actors_Name': result})


# ------------------- ES Search -----------------------------

def filter_doc_fields(res_query,level_id, approval_reference_id, from_year, to_year):

    if approval_reference_id != 0:
        approval_reference_name = ApprovalReference.objects.get(id = approval_reference_id).name

        approval_ref_query = {
        "term": {
        "approval_reference_name.keyword": approval_reference_name
        }            
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if level_id != 0:
        level_name = Level.objects.get(id = level_id).name
        level_query = {
        "term": {
        "level_name.keyword": level_name
        }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------

    First_Year = 1700
    Last_Year = 2023

    if from_year != 0 or to_year !=0:

        from_year = from_year if from_year!=0 else First_Year
        to_year = to_year if to_year!=0 else Last_Year

        year_query = {
            "range": {
                "approval_date": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }
        

        res_query['bool']['filter'].append(year_query)


    return res_query


def boolean_search_text(res_query,place,text,operator,ALL_FIELDS):

    if  place == 'عنوان' :
        title_query = {
            "match": {
                "name": {
                "query": text,
                "operator":operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif  place == 'متن' :
        content_query = {
        "match": {
            "attachment.content": {
                "query": text,
                "operator":operator
                    }
                }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)
    else:
        title_content_query = {
                "bool" : {
                    
                "should": [
                {
                    "match": {
                        "name": {
                        "query": text,
                        "operator":operator
                        }
                    }
                },
                {
                "match": {
                    "attachment.content": {
                        "query": text,
                        "operator":operator
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


def exact_search_text(res_query,place,text,ALL_FIELDS):

    if  place == 'عنوان' :
        title_query = {
            "match_phrase": {
            "name": text
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif  place == 'متن' :
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
                "bool" : {
                "should": [
                {
                "match_phrase": {
                    "name": text
                }
                },
                {
                "match_phrase" : {
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


def SearchDocument_ES(request, country_id, level_id, approval_reference_id, from_year, to_year,
                        place, text,search_type):

    fields = [level_id, approval_reference_id, from_year, to_year] 
    
    res_query = {
        "bool":{}
    }


    ALL_FIELDS = True

    if not all(field==0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query,level_id, approval_reference_id, from_year, to_year)
    
    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query,place,text,ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query,place,text,search_type,ALL_FIELDS)


    country_obj = Country.objects.get(id = country_id)
    index_name = standardIndexName(country_obj,Document.__name__)


    response = client.search(index=index_name,
        _source_includes = ['document_id','name','approval_reference_name','approval_date',
            "level_name",'approval_year','communicated_date'],
        request_timeout=40,
        query=res_query,
        size=100

    )
  
    # print("Got %d Hits:" % response['hits']['total']['value'])
    total_hits = response['hits']['total']['value']

    return JsonResponse({
   "result":response['hits']['hits'],
   'total_hits':total_hits })


def GetSearchDetails_ES(request,document_id,search_type,text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)

    local_index = standardIndexName(country,Document.__name__)

        
    result_text = ''
    place = 'متن'
    
    res_query = {
        "bool":{
            "filter":{
                "term":{
                    "document_id":document_id
                }
            }
        }
    }
    
    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query,place,text,False)
        else:
            res_query = boolean_search_text(res_query,place,text,search_type,False)

    response = client.search(index=local_index,
    _source_includes = ['document_id','name','attachment.content'],
    request_timeout=40,
    query=res_query,
    highlight = {
        "order":"score",
        "fields" : {
        "attachment.content" : 
        {"pre_tags" : ["<em>"], "post_tags" : ["</em>"],
            "number_of_fragments":0
        }
    }}

)
    if len(response['hits']['hits']) > 0:
        result_text = response['hits']['hits'][0]["highlight"]["attachment.content"][0]
    else:
        response = client.get(index=local_index, id=document_id,
        _source_includes = ['document_id','name','attachment.content']
        )
        result_text = response['_source']['attachment']['content']


    return JsonResponse({
   "result":result_text})


def GetActorsChartData_ES(request,text,doc_ids_text):

  
    # ---------- Generate Data -------------

    doc_ids = doc_ids_text.split(',')

    words = text.split(" ")
    actors_chart_data = getActorsChartData(words, doc_ids)
    if len(actors_chart_data) < 1:
        temp = {'sum_columns':0, 'column_1':0, 'column_2':0, 'column_3':0}
        entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = temp, \
                                                                                   {'sum_columns':'صفر', 'column_1':'صفر', 'column_2':'صفر', 'column_3':'صفر'},\
                                                                                   temp, temp, temp
    else:
        entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = chart_entropy(actors_chart_data)

    return JsonResponse({
                         'actors_chart_data': actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })


# ------------------------------------------------------------------