
from pathlib import Path
from hazm import *
import time
from abdal import config
from django.db.models import Count

from doc.models import Document,DocumentParagraphs,\
    ClusterTopic,ParagraphsTopic,ClusteringAlorithm,ClusteringResults, \
    FeatureSelectionAlgorithm, FeatureSelectionResults,\
    TopicDiscriminantWords,ParagraphsSubject,CUBE_Clustering_TableData

from hazm import sent_tokenize, Normalizer
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaMulticore
from collections import Counter
import math
import numpy as np


# -----------------------------

# Data Structures
import numpy  as np
import pandas as pd

# Corpus Processing
import re
import nltk.corpus
from unidecode import unidecode
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text  import TfidfVectorizer ,TfidfTransformer
from sklearn.preprocessing import normalize

# K-Means
from sklearn import cluster

# Visualization and Analysis
import matplotlib.pyplot  as plt
import matplotlib.cm as cm
import seaborn as sns
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.metrics.pairwise import euclidean_distances

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix,accuracy_score
from sklearn import tree
from sklearn.tree import plot_tree

from sklearn.cluster import MiniBatchKMeans

from . import CreateDecisionTree
# --------------------------------

clustering_configs = {
    "فاوا":{
        "min_k":5,
        "max_k":20,
        "step":5,
        "batch_size":512
    },
    "هوش‌یار":{
        "min_k":5,
        "max_k":50,
        "step":5,
        "batch_size":4096
    }
}

clustering_configs_2 = {
    "فاوا":{
        "min_k":21,
        "max_k":25,
        "step":1,
        "batch_size":512
    },
    "هوش‌یار":{
        "min_k":60,
        "max_k":100,
        "step":10,
        "batch_size":4096
    }
}


normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"

stemmer = Stemmer()


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


def printAvg(avg_dict):
    for avg in sorted(avg_dict.keys(), reverse=True):
        print("Avg: {}\tK:{}".format(avg.round(4), avg_dict[avg]))
        
def plotSilhouette(df, n_clusters, kmeans_labels, silhouette_avg):
    fig, ax1 = plt.subplots(1)
    fig.set_size_inches(8, 6)
    ax1.set_xlim([-0.2, 1])
    ax1.set_ylim([0, len(df) + (n_clusters + 1) * 10])
    
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--") # The vertical line for average silhouette score of all the values
    ax1.set_yticks([])  # Clear the yaxis labels / ticks
    ax1.set_xticks([-0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
    plt.title(("Silhouette analysis for K = %d" % n_clusters), fontsize=10, fontweight='bold')
    
    y_lower = 10
    sample_silhouette_values = silhouette_samples(df, kmeans_labels) # Compute the silhouette scores for each sample
    for i in range(n_clusters):
        ith_cluster_silhouette_values = sample_silhouette_values[kmeans_labels == i]
        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = cm.nipy_spectral(float(i) / n_clusters)
        ax1.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values, facecolor=color, edgecolor=color, alpha=0.7)

        ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i)) # Label the silhouette plots with their cluster numbers at the middle
        y_lower = y_upper + 10  # Compute the new y_lower for next plot. 10 for the 0 samples
    plt.show()
    
        
def silhouette(kmeans_dict, df, plot=False):
    print('Running silhouette ...')

    df = df.to_numpy()
    avg_dict = dict()
    for n_clusters, kmeans in kmeans_dict.items():      
        kmeans_labels = kmeans.predict(df)
        silhouette_avg = silhouette_score(df, kmeans_labels) # Average Score for all Samples
        avg_dict.update( {silhouette_avg : n_clusters} )
    
        if(plot): plotSilhouette(df, n_clusters, kmeans_labels, silhouette_avg)

    printAvg(avg_dict)

    best_silhouete = max(avg_dict.keys())
    best_cluster_count = avg_dict[best_silhouete]

    return [best_silhouete,best_cluster_count]

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

            stopword_list_1 = open(Path(config.BASE_PATH, "text_files/stopWords.txt"), encoding="utf8").read().split(
                "\n")

            stopword_list_2 = open(Path(config.PERSIAN_PATH, "stopwords.txt"), encoding="utf8").read().split(
                "\n")

            stopword_list_3 = open(Path(config.PERSIAN_PATH, "TopicModeling_Stopwrods.txt"), encoding="utf8").read().split(
                "\n")

            stopword_list_4 = open(Path(config.PERSIAN_PATH, "ClusteringCustomStopwords.txt"), encoding="utf8").read().split(
                "\n")

            stopword_list = stopword_list_1 + stopword_list_2 + stopword_list_3 + stopword_list_4


            stopword_list = list(set(stopword_list))

            if country_name == 'فاوا':
                stopword_list += ['فناوری','اطلاعات','ارتباطات']

            text = [word for word in text if word not in stopword_list]

            # filtering
            text = [word for word in text if len(word) >= 2]

        # stemming
        if stem:
            text = [stemming(word) for word in text]

    return text


