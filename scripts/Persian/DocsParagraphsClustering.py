
from pathlib import Path
from hazm import *
import time
from abdal import config
from django.db.models import Count

from doc.models import Document,DocumentParagraphs,\
    ClusterTopic,ParagraphsTopic,ClusteringAlorithm,ClusteringResults, \
    FeatureSelectionAlgorithm, FeatureSelectionResults,\
    TopicDiscriminantWords,ParagraphsSubject,ClusteringEvaluationResults, \
        UserTopicLabel,ParagraphsFeatures
from es_scripts import IngestClusteringParagraphsToElastic

from hazm import sent_tokenize, Normalizer
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaMulticore
from collections import Counter
import math
import numpy as np
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering

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
from sklearn.metrics.pairwise import euclidean_distances,cosine_similarity
from sklearn.metrics.pairwise import distance_metrics
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix,accuracy_score
from sklearn import tree
from sklearn.tree import plot_tree

from sklearn.cluster import MiniBatchKMeans

from . import CreateDecisionTree
from . import DocsParagraphsClusteringCubeData,ClusteringGraphData
# --------------------------------

clustering_configs = {
    "اسناد رهبری":{
        "min_k":5,
        "max_k":15,
        "step":5,
        "batch_size":512,
        "ngram_types":[(2,2)]
    },
    "فاوا":{
        "min_k":5,
        "max_k":20,
        "step":5,
        "batch_size":512,
        "ngram_types":[(1,1)]
    },
    "هوش‌یار":{
        "min_k":5,
        "max_k":50,
        "step":5,
        "batch_size":4096,
        "ngram_types":[(1,1)]

    }
}

