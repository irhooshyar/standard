import re
from doc.models import Document, DocumentParagraphs, ParagraphsSubject,UserLDATopicLabel
from doc.models import AIParagraphLDATopic, AILDAParagraphToTopic, AI_Paragraph_Subject_By_LDA, ParagraphLDAScore, AILDAResults
from hazm import *
from gensim.corpora.dictionary import Dictionary
from django.db.models import Max, Min, F, IntegerField, Q
from sklearn.metrics.pairwise import euclidean_distances,cosine_similarity
from gensim.models import LdaMulticore
from collections import Counter
import math
from abdal import config
import numpy as np
from pathlib import Path
from scipy import spatial
import json


LDA_configs = {
    "اسناد رهبری":{
        "num_topic":[5,10,15,20,25,30,35,40,45,50]
        },
    "فاوا":{
        "num_topic":[5,10,15,20,25]
    },
    "هوش‌یار":{
        "num_topic":[5,10,15,20,25,30,35,40,45,50,60,70,80,90,100]
    }
}

normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"


normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"

stemmer = Stemmer()

def create_heatmap_data(distance_array):
    chart_data = [] # array of blocks

    i = 0
    for row in distance_array:
        i += 1
        j = 0
        x_value = "C"+ str(i)

        for col in row:
            j += 1
            y_value = "C"+ str(j)

            block = {"x":x_value,"y":y_value,"heat":float(round(float(col),3))}
            chart_data.append(block)

    return chart_data

def stemming(word):
    word_s = stemmer.stem(word)
    return word_s

def LocalPreprocessing(text):
    # Cleaning
    ignoreList = ["!", "@", "$", "%", "^", "&", "*", "_", "+", "*", "'",
                  "{", "}", "[", "]", "<", ">", ".", '"', "\t"]
    for item in ignoreList:
        text = text.replace(item, " ")

    # Delete non-ACII char
    for ch in text:
        if ch != "/" and ord(ch) <= 255 or (ord(ch) > 2000):
            text = text.replace(ch, " ")

    return text

def Preprocessing(country_name,text, tokenize=True, stem=True, removeSW=True, normalize=True, removeSpecialChar=True):

    # Cleaning
    if removeSpecialChar:
        ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",", ""
                                                                                                                "{",
                      "}", '\xad', '­'
                      "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"',
                      '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', "٫",
                      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for item in ignoreList:
            text = text.replace(item, " ")

    # Normalization
    if normalize:
        normalizer = Normalizer()
        text = normalizer.normalize(text)

        # Delete non-ACII char
        for ch in text:
            if ord(ch) <= 255 or (ord(ch) > 2000):
                text = text.replace(ch, " ")

    # Tokenization
    if tokenize:
        text = [word for word in text.split(" ") if word != ""]

        # stopwords
        if removeSW:

            stopword_list = open(Path(config.PERSIAN_PATH, "all_stopwords.txt"), encoding="utf8").read().split(
                "\n")

            stopword_list = list(set(stopword_list))


            if country_name == 'فاوا':
                stopword_list += ['فناوری','اطلاعات','ارتباطات']
            
            if country_name == 'اسناد رهبری':
                rahbari_stopword_list = open(Path(config.PERSIAN_PATH, "rahbari_stopwords.txt"), encoding="utf8").read().split(
                    "\n")
                
                rahbari_stopword_list = list(set(rahbari_stopword_list))
                stopword_list += rahbari_stopword_list

            text = [word for word in text if word not in stopword_list]

            # filtering
            text = [word for word in text if len(word) >= 2]

        # stemming
        if stem:
            text = [stemming(word) for word in text]

    return text

def entropy(array):
    total_entropy = 0
    s = sum(array)

    for i in array:
        pi = (i/s)
        if i != 0:
            total_entropy += -pi * math.log(pi, 2)

    return total_entropy