def FeatureExtraction(corpus):
    from sklearn.preprocessing import MaxAbsScaler,StandardScaler

    print('Running FeatureExtraction ...')

    vectorizer = TfidfVectorizer(max_df = 0.35
    , min_df = 0.01
    # ,ngram_range = (2,2)
    ,max_features = 10000
    )



    X = vectorizer.fit_transform(corpus)
    # print(f"X: {X}")

    # idf = X.idf_ 
    # vocabulary = vectorizer.vocabulary_ 


    scaler = MaxAbsScaler()
    # scaler = StandardScaler(with_mean=False)

    X =scaler.fit_transform(X)

    tf_idf = pd.DataFrame(data = X.toarray(), columns=vectorizer.get_feature_names_out())

    final_df = tf_idf

    print("{} rows".format(final_df.shape))
    # print(final_df.T.nlargest(5, 1))

    return [vectorizer,final_df]


def run_KMeans(max_k, data,configs):
    print('Running run_KMeans ...')

    # max_k += 1
    # kmeans_results = dict()
    # for k in range(max_k - 1 , max_k):
    kmeans = cluster.MiniBatchKMeans(n_clusters = max_k
                        , init = 'k-means++'
                        , n_init = 10
                        , tol = 0.0001
                        , random_state = 1
                        ,max_no_improvement=200
                        , batch_size = configs['batch_size']
                        , max_iter = 1000
                        #    , algorithm = 'full'
                        )

        # kmeans_results.update( {k : kmeans.fit(data)} )
        
    return kmeans.fit(data)


def get_top_features_cluster(tf_idf_array, prediction, n_feats,vectorizer):
    print("Running get_top_features_cluster ...")

    labels = np.unique(prediction)
    dfs = []
    for label in labels:
        id_temp = np.where(prediction==label) # indices for each cluster
        x_means = np.mean(tf_idf_array[id_temp], axis = 0) # returns average score across cluster

        sorted_means = np.argsort(x_means)[::-1][:n_feats] # indices with top 20 scores
        features = vectorizer.get_feature_names_out()
        best_features = [(features[i], x_means[i]) for i in sorted_means]
        df = pd.DataFrame(best_features, columns = ['features', 'score'])
        dfs.append(df)
    return dfs

def plotWords(dfs, n_feats):
    plt.figure(figsize=(8, 4))
    for i in range(0, len(dfs)):
        plt.title(("Most Common Words in Cluster {}".format(i)), fontsize=10, fontweight='bold')
        sns.barplot(x = 'score' , y = 'features', orient = 'h' , data = dfs[i][:n_feats])
        plt.show()




# Transforms a centroids dataframe into a dictionary to be used on a WordCloud.
def centroidsDict(centroids, index):
    a = centroids.T[index].sort_values(ascending = False).reset_index().values
    centroid_dict = dict()

    for i in range(0, len(a)):
        centroid_dict.update( {a[i,0] : a[i,1]} )

    return centroid_dict

def generateWordClouds(centroids):
    wordcloud = PersianWordCloud(max_font_size=100, background_color = 'white',
    only_persian=True,no_reshape=True)

    for i in range(0, len(centroids)):
        centroid_dict = centroidsDict(centroids, i)        
        wordcloud.generate_from_frequencies(centroid_dict)

        plt.figure()
        plt.title('Cluster {}'.format(i))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()



    
