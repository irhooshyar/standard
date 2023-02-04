from django.urls import path
from ru_doc import views

urlpatterns = [
    path('', views.index, name='ru_index'),

    # main pages urls
    path('information/', views.information, name='ru_information'),
    path('graph/', views.graph, name='ru_graph'),
    path('comparison/', views.comparison, name='ru_comparison'),
    path('search/', views.search, name='ru_search'),
    path('subject/', views.subject, name='ru_subject'),
    path('subject_statistics/', views.subject_statistics, name='ru_subject_statistics'),
    path('adaptation/', views.adaptation, name='ru_adaptation'),
    path('votes_analysis/', views.votes_analysis, name='ru_votes_analysis'),
    path('subject_graph/', views.subject_graph, name='ru_subject_graph'),
]