def apply(folder_name, Country):
    selected_country_lang = Country.language
    country_name = Country.name

    # Empty the database
    AIParagraphLDATopic.objects.filter(country=Country).delete()
    AILDAParagraphToTopic.objects.filter(country=Country).delete()
    AI_Paragraph_Subject_By_LDA.objects.filter(country=Country).delete()
    ParagraphLDAScore.objects.filter(country=Country).delete()
    AILDAResults.objects.filter(country=Country).delete()
    UserLDATopicLabel.objects.filter(topic__country__id = Country.id)

    if country_name == 'هوش‌یار':
        paragraphs_list = DocumentParagraphs.objects.filter(document_id__country_id__id=Country.id, document_id__type_name='قانون').values()
    else:
        paragraphs_list = DocumentParagraphs.objects.filter(document_id__country_id__id=Country.id).values()

    PARAGRAPH_SUBJECT_DICT = {}
    for para in paragraphs_list:
        subject_name = ''
        try:
            subject_name = ParagraphsSubject.objects.get(country__id=Country.id, paragraph_id=para['id'], version__id=12).subject1_name
        except:
            subject_name = "نامشخص"
        
        PARAGRAPH_SUBJECT_DICT[para['id']]= subject_name
        para['subject_name'] = subject_name


    # Aggregation the text of documents
    token_list = []
    id_list = []

    # max topic for each doc
    max_topic_for_para = {}

    min_para_length = 80
    text = ""
    for p in paragraphs_list:
        if len(p['text']) > min_para_length:
            max_topic_for_para[p['id']] = ("", 0)
            text = LocalPreprocessing(p['text'])
            text = Preprocessing(Country.name,text, stem=False)
            token_list.append(text)
            id_list.append(p['id'])
    
    

    # LDA
    dictionary = Dictionary(token_list)
    dictionary.filter_extremes(no_below=int(len(id_list)*0.01), no_above=0.35, keep_n=None)
    corpus = [dictionary.doc2bow(para) for para in token_list]

    terms_count = len(dictionary.token2id)

    country_LDA_configs = LDA_configs[country_name]

    num_topic = country_LDA_configs['num_topic']
    

    SIZE_TO_ID = {}

    for k in num_topic:
        number_of_topic = k
        lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=50, num_topics=number_of_topic, workers=4, passes=10)
        # lda_topic = lda_model.get_topic_terms(i, topn=h_highest_topic_word*2)

        # Save topics
        create_list = []
        list_topic_cernters = []
        batch_size = 1000
        for i in range(0, number_of_topic):
            topic = lda_model.get_topic_terms(i, topn=20)
            topic_all_terms = lda_model.get_topic_terms(i, topn=terms_count)
            sorted_topic_all_terms = sorted(topic_all_terms, key=lambda x: x[0])
            list_topic_all_terms = [item[1] for item in sorted_topic_all_terms]
            list_topic_cernters.append(list_topic_all_terms)
            words_json = {}
            for item in topic:
                word = dictionary[item[0]]
                score = item[1]
                words_json[word] = str(round(score,4))

            topic_obj = AIParagraphLDATopic(country=Country, topic_id=i, topic_name='C'+ str(i+1), words=words_json, number_of_topic=number_of_topic)
            create_list.append(topic_obj)

        AIParagraphLDATopic.objects.bulk_create(create_list)

        distance_array = euclidean_distances(list_topic_cernters)
        heatmap_chart_data =  create_heatmap_data(distance_array)
        

        similarity_array = cosine_similarity(list_topic_cernters)
        similarity_chart_data =  create_heatmap_data(similarity_array)

        AILDAResults.objects.create(
            country = Country,
            number_of_topic = number_of_topic,
            heatmap_chart_data = {"data":heatmap_chart_data},
            similarity_chart_data = {"data":similarity_chart_data}
        )



        # get topics (for get id)
        topic_list = AIParagraphLDATopic.objects.filter(country=Country, number_of_topic=number_of_topic)
        topic_dict = {}
        list_of_subjects_for_topic = {}
        for t in topic_list:
            topic_dict[t.topic_id] = t.id
            list_of_subjects_for_topic[t.topic_id] = []

        res = lda_model[corpus]
        create_list_doc = []
        create_lda_topic_score_doc = []

        # Save document score for each topic
        for i,doc_topic in enumerate(res):
            topic_score = {}
            paragraph = DocumentParagraphs.objects.get(id=id_list[i])

            for topic in topic_dict.values():
                topic_score[topic] = 0
            for t in doc_topic:
                para_id = id_list[i]
                topic_id = topic_dict[t[0]]
                score = round(t[1]*100,2)
                if score > 50:
                    obj = AILDAParagraphToTopic(country=Country, paragraph_id=para_id, topic_id=topic_id, score=score, number_of_topic=number_of_topic )
                    create_list_doc.append(obj)
                topic_score[topic_id] = score
                # for max topic score
                if max_topic_for_para[para_id][1] < score:
                    max_topic_for_para[para_id] = (topic_id, score)

                if batch_size < len(create_list_doc):
                    AILDAParagraphToTopic.objects.bulk_create(create_list_doc)
                    create_list_doc = []
                        
            topic_score_str = ""
            for topic in topic_score.keys():
                topic_score_str += str(topic_score[topic]) + "--"
            obj = ParagraphLDAScore(country=Country, paragraph=paragraph, scores=topic_score_str, number_of_topic=number_of_topic ) 
            create_lda_topic_score_doc.append(obj) 
                
        AILDAParagraphToTopic.objects.bulk_create(create_list_doc)
        ParagraphLDAScore.objects.bulk_create(create_lda_topic_score_doc)

        # for calculate topic correlation score
        for i,doc_topic in enumerate(res):
            paragraph_topic_keyword = PARAGRAPH_SUBJECT_DICT[id_list[i]]
            for t in doc_topic:
                score = round(t[1]*100,2)
                if score > 50:
                    list_of_subjects_for_topic[t[0]].append(paragraph_topic_keyword)
        # calculate and save entropy
        max_subject_for_topic = {}
        for i in list_of_subjects_for_topic:

            paragraph_count = len(list_of_subjects_for_topic[i])
            subjects_list_chart_data = []
            list_of_subjects_for_topic[i] = Counter(list_of_subjects_for_topic[i])
            
            for key,value in list_of_subjects_for_topic[i].items():
                subjects_list_chart_data.append([key,value])

            subjects_list_chart_data_json = {"data":subjects_list_chart_data}

            en = round(entropy(list_of_subjects_for_topic[i].values()), 2)
            topic_correlation_score = dict(sorted(list_of_subjects_for_topic[i].items(), key=lambda x: x[1], reverse=True))
            if len(topic_correlation_score)>0:
                max_subject = list(topic_correlation_score.keys())[0]
                tModel = AIParagraphLDATopic.objects.filter(id=topic_dict[i])
                tModel.update(correlation_score=en, 
                dominant_subject_name=max_subject,
                subjects_list_chart_data_json=subjects_list_chart_data_json,
                paragraph_count=paragraph_count)
                max_subject_for_topic[topic_dict[i]] = (max_subject, en)


        # predict subject
        create_list = []
        for p in paragraphs_list:
            try:
                topic_id = max_topic_for_para[p['id']][0]
                topic_score = max_topic_for_para[p['id']][1]/100

                pre_subject = max_subject_for_topic[topic_id][0]
                subject_entropy = max_subject_for_topic[topic_id][1]

                ac = (topic_score * 2) - subject_entropy
                if p['subject_name'] != pre_subject:
                    obj = AI_Paragraph_Subject_By_LDA(paragraph_id=p["id"], country=Country, subject=p['subject_name'],
                                            subject_predict=pre_subject, topic_id=topic_id, Accuracy=ac, number_of_topic=number_of_topic)
                    create_list.append(obj)

            except Exception as e:
                print(e)
                pass

            if batch_size < len(create_list):
                AI_Paragraph_Subject_By_LDA.objects.bulk_create(create_list)
                create_list = []

        AI_Paragraph_Subject_By_LDA.objects.bulk_create(create_list)
    