def save_topics_to_db(Country,dfs,k):
    print("save_topics_to_db")
    i = 0
    create_list = []
    topic_id_list = []

    for cluster in dfs:
        word_dict = {}

        for index,row in cluster.iterrows():

            word = row['features']
            score = row['score']

            word_dict[word] = str(round(score,4))

        i += 1

        topic_name = f"C{i}"
        # print(f"word_dict= {word_dict}")

        topic_id = str(Country.id) + "-KMS-" + str(k) + "-T-"+str(i)
        topic_id_list.append(topic_id)

        algorithm_obj = ClusteringAlorithm.objects.get(name = "K-Means",
        input_vector_type = "TF-IDF",cluster_count = k)


        topic_obj = ClusterTopic(country=Country,id = topic_id, name=topic_name, words=word_dict,
            algorithm = algorithm_obj)
        
        create_list.append(topic_obj)

    ClusterTopic.objects.bulk_create(create_list)
    
    return topic_id_list
    print(f"{len(create_list)} created.")

def clean_tables(Country,size_to_id_dict):
    clustering_algorithm_ids = size_to_id_dict.values()

    ClusterTopic.objects.filter(
        country = Country,
        algorithm__id__in = clustering_algorithm_ids).delete()

    ParagraphsTopic.objects.filter(
        country = Country,
        topic__algorithm__id__in = clustering_algorithm_ids).delete()

    ClusteringResults.objects.filter(
        country = Country,
        algorithm__id__in = clustering_algorithm_ids).delete()

    FeatureSelectionResults.objects.filter(
        country = Country,
        c_algorithm__id__in = clustering_algorithm_ids
    ).delete()
    
    print('Tabels cleaned.')

def create_corpus(Country):

    corpus = []

    selected_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id
    )

    if Country.name != 'فاوا':

        selected_paragraphs = selected_paragraphs.filter(
                document_id__type_name = 'قانون'
        )

    selected_paragraphs = selected_paragraphs.values()

    selected_para_count = len(selected_paragraphs)
    para_count = 0
    para_id_list = []

    i = 1
    for para in selected_paragraphs[:]:
        para_text = para['text']

        if len(para_text) > 80:
            para_count += 1

            para_text = LocalPreprocessing(para_text)

            para_token_list = Preprocessing(Country.name,para_text, stem=False)
            
            new_para_text = " ".join(para_token_list)
            corpus.append(new_para_text)

            para_id_list.append(para['id'])

        # print(f"{i}/{selected_para_count}")
        i += 1

    print(f"Collected {para_count} paragraphs.")
    

    # create para-subject dict
    paragraph_subject_dict = {}

    paragraph_list = ParagraphsSubject.objects.filter(
        country__id = Country.id,
        version__id = 12,
        paragraph__id__in = para_id_list).values('paragraph_id','subject1_name')

    for para in paragraph_list:
        subject = para['subject1_name']
        paragraph_subject_dict[para['paragraph_id']] = subject if subject != None else 'نامشخص'

    print(f"paragraph_subject_dict created.")

    return [corpus,para_id_list,paragraph_subject_dict]

