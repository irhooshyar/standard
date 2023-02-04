
from pathlib import Path
from hazm import *
import time
from abdal import config

from doc.models import Document, DocumentParagraphs,ClusterTopic, FeatureSelectionAlgorithm, FeatureSelectionResults,ParagraphsTopic,ClusteringAlorithm,ClusteringResults
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
from sklearn.feature_extraction.text  import TfidfVectorizer
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
from fcmeans import FCM
# --------------------------------

clustering_configs = {
    "فاوا":{
        "k":10,
        "batch_size":512
    },
    "هوش‌یار":{
        "k":35,
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

def Preprocessing(text, tokenize=True, stem=True, removeSW=True, normalize=True, removeSpecialChar=True):

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
            stopwords_list_1 = open(Path(config.BASE_PATH, "text_files/stopWords.txt"), encoding="utf8").read().split(
                "\n")

            stopwords_list_2 = open(Path(config.PERSIAN_PATH, "ClusteringCustomStopwords.txt"), encoding="utf8").read().split(
                "\n")


            stopwords_list = open(Path(config.PERSIAN_PATH, "TopicModeling_Stopwrods.txt"), encoding="utf8").read().split(
                "\n") + stopwords_list_1 + stopwords_list_2

            text = [word for word in text if word not in stopwords_list]

            # filtering
            text = [word for word in text if len(word) >= 2]

        # stemming
        if stem:
            text = [stemming(word) for word in text]

    return text


def FeatureExtraction(corpus):
    print('Running FeatureExtraction ...')

    vectorizer = TfidfVectorizer(max_df = 0.35
    , min_df = 0.01
    # ,ngram_range = (2,2)
    ,max_features = 10000
    )

    X = vectorizer.fit_transform(corpus)
    # print(f"X: {X}")

    tf_idf = pd.DataFrame(data = X.toarray(), columns=vectorizer.get_feature_names_out())

    final_df = tf_idf

    print("{} rows".format(final_df.shape))
    # print(final_df.T.nlargest(5, 1))

    return [vectorizer,final_df]


def run_FCM(k,data):

    model_results = {}

    numpy_array_data = data.to_numpy()  ## X, numpy array. rows:samples columns:features

    my_model = FCM(n_clusters=k
                    , n_init = 10
                    , tol = 0.0001
                    , fuzzifier=2
                    , random_state = 1)

    fcm_result = my_model.fit(numpy_array_data)

    centers = my_model.centers
    labels = my_model.predict(numpy_array_data)

    model_results['centers'] = centers
    model_results['labels'] = labels

    return model_results




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



    
def save_topics_to_db(Country,dfs):
    print("save_topics_to_db")
    i = 0
    create_list = []

    for cluster in dfs:
        word_dict = {}

        for index,row in cluster.iterrows():

            word = row['features']
            score = row['score']

            word_dict[word] = str(round(score,4))

        i += 1

        topic_name = f"C{i}"

        # print(f"Cluster {i}:")
        # print(word_dict)

        # print("===================================")

        topic_id = str(Country.id) + "-KMS-T-"+str(i)

        algorithm_obj = ClusteringAlorithm.objects.get(name = "K-Means",
        input_vector_type = "TF-IDF")

        topic_obj = ClusterTopic(country=Country,id = topic_id, name=topic_name, words=word_dict,
            algorithm = algorithm_obj)
        
        create_list.append(topic_obj)

    ClusterTopic.objects.bulk_create(create_list)
    
    print(f"{len(create_list)} created.")



def create_corpus(Country):

    corpus = []

    selected_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id = Country.id
        # ,document_id__type_name = 'قانون'
    ).values()

    selected_para_count = len(selected_paragraphs)
    para_count = 0
    para_id_list = []

    i = 1
    for para in selected_paragraphs[:]:
        para_text = para['text']

        if len(para_text) > 80:
            para_count += 1

            para_text = LocalPreprocessing(para_text)

            para_token_list = Preprocessing(para_text, stem=False)
            
            new_para_text = " ".join(para_token_list)
            corpus.append(new_para_text)

            para_id_list.append(para['id'])

        print(f"{i}/{selected_para_count}")
        i += 1

    print(f"{para_count} paragraphs.")
    
    return [corpus,para_id_list]

def apply(folder_name, Country):
    start_t = time.time()

    #------ Gloabal Varriables -------------------
    corpus = []
    country_name = Country.name
    k =  clustering_configs[country_name]['k']

    algorithm_obj = ClusteringAlorithm.objects.get(name = "K-Means",
    input_vector_type = "TF-IDF")

    fs_algorithm_obj = FeatureSelectionAlgorithm.objects.get(name = "ANOVA")


    # ------------- Clean Tables -------------

    ClusterTopic.objects.filter(country = Country).delete()
    ParagraphsTopic.objects.filter(country = Country).delete()
    ClusteringResults.objects.filter(country = Country).delete()
    FeatureSelectionResults.objects.filter(
        country = Country,
        algorithm = fs_algorithm_obj
    ).delete()

    #------ create corpus -----------------------------------

    [corpus,para_id_list] = create_corpus(Country)

    #------ feature extraction -----------------------------------
    
    f_result = FeatureExtraction(corpus)
    vectorizer = f_result[0]
    final_df = f_result[1]

    #------- Running Kmeans --------------------------------------

    model_result = run_FCM(k,final_df)

    prediction = model_result['labels']
    labels = model_result['labels'] 
    centers = model_result['centers']

    #----------- Save Topics ---------------------------------

    
    n_feats = 20
    final_df_array = final_df.to_numpy()
    dfs = get_top_features_cluster(final_df_array, prediction, n_feats,vectorizer)

    save_topics_to_db(Country,dfs)
    save_para_topics(Country,para_id_list,labels)

    # --------- Save Clustering Results --------------------------------
    centroids = pd.DataFrame(centers)
    centroids.columns = final_df.columns

    distance_array = euclidean_distances(centers)
    heatmap_chart_data =  create_heatmap_data(distance_array)

    
    ClusteringResults.objects.create(
        country = Country,
        algorithm = algorithm_obj,
        heatmap_chart_data = {"data":heatmap_chart_data},
    )

    end_t = time.time()
    print('Clusters created(' + str(end_t - start_t) + ').')


    #--------- ANOVA -------------------------
    y = ["C"+str(c_number + 1) for c_number in labels]

    important_features_chart_data = ANOVA_feature_selection(y,final_df,vectorizer,10)

    FeatureSelectionResults.objects.create(
        country = Country,
        algorithm = fs_algorithm_obj,
        important_words_chart_data = {"data":important_features_chart_data}
    )


    print("============== Saving DT DataFrame ====================")
    # create_decision_tree(final_df,labels)

    final_df['y'] = y


    # import scipy.stats as stats

    # fvalue, pvalue = stats.f_oneway(final_df['اقتصاد'], final_df['شماره'], final_df['فصل'], final_df['فضای'])
    # print(fvalue, pvalue)


    final_df_file = str(Path(config.DECISION_TREE_PATH, folder_name,'final_df_file.csv'))

    final_df.to_csv(final_df_file,index=False, sep=';', encoding='utf32')

    decision_tree_configs = {
        "max_depth":int(clustering_configs[country_name]['k']/2),
        "generate_structure_1":True,
        "generate_structure_2":True
        
    }

    CreateDecisionTree.apply(folder_name,Country, decision_tree_configs,final_df)




    #--------- Plotting Silhouette Analysis -------------------------

    # best_result = silhouette(algorithm_results, final_df, plot=False)

    # best_silhouete = best_result[0]
    # best_cluster_count = best_result[1]

    # print(f"Best Cluster Count: {best_cluster_count}:{best_silhouete}")

    # -----------------------------------------------------




def ANOVA_feature_selection(y,final_df,vectorizer,num_of_features):

    # ANOVA feature selection for numeric input and categorical output
    from sklearn.datasets import make_classification
    from sklearn.feature_selection import SelectKBest
    from sklearn.feature_selection import f_classif
    from numpy import array
    from doc.models import FeatureSelectionAlgorithm

    important_features_chart_data = []

    # define feature selection
    fs = SelectKBest(score_func=f_classif, k=num_of_features)

    # apply feature selection

    X_selected2 = fs.fit(final_df, y)

    scores = X_selected2.scores_

    filter = fs.get_support()
    features = array(vectorizer.get_feature_names_out())
    
    # print("All features:")
    # print(features)
    
    print(f"Selected best {num_of_features}:")
    selected_features = features[filter]
    selected_scores = scores[filter]

    sum_score = sum(selected_scores)


    feat_score_dict = {}
    for i in range(len(selected_features)):
        feat_score_dict[selected_features[i]] = round((selected_scores[i]/sum_score)*100,2)

    
    sorted_feat_score_list = sorted(feat_score_dict.items(), key=lambda k: k[1], reverse=True)

    j = 0
    for feat_score in sorted_feat_score_list:
        j += 1
        print(f"{j}. {feat_score[0]}, {feat_score[1]}")

        feature_name = feat_score[0]
        feature_score = feat_score[1]

        important_features_chart_data.append([feature_name,feature_score])


    return important_features_chart_data


def create_decision_tree(final_df, labels):

    x = final_df # raw_data.drop('Kyphosis', axis = 1)
    y = ["C"+str(c_number + 1) for c_number in labels]

    
    x_training_data, x_test_data, y_training_data, y_test_data = train_test_split(
        x, y, test_size = 0.3,random_state=1)

    model = DecisionTreeClassifier(
        min_samples_leaf = 0.02
        ,max_depth=5)

    model.fit(x_training_data, y_training_data)
    predictions = model.predict(x_test_data)


    # print(classification_report(y_test_data, predictions))
    # print(confusion_matrix(y_test_data, predictions))
    print("Test-Accuracy:",str(accuracy_score(y_test_data, predictions)))

    text_representation = tree.export_text(model,feature_names = final_df.columns.tolist())
    print(text_representation)

    
    # plt.figure()
    # plot_tree(model, filled=True)
    # plt.title("Decision tree trained on all the features")
    # plt.show()




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

            block = {"x":x_value,"y":y_value,"heat":round(col,3)}
            chart_data.append(block)

    return chart_data

def save_para_topics(Country,para_id_list,labels):
    print("save_para_topics")
    create_list = []
    batch_size = 10000

    para_count = len(para_id_list)

    for i in range(0,len(para_id_list)):
        para_id = para_id_list[i]

        topic_id = str(Country.id) + "-KMS-T-"+str(labels[i] + 1)

        para_topic_obj = ParagraphsTopic(country = Country, paragraph_id=para_id, topic_id = topic_id)
        
        create_list.append(para_topic_obj)
        # print(f"{i}/{para_count} added.")


        if create_list.__len__() > batch_size:
            ParagraphsTopic.objects.bulk_create(create_list)
            create_list = []


    ParagraphsTopic.objects.bulk_create(create_list)


