from django.test import TestCase
import requests

class SearchActorsTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"

    def test_actor_count_filter(self):
        place = "عنوان یا متن"
        search_type = "exact"
        text = "تنوع زیستی"

        my_url = self.base_url + "/GetActorsChartData_ES_2/" + "1" + "/" + "0" \
                 + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "0" + "/" + "0" + "/" \
                 + "0" + "/" + "0" + "/" \
                 + "0" + "/" + place + "/" + text + "/" + search_type + "/"

        req = requests.request("GET", my_url)
        response = req.json()
        actors_chart_data = response["actors_chart_data"]
        actor_names = [column[0] for column in actors_chart_data]
        self.assertTrue(req.ok)
        self.assertEqual(len(actors_chart_data), 7)
        self.assertIn('سازمان حفاظت محیط زیست', actor_names)