clustering_configs_2 = {
    "اسناد رهبری":{
        "min_k":60,
        "max_k":100,
        "step":10,
        "batch_size":512,
        "ngram_types":[(1,1)]
    },
    "فاوا":{
        "min_k":25,
        "max_k":25,
        "step":1,
        "batch_size":512,
        "ngram_types":[(1,1)]

    },
    "هوش‌یار":{
        "min_k":60,
        "max_k":100,
        "step":10,
        "batch_size":4096,
        "ngram_types":[(1,1)]

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


def save_stopwords(stopwrod_list):
    f = open("all_stopwrods.txt", "w",encoding="utf8")

    i = 0
    for sw in stopwrod_list:
        i+=1
        if i < len(stopwrod_list):
            sw = sw+"\n"
       
        f.write(sw)
    
    f.close()


def FeatureExtraction(corpus,ngram_type):
    from sklearn.preprocessing import MaxAbsScaler,StandardScaler

    print('Running FeatureExtraction ...')

    min_df = 0.01
    max_df = 0.35 # default
    # max_df = .20
    if ngram_type == (2,2):
        min_df = 0.005
    
    
    vectorizer = TfidfVectorizer(
    max_df = max_df
    , min_df = min_df
    ,ngram_range = ngram_type

    )



    X = vectorizer.fit_transform(corpus)
    # print(f"X: {X}")



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


def get_top_features_cluster(tf_idf_array, prediction, n_feats,features):
    print("Running get_top_features_cluster ...")

    labels = np.unique(prediction)
    dfs = []
    for label in labels:
        id_temp = np.where(prediction==label) # indices for each cluster
        x_means = np.mean(tf_idf_array[id_temp], axis = 0) # returns average score across cluster

        sorted_means = np.argsort(x_means)[::-1][:n_feats] # indices with top 20 scores
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



    
def save_topics_to_db(Country,dfs,algorithm_obj):
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


        algorithm_abbr = algorithm_obj.abbreviation

        topic_id = str(Country.id) + "-" + algorithm_abbr + "-"  +str(i)
        topic_id_list.append(topic_id)



        topic_obj = ClusterTopic(country=Country,id = topic_id, name=topic_name, words=word_dict,
            algorithm = algorithm_obj)
        
        create_list.append(topic_obj)

    ClusterTopic.objects.bulk_create(create_list)
    
    return topic_id_list
    print(f"{len(create_list)} created.")

def clean_tables(Country,size_to_id_dict):
    clustering_algorithm_ids = []

    for size,info in size_to_id_dict.items():
        for ngram,algo_obj in info.items():
            clustering_algorithm_ids.append(algo_obj.id)

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

    ClusteringEvaluationResults.objects.filter(
        country = Country,
        name = 'K-Means',
        input_vector_type = "TF-IDF",
        ngram_type__in = [str(ngram) for ngram in NGRAM_TYPES]
    ).delete()

    UserTopicLabel.objects.filter(
        topic__country__id = Country.id,
        topic__algorithm__id__in = clustering_algorithm_ids).delete()


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

    if Country.name not in  ['فاوا' , 'اسناد رهبری'] :

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



# ----------------- Dendrogram -----------------------------------------

def save_dendrogram(folder_name,tf_idf_matrix,ngram_type):

    # setting distance_threshold=0 ensures we compute the full tree.
    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)

    # model = AgglomerativeClustering(n_clusters=6,compute_distances=True,
    # affinity="cosine",linkage="average")

    model = model.fit(tf_idf_matrix)
    plt.title("Hierarchical Clustering Dendrogram")
    
    # plot the top three levels of the dendrogram
    plot_dendrogram(model, truncate_mode="level", p=5)
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    # plt.show()

    fig = plt.gcf()
    # fig.set_size_inches(18.5, 10.5)
    fig.set_size_inches(13.6, 6.5)

    Create_Folder(config.DENDROGRAM_PATH)

    dendo_file_name = folder_name + "_" + str(ngram_type) +'_dendrogram.png'
    dendo_file_path = str(Path(config.DENDROGRAM_PATH,dendo_file_name))


    fig.savefig(dendo_file_path,dpi=100,bbox_inches='tight')

def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


def scipy_dendrogram(cluster_df):
    # Dendogram for Heirarchical Clustering
    import scipy.cluster.hierarchy as shc
    from matplotlib import pyplot
    pyplot.figure(figsize=(10, 7))  
    pyplot.title("Dendrograms")  
    pyplot.show()
    dend = shc.dendrogram(shc.linkage(cluster_df, method='ward'))


def create_dendrogram(folder_name, Country,ngram_type):

    [corpus,para_id_list,paragraph_subject_dict] = create_corpus(Country)
    f_result = FeatureExtraction(corpus,ngram_type)
    tf_idf_matrix = f_result[1]

    # scipy_dendrogram(tf_idf_matrix)

    save_dendrogram(folder_name,tf_idf_matrix,ngram_type)

# -----------------------------------------------------------------------

def get_vocabulary(Country,ngram_type):

    ParagraphsFeatures.objects.filter(
            country = Country,ngram_type = str(ngram_type)).delete()

    [corpus,para_id_list,paragraph_subject_dict] = create_corpus(Country)

    f_result = FeatureExtraction(corpus,ngram_type)
    
    vectorizer = f_result[0]
    idf = vectorizer.idf_ 
    vocabulary = vectorizer.vocabulary_ 

    IDF_Matrix = {}
    for term,index in vocabulary.items():
         IDF_Matrix[term] = round(idf[index],3)
        
    sorted_IDF_Matrix = sorted(IDF_Matrix.items(), key=lambda x:x[1],reverse=True)


    ParagraphsFeatures.objects.create(
        country = Country,
        feature_extractor = "TF-IDF",
        features = sorted_IDF_Matrix,
        ngram_type = ngram_type
    )


NGRAM_TYPES = [(2,2)]


def apply(folder_name, Country):

    for ngram in NGRAM_TYPES:

        get_vocabulary(Country,ngram)
        
        if Country.name == "فاوا":
            create_dendrogram(folder_name, Country,ngram)


    kmeans_clustering(folder_name, Country)

    # agglomerative_clustering(folder_name,Country)

    # ---- Create Cube Data ---------------------------
    Country.status = "DocsParagraphsClusteringCubeData"
    Country.save()

    DocsParagraphsClusteringCubeData.apply(folder_name,Country)

    # ---- Create Graph Data ---------------------------

    Country.status = "ClusteringGraphData"
    Country.save()

    ClusteringGraphData.apply(Country)

    # ---- Ingest paragraphs topic ---------
    
    Country.status = "IngestClusteringParagraphsToElastic"
    Country.save()    
    IngestClusteringParagraphsToElastic.apply(folder_name,Country)

    # ---------------- end of apply -------------------
    Country.status = "Done"
    Country.save()


def run_Agglomerative(n_clusters,data):

    from sklearn.cluster import AgglomerativeClustering
    agg_model = AgglomerativeClustering(n_clusters=n_clusters,
    linkage = "ward",
    compute_distances = True)

    return agg_model


def agglomerative_clustering(folder_name,Country):
    print("agglomerative_clustering started:")
    start_t = time.time()

    silhouette_avg_dict = {}

    #------ Gloabal Varriables -------------------
    country_name = Country.name

    corpus = []
    paragraph_subject_dict = {}

    fs_algorithm_obj = FeatureSelectionAlgorithm.objects.get(name = "ANOVA")

    #------ Clustering Configs -------------------

    configs_list = [clustering_configs,clustering_configs_2]

    #------ create corpus -----------------------------------

    [corpus,para_id_list,paragraph_subject_dict] = create_corpus(Country)


    for selected_config in configs_list:

        country_clustering_configs = selected_config[country_name]
        
        min_k = country_clustering_configs['min_k']
        max_k = country_clustering_configs['max_k']
        step = country_clustering_configs['step']
        ngram_types = country_clustering_configs['ngram_types']

        SIZE_TO_ID = {}

        for k in range(min_k,max_k+1,step):
            SIZE_TO_ID[k] = {}
            for ngram in ngram_types:

                algorithm_obj= ClusteringAlorithm.objects.get(name = "Agglomerative",
                input_vector_type = "TF-IDF",cluster_count = k,ngram_type = str(ngram))

                SIZE_TO_ID[k][ngram] = algorithm_obj

        # --------------- clean tables ------------------------------

        clean_tables(Country,SIZE_TO_ID)
        
        #------- Running Kmeans --------------------------------------


        for k in range(min_k,max_k+1,step):
            silhouette_avg_dict[k] = {}
            for ngram in ngram_types:

                print(f"current k: {k}")
                c_algorithm_obj = SIZE_TO_ID[k][ngram]
                c_algorithm_id = c_algorithm_obj.id
                c_algorithm_abb = c_algorithm_obj.abbreviation


            #------ feature extraction -----------------------------------
            
            f_result = FeatureExtraction(corpus)
            vectorizer = f_result[0]
            final_df = f_result[1]

            features =  vectorizer.get_feature_names_out()

            # ------- Run ---------------

            agg_model = run_Agglomerative(k, final_df)

            fitted_agg_model = agg_model.fit(final_df)
            prediction = agg_model.fit_predict(final_df)

            # unique_labels = np.unique(prediction)

            labels = fitted_agg_model.labels_ 

            silhouette_avg = silhouette_score(final_df, labels)
            silhouette_avg = round(silhouette_avg,3)
            silhouette_avg_dict[k][ngram] = silhouette_avg


            #----------- Save Topics ---------------------------------
            # best_cluster_count = k
            # kmeans = kmeans_results.get(best_cluster_count)
            
        
            final_df_array = final_df.to_numpy()
            

            n_feats = 20
            dfs = get_top_features_cluster(final_df_array, prediction, n_feats,features)

            topic_id_list = save_topics_to_db(Country,dfs,c_algorithm_obj)
            save_para_topics(Country,para_id_list,paragraph_subject_dict,labels,c_algorithm_abb)
            update_topics_frequent_subject_entropy(Country.id,topic_id_list)
        
            # --------- Save Clustering Results --------------------------------


            heatmap_chart_data =  []

            similarity_chart_data = []

            cluster_size_chart_data = create_cluster_size_chart_data(topic_id_list)

            ClusteringResults.objects.create(
                country = Country,
                algorithm_id = c_algorithm_id,
                heatmap_chart_data = {"data":heatmap_chart_data},
                similarity_chart_data = {"data":similarity_chart_data},
                cluster_size_chart_data = {"data":cluster_size_chart_data},
                silhouette_score = silhouette_avg
            )

            end_t = time.time()
            print('Clusters created(' + str(end_t - start_t) + ').')


            #--------- ANOVA -------------------------
            y = ["C"+str(c_number + 1) for c_number in labels]

            important_features_chart_data = ANOVA_feature_selection(y,final_df,features,10)

            FeatureSelectionResults.objects.create(
                country = Country,
                c_algorithm_id = c_algorithm_id,
                f_algorithm = fs_algorithm_obj,
                important_words_chart_data = {"data":important_features_chart_data}
            )

            ANOVA_one_versus_all(Country,final_df,features,10,labels,fs_algorithm_obj,c_algorithm_abb)

            # ============== Saving DT DataFrame ====================
            
            # create_decision_tree(final_df,labels)

            final_df['y'] = y

            decision_tree_configs = {
                "max_depth":int(k),
                "generate_structure_1":True,
                "generate_structure_2":True
                
            }

            Create_Folder(config.DECISION_TREE_PATH,folder_name)

            CreateDecisionTree.apply(folder_name,Country, decision_tree_configs,c_algorithm_id,final_df)



    # ---- Calculate Silhouette & Elbow Data ---------------------------

    # calculate_silhouette_elbow_data(Country,silhouette_avg_dict,inertias_mapping)



def kmeans_clustering(folder_name, Country):
    print('kmeans_clustering started:')
    start_t = time.time()

    silhouette_avg_dict = {}

    #------ Gloabal Varriables -------------------
    country_name = Country.name

    corpus = []
    paragraph_subject_dict = {}

    fs_algorithm_obj = FeatureSelectionAlgorithm.objects.get(name = "ANOVA")

    inertias_mapping = {} # for elbow

    #------ Clustering Configs -------------------

    configs_list = [clustering_configs]

    #------ create corpus -----------------------------------

    [corpus,para_id_list,paragraph_subject_dict] = create_corpus(Country)


    for selected_config in configs_list:

        country_clustering_configs = selected_config[country_name]
        
        min_k = country_clustering_configs['min_k']
        max_k = country_clustering_configs['max_k']
        step = country_clustering_configs['step']
        ngram_types = country_clustering_configs['ngram_types']

        SIZE_TO_ID = {}

        for k in range(min_k,max_k+1,step):
            SIZE_TO_ID[k] = {}
            for ngram in ngram_types:

                algorithm_obj= ClusteringAlorithm.objects.get(name = "K-Means",
                input_vector_type = "TF-IDF",cluster_count = k,ngram_type = str(ngram))

                SIZE_TO_ID[k][ngram] = algorithm_obj

        # --------------- clean tables ------------------------------

        clean_tables(Country,SIZE_TO_ID)
        
        #------- Running Kmeans --------------------------------------


        for k in range(min_k,max_k+1,step):
            silhouette_avg_dict[k] = {}
            inertias_mapping[k] = {}

            for ngram in ngram_types:

                print(f"current k: {k}")
                c_algorithm_obj = SIZE_TO_ID[k][ngram]
                c_algorithm_id = c_algorithm_obj.id
                c_algorithm_abb = c_algorithm_obj.abbreviation


                #------ feature extraction -----------------------------------
                
                f_result = FeatureExtraction(corpus,ngram)
                vectorizer = f_result[0]
                final_df = f_result[1]

                features =  vectorizer.get_feature_names_out()

                # ------- Run ---------------
                kmeanModel = run_KMeans(k, final_df,country_clustering_configs)

                prediction = kmeanModel.predict(final_df)


                # unique_labels = np.unique(prediction)


                labels = kmeanModel.labels_ 
                centroids = pd.DataFrame(kmeanModel.cluster_centers_)
                centroids.columns = final_df.columns
                silhouette_avg = silhouette_score(final_df, labels)
                silhouette_avg = round(silhouette_avg,3)
                silhouette_avg_dict[k][ngram] = silhouette_avg


                #----------- Save Topics ---------------------------------
                # best_cluster_count = k
                # kmeans = kmeans_results.get(best_cluster_count)
                
            
                final_df_array = final_df.to_numpy()
                
                calculate_elbow_data(kmeanModel,final_df_array,k,inertias_mapping,ngram)

                n_feats = 20
                dfs = get_top_features_cluster(final_df_array, prediction, n_feats,features)

                topic_id_list = save_topics_to_db(Country,dfs,c_algorithm_obj)
                save_para_topics(Country,para_id_list,paragraph_subject_dict,labels,c_algorithm_abb)
                update_topics_frequent_subject_entropy(Country.id,topic_id_list)
            
                # --------- Save Clustering Results --------------------------------


                distance_array = euclidean_distances(kmeanModel.cluster_centers_)
                heatmap_chart_data =  create_heatmap_data(distance_array)

                similarity_array = cosine_similarity(kmeanModel.cluster_centers_)
                similarity_chart_data =  create_heatmap_data(similarity_array)

                cluster_size_chart_data = create_cluster_size_chart_data(topic_id_list)

                ClusteringResults.objects.create(
                    country = Country,
                    algorithm_id = c_algorithm_id,
                    heatmap_chart_data = {"data":heatmap_chart_data},
                    similarity_chart_data = {"data":similarity_chart_data},
                    cluster_size_chart_data = {"data":cluster_size_chart_data},
                    # silhouette_score = silhouette_avg
                )

                end_t = time.time()
                print('Clusters created(' + str(end_t - start_t) + ').')


                #--------- ANOVA -------------------------
                y = ["C"+str(c_number + 1) for c_number in labels]

                important_features_chart_data = []
                important_features_chart_data = ANOVA_feature_selection(y,final_df,features,10)


                FeatureSelectionResults.objects.create(
                    country = Country,
                    c_algorithm_id = c_algorithm_id,
                    f_algorithm = fs_algorithm_obj,
                    important_words_chart_data = {"data":important_features_chart_data}
                )

                ANOVA_one_versus_all(Country,final_df,features,10,labels,fs_algorithm_obj,c_algorithm_abb)

                # ============== Saving DT DataFrame ====================
                
                # create_decision_tree(final_df,labels)

                final_df['y'] = y

                decision_tree_configs = {
                    "max_depth":int(k),
                    "generate_structure_1":True,
                    "generate_structure_2":True
                    
                }

                Create_Folder(config.DECISION_TREE_PATH,folder_name)

                CreateDecisionTree.apply(folder_name,Country, decision_tree_configs,c_algorithm_id,final_df)



    # ---- Calculate Silhouette & Elbow Data ---------------------------

    calculate_silhouette_elbow_data(Country,silhouette_avg_dict,inertias_mapping)


# -- Silhouette & Elbow ---------------------------------

def calculate_silhouette_elbow_data(Country,silhouette_avg_dict,inertias_mapping):


    silhouette_score_chart_data = []
    elbow_inertia_chart_data = []

    eval_result_create_list = []

    for ngram in NGRAM_TYPES:
        
        silhouette_score_chart_data = []
        elbow_inertia_chart_data = []

        for k, data in silhouette_avg_dict.items():
            score = data[ngram]
            silhouette_score_chart_data.append([k,score])
        
        for k, data in inertias_mapping.items():
            dist = data[ngram]
            elbow_inertia_chart_data.append([k,round(dist,3)])

        row_obj = ClusteringEvaluationResults(
            name = "K-Means",
            input_vector_type = "TF-IDF",
            ngram_type = str(ngram),
            country = Country,
            silhouette_score_chart_data = silhouette_score_chart_data,
            elbow_inertia_chart_data = elbow_inertia_chart_data
        )
        eval_result_create_list.append(row_obj)



    ClusteringEvaluationResults.objects.bulk_create(eval_result_create_list)

def calculate_elbow_data(kmeanModel,X,k,inertias_mapping,ngram):

    from scipy.spatial.distance import cdist
    distortions = []

    # distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_,
    #                                     'euclidean'), axis=1)) / X.shape[0])
  
    # distortions_mapping[k][ngram] = sum(np.min(cdist(X, kmeanModel.cluster_centers_,
    #                                'euclidean'), axis=1)) / X.shape[0]

    inertias = []
 
    inertias.append(kmeanModel.inertia_)
    inertias_mapping[k][ngram] = kmeanModel.inertia_



# -- Centroid Charts ---------------------------------

def create_cluster_size_chart_data(topic_id_list):
    import collections
    cluster_size_chart_data = []


    start_t = time.time()
    print('update cluster-size chart data  started:')

    topic_name_list = ParagraphsTopic.objects.filter(topic__id__in = topic_id_list).values_list('topic__name',flat = True)
    frequency_dict = collections.Counter(topic_name_list)

    for topic_name,count in frequency_dict.items():
        cluster_size_chart_data.append([topic_name,count])

    end_t = time.time()        
    print('cluster-size chart data updated (' + str(end_t - start_t) + ').')

    return cluster_size_chart_data

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


# ------ ANOVA ---------------------------------

def ANOVA_one_versus_all(Country,final_df,features,num_of_feature,original_labels,fs_algorithm_obj,algo_abbreviation):
    batch_size = 1000
    create_list = []

    unique_labels = set(original_labels)
    k = len(unique_labels)

    print("unique_labels")
    print(unique_labels)

    for selected_cluster_number in unique_labels:
    
        new_labels = [label if label == selected_cluster_number else -1 for label in original_labels ]

        y = ["C"+str(c_number + 1) if c_number != -1 else "NOT_C"+str(selected_cluster_number + 1) for c_number in new_labels]
        print(set(y))

        important_features_chart_data = ANOVA_feature_selection(y,final_df,features,num_of_feature)
        topic_id = str(Country.id) + "-" + algo_abbreviation+ "-" + str(int(selected_cluster_number + 1))
        

        row_obj= TopicDiscriminantWords(country = Country,topic_id = topic_id,
        f_algorithm = fs_algorithm_obj,
        discriminant_words_chart_data = {"data":important_features_chart_data})


        create_list.append(row_obj)
        # print(f"{i}/{para_count} added.")


        if create_list.__len__() > batch_size:
            TopicDiscriminantWords.objects.bulk_create(create_list)
            create_list = []


    TopicDiscriminantWords.objects.bulk_create(create_list)

def ANOVA_feature_selection(y,final_df,features,num_of_features):

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
    pvalues = X_selected2.pvalues_

    temp = [round(p,4) for p in pvalues if p < 0.05]
    print(len(pvalues))
    print(len(temp))

    filter = fs.get_support()
    features = array(features)
    
    # print("All features:")
    # print(features)
    
    print(f"Selected best {num_of_features}:")
    selected_features = features[filter]
    selected_scores = scores[filter]
    selected_pvalues = pvalues[filter]

    if np.inf in selected_scores:

        max_score = max([s for s in selected_scores if not np.isinf(s)])

        for i in range(len(selected_scores)):
            if np.isinf(selected_scores[i]):
                selected_scores[i] = 2*max_score

    sum_score = sum(selected_scores)

    print('selected_scores= '+str(selected_scores))


    feat_score_dict = {}
    for i in range(len(selected_features)):
        # feat_score_dict[selected_features[i]] = [round((selected_scores[i]/sum_score)*100,4),round(selected_pvalues[i],4)]
        
        
        feat_score_dict[selected_features[i]] = round((selected_scores[i]/sum_score)*100,4)

        
        if np.isinf(feat_score_dict[selected_features[i]]):
            feat_score_dict[selected_features[i]] = max_score
    
    sorted_feat_score_list = sorted(feat_score_dict.items(), key=lambda k: k[1], reverse=True)

    j = 0
    for feat_score in sorted_feat_score_list:
        j += 1
        print(f"{j}. {feat_score[0]}, {feat_score[1]}")

        feature_name = feat_score[0]
        feature_score = feat_score[1]

        important_features_chart_data.append([feature_name,feature_score])


    return important_features_chart_data

def entropy(array):
    total_entropy = 0
    s = sum(array)

    for i in array:
        pi = (i/s)
        if i != 0:
            total_entropy += -pi * math.log(pi, 2)

    return total_entropy


# -- Decision Tree ---------------------------------

def Create_Folder(source_path, folder_name=None):

    import os
    from scripts.Persian import FolderCreator

    if not os.path.isdir(source_path):
        os.mkdir(source_path)

    if folder_name is not None:

        folder_path = str(Path(source_path, folder_name))
        FolderCreator.apply(folder_path)

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


# -- Save to DB ---------------------------------

def update_topics_frequent_subject_entropy(country_id,topic_id_list):
    batch_size = 10000

    start_t = time.time()
    print('update cluster-topic fields started:')

    topic_objects = ClusterTopic.objects.filter(id__in = topic_id_list)

    for topic in topic_objects:
        topic_id = topic.id
        res_query = ParagraphsTopic.objects.filter(country__id =country_id,topic__id = topic_id ).values_list('keyword_subject').annotate(keyword_subject_count=Count('keyword_subject')).order_by('-keyword_subject_count')
        list_of_subject_counts = res_query.values_list('keyword_subject_count',flat = True)
        frequent_keyword_subject = res_query[0][0] # [(subject,count),(),...]  
        topic.frequent_keyword_subject = frequent_keyword_subject
        
        try:
            second_frequent_keyword_subject = res_query[1][0] # [(subject,count),(),...]
            topic.second_frequent_keyword_subject = second_frequent_keyword_subject
        except:
            pass
        topic.entropy = round(entropy(list_of_subject_counts), 2)

    ClusterTopic.objects.bulk_update(
        topic_objects,['frequent_keyword_subject','entropy','second_frequent_keyword_subject'],batch_size) 

    end_t = time.time()        
    print('ClusterTopic fields updated (' + str(end_t - start_t) + ').')

def save_para_topics(Country,para_id_list,paragraph_subject_dict,labels,algo_abbreviation):
    print("save_para_topics")
    create_list = []
    batch_size = 10000



    para_count = len(para_id_list)

    for i in range(0,len(para_id_list)):
        para_id = para_id_list[i]

    # if (labels[i] + 1) in unique_labels:
        topic_id = str(Country.id) + "-" + algo_abbreviation + "-" + str(int(labels[i] + 1))
        
        keyword_subject = paragraph_subject_dict[para_id] if para_id in paragraph_subject_dict else 'نامشخص'

        para_topic_obj = ParagraphsTopic(
            country = Country,
             paragraph_id=para_id,
              topic_id = topic_id,
              keyword_subject = keyword_subject)
        

        create_list.append(para_topic_obj)
        # print(f"{i}/{para_count} added.")


        if create_list.__len__() > batch_size:
            ParagraphsTopic.objects.bulk_create(create_list)
            create_list = []


    ParagraphsTopic.objects.bulk_create(create_list)

