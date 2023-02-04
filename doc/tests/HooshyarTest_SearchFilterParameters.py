from django.test import TestCase
import requests

class SearchFilterParametersTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"

    def test_subject_filter(self):
        subject_id = "2"  #
        subject_name = "اقتصادی"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + subject_id + "/" + "0" + "/" \
                 + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "عنوان یا متن" + "/" + "empty" + "/" + "all" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        aggregations = response["aggregations"]
        field_data = aggregations['subject-agg']['buckets']

        self.assertTrue(req.ok)
        self.assertEqual(len(field_data), 1)
        self.assertEqual(field_data[0]['key'], subject_name)
        self.assertEqual(field_data[0]['doc_count'], total_hits)

    def test_year_filter(self):
        selected_year = "1401"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + selected_year + "/" + selected_year + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "عنوان یا متن" + "/" + "empty" + "/" + "all" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        aggregations = response["aggregations"]
        field_data = aggregations['approval-year-agg']['buckets']

        self.assertTrue(req.ok)
        self.assertEqual(len(field_data), 1)
        self.assertEqual(field_data[0]['key'], int(selected_year))
        self.assertEqual(field_data[0]['doc_count'], total_hits)

    def test_level_filter(self):
        level_id = "2"
        level_name = "قانون"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + level_id + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "عنوان یا متن" + "/" + "empty" + "/" + "all" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        aggregations = response["aggregations"]
        field_data = aggregations['level-agg']['buckets']

        self.assertTrue(req.ok)
        self.assertEqual(len(field_data), 1)
        self.assertEqual(field_data[0]['key'], (level_name))
        self.assertEqual(field_data[0]['doc_count'], total_hits)

    def test_type_filter(self):
        type_id = "2"
        type_name = "قانون"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + "0" + "/" + type_id + "/" \
                 + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "عنوان یا متن" + "/" + "empty" + "/" + "all" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        aggregations = response["aggregations"]
        field_data = aggregations['type-agg']['buckets']

        self.assertTrue(req.ok)
        self.assertEqual(len(field_data), 1)
        self.assertEqual(field_data[0]['key'], (type_name))
        self.assertEqual(field_data[0]['doc_count'], total_hits)

    def test_approval_reference_filter(self):
        approval_ref_id = "45"
        approval_ref_name = "هیات وزیران"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + approval_ref_id + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "عنوان یا متن" + "/" + "empty" + "/" + "all" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        aggregations = response["aggregations"]
        field_data = aggregations['approval-ref-agg']['buckets']

        self.assertTrue(req.ok)
        self.assertEqual(len(field_data), 1)
        self.assertEqual(field_data[0]['key'], (approval_ref_name))
        self.assertEqual(field_data[0]['doc_count'], total_hits)

    def test_place_filter(self):
        user_text = "جام جهانی"
        place = "عنوان"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + place + "/" + user_text + "/" + "exact" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        self.assertTrue(req.ok)
        self.assertEqual(1, total_hits)

    def test_AND_filter(self):
        user_text = "جام جهانی"
        place = "عنوان"

        my_url = self.base_url + "/SearchDocument_ES/" + "1" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + place + "/" + user_text + "/" + "and" + "/" \
                 + "1" + "/"
        req = requests.request("GET", my_url)
        response = req.json()
        total_hits = response["total_hits"]
        self.assertTrue(req.ok)
        self.assertEqual(1, total_hits)

    def test_GetSearchParameters(self):
        my_url = self.base_url + "/GetSearchParameters/1/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        self.assertIn("parameters_result", req.json())