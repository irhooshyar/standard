from django.test import TestCase
import requests

class ClusteringResultTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"

    def test_topics_count(self):
        cluster_count = "80"

        my_url = self.base_url + "/GetParagraph_Clusters/" + "1" + "/" \
                 + "K-Means" + "/" + "TF-IDF" + "/" \
                 + cluster_count + "/" + "(1, 1)" + "/" + "test_user" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        table_data = response["table_data"]
        clusters_data = response['clusters_data']

        res_topic_count = len(list(clusters_data.keys()))
        res_table_row_count = len(table_data)

        self.assertTrue(req.ok)
        self.assertTrue(res_topic_count, cluster_count)
        self.assertTrue(res_topic_count, res_table_row_count)

    def test_vocabulary_exist(self):
        min_terms_count = 20
        my_url = self.base_url + "/Get_Clustering_Vocabulary/" + "1" + "/" \
                 + "TF-IDF" + "/" + "(1, 1)" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        table_data = response['table_data']

        self.assertTrue(req.ok)
        self.assertGreater(len(table_data), min_terms_count)

    def test_centers_charts_data(self):
        cluster_count = 20
        my_url = self.base_url + "/Get_ClusterCenters_ChartData/" + "1" + "/" \
                 + "K-Means" + "/" + "TF-IDF" + "/" + str(cluster_count) + "/" + "(1, 1)" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        heatmap_chart_data = response['heatmap_chart_data']
        cluster_size_chart_data = response['cluster_size_chart_data']

        self.assertTrue(req.ok)
        self.assertEqual(len(heatmap_chart_data), cluster_count ** 2)
        self.assertEqual(len(cluster_size_chart_data), cluster_count)

    def test_discriminant_words_charts_data(self):
        discriminan_words_count = 10
        my_url = self.base_url + "/Get_ClusteringAlgorithm_DiscriminatWords_ChartData/" + "1" + "/" \
                 + "K-Means" + "/" + "TF-IDF" + "/" + "25" + "/" + "(1, 1)" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        anova_chart_data = response['anova_chart_data']
        decision_tree_chart_data = response['decision_tree_chart_data']

        self.assertTrue(req.ok)
        self.assertEqual(len(anova_chart_data), discriminan_words_count)
        self.assertEqual(len(decision_tree_chart_data), discriminan_words_count)

    def test_evaluation_charts_data(self):
        min_cluster_count = 5

        my_url = self.base_url + "/Get_ClusteringEvaluation_Silhouette_ChartData/" + "1" + "/" \
                 + "K-Means" + "/" + "TF-IDF" + "/" + "(1, 1)" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        silhouette_score_chart_data = response['silhouette_score_chart_data']
        elbow_inertia_chart_data = response['elbow_inertia_chart_data']

        self.assertTrue(req.ok)
        self.assertGreater(len(silhouette_score_chart_data), min_cluster_count)
        self.assertGreater(len(elbow_inertia_chart_data), min_cluster_count)

    def test_tag_cloud_chart_data(self):
        cluster_id = "1-KMS-5-(1, 1)-T-1"

        my_url = self.base_url + "/Get_Topic_TagCloud_ChartData/" + "1" + "/" \
                 + cluster_id + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        tag_cloud_chart_data = response['tag_cloud_chart_data']
        cloud_word_count = len(tag_cloud_chart_data)

        self.assertTrue(req.ok)

        my_url = self.base_url + "/GetParagraph_Clusters/" + "1" + "/" \
                 + "K-Means" + "/" + "TF-IDF" + "/" \
                 + "5" + "/" + "(1, 1)" + "/" + "test_user" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        clusters_data = response['clusters_data']
        cluster_word_count = len(clusters_data[cluster_id]['word_list'].split(' -'))

        self.assertTrue(req.ok)
        self.assertEqual(cluster_word_count, cloud_word_count)

    def test_cluster_paragraphs_count(self):
        topic_id = "1-KMS-5-(1, 1)-T-1"

        my_url = self.base_url + "/Get_Topic_Paragraphs_ES/" + "1" + "/" \
                 + topic_id + "/" + "100" + "/" + "1" + "/" + "1" + "/" + "0" + "/" + "0" + "/"

        req = requests.request("GET", my_url)

        response = req.json()

        total_hits = response["total_hits"]

        self.assertTrue(req.ok)

        my_url = self.base_url + "/GetParagraph_Clusters/" + "1" + "/" \
                 + "K-Means" + "/" + "TF-IDF" + "/" \
                 + "5" + "/" + "(1, 1)" + "/" + "test_user" + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        cluster_size = response["clusters_data"]["1-KMS-5-(1, 1)-T-1"]['cluster_size']

        self.assertTrue(req.ok)
        self.assertEqual(cluster_size, total_hits)

    def test_cluster_subjects_chart_data(self):
        topic_id = "1-KMS-5-(1, 1)-T-4"

        my_url = self.base_url + "/Get_Topic_Paragraphs_ES/" + "1" + "/" \
                 + topic_id + "/" + "100" + "/" + "1" + "/" + "0" + "/" + "1" + "/"

        req = requests.request("GET", my_url)
        response = req.json()

        total_hits = response["total_hits"]
        aggregations = response['aggregations']

        subject_data = aggregations['subject-agg']['buckets']

        para_sum = sum([column['doc_count'] for column in subject_data])

        self.assertTrue(req.ok)
        self.assertEqual(para_sum, total_hits)

    def test_cluster_year_chart_data(self):
        topic_id = "1-KMS-5-(1, 1)-T-4"

        my_url = self.base_url + "/Get_Topic_Paragraphs_ES/" + "1" + "/" \
                 + topic_id + "/" + "100" + "/" + "1" + "/" + "0" + "/" + "1" + "/"

        req = requests.request("GET", my_url)
        response = req.json()

        total_hits = response["total_hits"]
        aggregations = response['aggregations']

        approval_year_data = aggregations['approval-year-agg']['buckets']

        para_sum = sum([column['doc_count'] for column in approval_year_data])

        self.assertTrue(req.ok)
        self.assertEqual(para_sum, total_hits)

    def test_cluster_approval_ref_chart_data(self):
        topic_id = "1-KMS-5-(1, 1)-T-4"

        my_url = self.base_url + "/Get_Topic_Paragraphs_ES/" + "1" + "/" \
                 + topic_id + "/" + "100" + "/" + "1" + "/" + "0" + "/" + "1" + "/"

        req = requests.request("GET", my_url)
        response = req.json()

        total_hits = response["total_hits"]
        aggregations = response['aggregations']

        approval_references_data = aggregations['approval-ref-agg']['buckets']

        para_sum = sum([column['doc_count'] for column in approval_references_data])

        self.assertTrue(req.ok)
        self.assertEqual(para_sum, total_hits)

    def test_cluster_level_chart_data(self):
        topic_id = "1-KMS-5-(1, 1)-T-4"

        my_url = self.base_url + "/Get_Topic_Paragraphs_ES/" + "1" + "/" \
                 + topic_id + "/" + "100" + "/" + "1" + "/" + "0" + "/" + "1" + "/"

        req = requests.request("GET", my_url)
        response = req.json()

        total_hits = response["total_hits"]
        aggregations = response['aggregations']

        level_data = aggregations['level-agg']['buckets']

        para_sum = sum([column['doc_count'] for column in level_data])

        self.assertTrue(req.ok)
        self.assertEqual(para_sum, total_hits)

