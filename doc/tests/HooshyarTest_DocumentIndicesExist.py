from django.test import TestCase
import requests

class DocumentIndicesExistTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"

    def test_indices_exist(self):
        country_id_list = [1, 3, 29, 32]

        for country_id in country_id_list:
            my_url = self.base_url + "/SearchDocument_ES/" + str(country_id) + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                     + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" + "0" + "/" \
                     + "0" + "/" + "عنوان یا متن" + "/" + "empty" + "/" + "all" + "/" \
                     + "1" + "/"
            req = requests.request("GET", my_url)
            self.assertTrue(req.ok)