def apply(folder_name, Country):
    start_t = time.time()
    print('Create Cube Started ..')

    CUBE_Clustering_TableData.objects.filter(country__id = Country.id).delete()


    create_list = []

    country_id = Country.id

    algorithm_ids = ClusteringResults.objects.filter(country__id = Country.id).values_list(
        'algorithm_id',flat=True
    ).distinct()

    for selected_algorithm_id in algorithm_ids:

        clusters =  ClusterTopic.objects.filter(
            country__id = country_id,
            algorithm__id = selected_algorithm_id
        ).values()


        result_list = []
        clusters_data = {}
        dict_table_data = {}
        index = 1
        for cluster in clusters:

            cluster_id = cluster['id']
            cluster_name = cluster['name']
            cluster_words = cluster['words']
            cluster_frequent_keyword_subject = cluster['frequent_keyword_subject']
            cluster_second_frequent_keyword_subject = cluster['second_frequent_keyword_subject'] if cluster['second_frequent_keyword_subject'] != None else "نامشخص"
            cluster_size =  ParagraphsTopic.objects.filter(
                country__id = country_id,
                topic__id = cluster_id  ).distinct().count()

            sorted_word_list =  [k for k, v in sorted(cluster_words.items(), reverse=True, key=lambda item: item[1])]
            
            cluster_word_list = " - ".join(sorted_word_list)

            cluster_entropy = float(cluster['entropy'])


            clusters_data[cluster_id] = {
                "name":cluster_name,
                "cluster_size":cluster_size,
                "entropy":cluster_entropy,
                "frequent_keyword_subject":cluster_frequent_keyword_subject,
                "second_frequent_keyword_subject":cluster_second_frequent_keyword_subject,
                "word_list":cluster_word_list,
            }

            # --- frequent subject --------------------------


            if cluster_entropy <= 0.75 :
                cluster_frequent_keyword_subject = '<span class="text-success">'  + cluster_frequent_keyword_subject + '</span>'
            
            elif cluster_entropy > 0.75 and cluster_entropy <= 1.75: 
                cluster_frequent_keyword_subject = '<span class="text-warning">' + cluster_frequent_keyword_subject + " - " + cluster_second_frequent_keyword_subject + '</span>'
                
            else:
                cluster_frequent_keyword_subject = '<span class="text-danger">' + cluster_frequent_keyword_subject + '</span>'
            

            # ----------------- buttons ---------------------------------------------
            cloud_function = "CloudFunction('" + str(country_id) + "','" + str(cluster_id) + "')"
            cloud_btn = '<button ' \
                'type="button" ' \
                'class="btn modal_btn" ' \
                'data-bs-toggle="modal" ' \
                'data-bs-target="#detailModal" ' \
                'onclick="' + cloud_function + '"' \
                                        '>' + 'مشاهده' + '</button>'


            detail_function = "DetailFunction('" + str(country_id) + "','" + str(cluster_id) + "')"
            detail_btn = '<button ' \
                'type="button" ' \
                'class="btn modal_btn" ' \
                'data-bs-toggle="modal" ' \
                'data-bs-target="#detailModal" ' \
                'onclick="' + detail_function + '"' \
                '>' + 'جزئیات' + '</button>'

            anova_function = "ANOVAFunction('" + str(country_id) + "','" + str(cluster_id) + "')"
            anova_btn = '<button ' \
                'type="button" ' \
                'class="btn modal_btn" ' \
                'data-bs-toggle="modal" ' \
                'data-bs-target="#detailModal" ' \
                'onclick="' + anova_function + '"' \
                                        '>' + 'مشاهده' + '</button>'



            distributions_function = "DistributionsFunction('" + str(country_id) + "','" + str(cluster_id) + "')"
            distributions_btn = '<button ' \
                'type="button" ' \
                'class="btn modal_btn" ' \
                'data-bs-toggle="modal" ' \
                'data-bs-target="#distributionsModal" ' \
                'onclick="' + distributions_function + '"' \
                                        '>' + 'مشاهده' + '</button>'



            row = {
                "id": index, "cluster_name": cluster_name,
                "user_label":
                "<div>" +
                "<input id ='" + cluster_id + "' class='form-control p-1 text-center d-block w-100' value = 'بدون برچسب' type= 'text'/>" + 
                "<button onclick=save_user_label('" + cluster_id + "') class = 'btn btn-outline-success mt-1 p-0 d-block w-100'>ذخیره</button>" +
                "</div>",

                 "word_list": cluster_word_list, "cluster_size": cluster_size,
                 "cloud": cloud_btn,
                "detail": detail_btn, "anova": anova_btn,
                "cluster_frequent_keyword_subject": cluster_frequent_keyword_subject,
                "cluster_entropy": cluster_entropy, "distributions": distributions_btn
            }

            dict_table_data[cluster_id] = row


            result_list.append(row)
            index +=1

        table_data_json = {
            "data":result_list
        }
         
        dict_table_data_json = {
            "data":dict_table_data
        }

        cube_row_obj =  CUBE_Clustering_TableData(
            country = Country,
            algorithm_id = selected_algorithm_id,
            table_data = table_data_json,
            dict_table_data = dict_table_data_json,
            clusters_data = clusters_data
        )

        create_list.append(cube_row_obj)


    CUBE_Clustering_TableData.objects.bulk_create(create_list)

    end_t = time.time()
    print('Clusters-Cube created(' + str(end_t - start_t) + ').')