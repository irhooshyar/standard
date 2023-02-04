from django.test import TestCase
import requests

class LDATopicExtractionTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"
    def test_AIGetLDATopic(self):
        country_id = "1"
        number_of_topic = "5"
        username = "test_user"

        my_url = self.base_url + "/AIGetLDATopic/" + country_id + "/" + number_of_topic + "/" + username + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertEqual(str(len(req.json()['lda_topics'])), number_of_topic)

    def test_AIGet_Topic_Centers_ChartData(self):
        country_id = "1"
        number_of_topic = "5"

        my_url = self.base_url + "/AIGet_Topic_Centers_CahrtData/" + country_id + "/" + number_of_topic + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertEqual(str(len(req.json()['cluster_size_chart_data'])), number_of_topic)

    def test_GetLDAKeywordGraphData(self):
        country_id = "1"
        number_of_topic = "5"

        my_url = self.base_url + "/GetLDAKeywordGraphData/" + country_id + "/" + number_of_topic + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        i = 0
        for node in req.json()['Nodes_data']:
            if node['node_type'] == "cluster":
                i += 1
        self.assertEqual(str(i), number_of_topic)

    def test_GetKeywordLDAData(self):
        country_id = "1"
        number_of_topic = "5"
        username = "test_user"
        node_name = "ملی"

        my_url = self.base_url + "/GetKeywordLDAData/" + country_id + "/" + number_of_topic + "/" + username + "/" + node_name + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        for cluster in req.json()['lda_topics']:
            self.assertIn(node_name, cluster['words'])

    def test_save_lda_topic_label(self):
        username = "test_user"
        topic_id = "2211"
        label = "برچسب تست"

        my_url = self.base_url + "/save_lda_topic_label/" + topic_id + "/" + username + "/" + label + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertEqual(".برچسب موضوع تغییر یافت", req.json()["result_response"])

    def test_AILDADocFromTopic(self):
        topic_id = "2211"

        my_url = self.base_url + "/AILDADocFromTopic/" + topic_id + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        keyword_list = req.json()['keywords'].split("-")
        self.assertEqual(20, len(keyword_list))

    def test_AILDAWordCloudTopic(self):
        topic_id = "2211"

        my_url = self.base_url + "/AILDAWordCloudTopic/" + topic_id + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertGreater(len(req.json()['Could_data']), 0)

    def test_AILDASubjectChartTopic(self):
        topic_id = "2211"

        my_url = self.base_url + "/AILDASubjectChartTopic/" + topic_id + "/";
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertGreater(int(req.json()['paragraph_count']), 0)

    def test_BoostingSearchParagraph_ES(self):
        country_id = "1"

        my_url = self.base_url + "/BoostingSearchParagraph_ES/" + country_id + "/1/10/"
        form_data = {'cluser_keyword_data': [",".join(["امضا", "5", "دیجیتال", "7"])],
                     'cluster_delete_data': [",".join(["ملی"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)

    def test_BoostingSearchParagraph_Column_ES(self):
        country_id = "1"
        field_name = "approval_reference_name.keyword"
        field_value = "نامشخص"

        my_url = self.base_url + "/BoostingSearchParagraph_Column_ES/" + country_id + "/" + field_name + "/" + field_value + "/1/10/"

        form_data = {'cluser_keyword_data': [",".join(["امضا", "5", "دیجیتال", "7"])],
                     'cluster_delete_data': [",".join(["ملی"])]}
        req = requests.post(my_url, data=form_data)
        self.assertTrue(req.ok)
        self.assertIn("total_hits", req.json())
        self.assertGreaterEqual(req.json()["total_hits"], 0)
