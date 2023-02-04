
import re

from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
import os
from django.forms import FileField
from doc.forms import ZipFileForm
from en_doc.models import *
from scripts import ZipFileExtractor, StratAutomating
from abdal import config
import shutil
import after_response
import json
from pathlib import Path
from django.http import JsonResponse
from scripts.English import Preprocessing
from django.db.models import Max, Min, Count, Sum, F, Q, IntegerField
from django.db.models.functions import Substr, Cast, Length
from django.core.files.storage import FileSystemStorage
import docx2txt


def get_country_maps(country_objects):
    dataset_map = {}
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "روسی":
            dataset_map[id] = name
    return dataset_map


def index(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/index.html', {'countries': country_map})


def information(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/information.html', {'countries': country_map})


def graph(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/graph.html', {'countries': country_map})


def comparison(request):
    return render(request, 'ru_doc/comparison.html')


def search(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    print("searchhh")
    return render(request, 'ru_doc/search.html', {'countries': country_map})


def subject(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/subject.html', {'countries': country_map})


def subject_statistics(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/subject_statistics.html', {'countries': country_map})


def votes_analysis(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/vote_analysis.html', {'countries': country_map})


def adaptation(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'ru_doc/adaptation.html', {'countries': country_map})


def subject_graph(request):
    return render(request, 'ru_doc/subject_graph.html')
