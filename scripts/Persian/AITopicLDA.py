import re
from scripts.Persian import Preprocessing
from doc.models import Document, DocumentParagraphs, AISimilarityDoc, AILDATopic, AILDADocToTopic, AI_Subject_By_LDA, DocLDAScore
# from transformers import BertTokenizer, TFBertModel
from hazm import sent_tokenize, Normalizer
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaMulticore
from collections import Counter
import math
import numpy as np
from scipy import spatial

normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"


# import nltk.data
# nltk_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


# bert_tokenizer = BertTokenizer.from_pretrained(model_name)


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

    # Empty the database
    AILDATopic.objects.filter(country=Country).delete()
    AILDADocToTopic.objects.filter(document__country_id=Country).delete()
    AI_Subject_By_LDA.objects.filter(country=Country).delete()
    DocLDAScore.objects.filter(document__country_id=Country).delete()
    
    document_list = Document.objects.filter(country_id=Country)
    number_of_topic = 50

    # Aggregation the text of documents
    token_list = []
    id_list = []

    # max topic for each doc
    max_topic_for_doc = {}

    for d in document_list:
        max_topic_for_doc[d.id] = ("", 0)
        paragraph_list = DocumentParagraphs.objects.filter(document_id=d)
        text = ""
        for p in paragraph_list:
            text += LocalPreprocessing(p.text)

        text = Preprocessing.Preprocessing(text, stem=False)
        token_list.append(text)
        id_list.append(d.id)

    # LDA
    dictionary = Dictionary(token_list)
    dictionary.filter_extremes(no_below=int(len(id_list)*0.01), no_above=0.35, keep_n=None)
    corpus = [dictionary.doc2bow(doc) for doc in token_list]
    lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=50, num_topics=number_of_topic, workers=4, passes=10)
    # lda_topic = lda_model.get_topic_terms(i, topn=h_highest_topic_word*2)

    # Save topics
    create_list = []
    batch_size = 1000
    for i in range(0, number_of_topic):
        topic = lda_model.get_topic_terms(i, topn=10)
        words_json = {}
        for item in topic:
            word = dictionary[item[0]]
            score = item[1]
            words_json[word] = str(round(score,4))

        topic_obj = AILDATopic(country=Country, topic_id=i, words=words_json)
        create_list.append(topic_obj)

    AILDATopic.objects.bulk_create(create_list)

    # get topics (for get id)
    topic_list = AILDATopic.objects.filter(country=Country)
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
        for topic in topic_dict.values():
            topic_score[topic] = 0
        for t in doc_topic:
            doc_id = id_list[i]
            topic_id = topic_dict[t[0]]
            score = round(t[1]*100,2)
            obj = AILDADocToTopic(document_id=doc_id, topic_id=topic_id, score=score )
            topic_score[topic_id] = score
            create_list_doc.append(obj)
            # for max topic score
            if max_topic_for_doc[doc_id][1] < score:
                max_topic_for_doc[doc_id] = (topic_id, score)

            if batch_size < len(create_list_doc):
                AILDADocToTopic.objects.bulk_create(create_list_doc)
                create_list_doc = []
                
        doc_id = Document.objects.get(id=id_list[i])       
        topic_score_str = ""
        for topic in topic_score.keys():
            topic_score_str += str(topic_score[topic]) + "--"
        obj = DocLDAScore(document=doc_id, scores=topic_score_str ) 
        if selected_country_lang in ['کتاب','استاندارد']:
            create_lda_topic_score_doc.append(obj) 
              
    AILDADocToTopic.objects.bulk_create(create_list_doc)
    DocLDAScore.objects.bulk_create(create_lda_topic_score_doc)

    # for calculate topic correlation score
    for i,doc_topic in enumerate(res):
        document_topic_keyword = Document.objects.get(id=id_list[i]).subject_name
        for t in doc_topic:
            score = round(t[1]*100,2)
            if score > 70:
                list_of_subjects_for_topic[t[0]].append(document_topic_keyword)
    # calculate and save entropy
    max_subject_for_topic = {}
    for i in list_of_subjects_for_topic:
        list_of_subjects_for_topic[i] = Counter(list_of_subjects_for_topic[i])
        en = round(entropy(list_of_subjects_for_topic[i].values()), 2)
        topic_correlation_score = dict(sorted(list_of_subjects_for_topic[i].items(), key=lambda x: x[1], reverse=True))
        if len(topic_correlation_score)>0:
            max_subject = list(topic_correlation_score.keys())[0]
            tModel = AILDATopic.objects.filter(id=topic_dict[i])
            tModel.update(correlation_score=en, dominant_subject_name=max_subject)
            max_subject_for_topic[topic_dict[i]] = (max_subject, en)


    # predict subject
    create_list = []
    for d in document_list:
        try:
            topic_id = max_topic_for_doc[d.id][0]
            topic_score = max_topic_for_doc[d.id][1]/100

            pre_subject = max_subject_for_topic[topic_id][0]
            subject_entropy = max_subject_for_topic[topic_id][1]

            ac = (topic_score * 2) - subject_entropy
            if d.subject_name != pre_subject:
                obj = AI_Subject_By_LDA(document=d, country=Country, subject=d.subject_name,
                                        subject_predict=pre_subject, topic_id=topic_id, Accuracy=ac)
                create_list.append(obj)

        except Exception as e:
            print(e)
            pass

        if batch_size < len(create_list):
            AI_Subject_By_LDA.objects.bulk_create(create_list)
            create_list = []

    AI_Subject_By_LDA.objects.bulk_create(create_list)













    # AISimilarityDoc.objects.filter(document_id1__country_id=Country).delete()
    # document_list = Document.objects.filter(country_id=Country)
    #
    # bach_size = 1000
    # bert_res = {}
    # for d in document_list:
    #     paragraph_list = DocumentParagraphs.objects.filter(document_id=d)
    #     text = ""
    #     for p in paragraph_list:
    #         text += LocalPreprocessing(p.text)
    #     vec = text_to_bert(text)
    #     bert_res[d.id] = tf.convert_to_tensor(vec.detach().numpy())
    #
    # doc_li = [i.id for i in document_list ]
    # create_list = []
    # for docID1 in bert_res:
    #     doc_li.remove(docID1)
    #     for docID2 in doc_li:
    #         v1 = bert_res[docID1]
    #         v2 = bert_res[docID2]
    #         cosine_sim = 1 - spatial.distance.cosine(v1, v2)
    #         sim_obj = AISimilarityDoc(document_id1_id=docID1, document_id2_id=docID2, sim=round(cosine_sim*100,2) )
    #         create_list.append(sim_obj)
    #
    #         if bach_size < len(create_list):
    #             AISimilarityDoc.objects.bulk_create(create_list)
    #             create_list = []
    #
    # AISimilarityDoc.objects.bulk_create(create_list)
