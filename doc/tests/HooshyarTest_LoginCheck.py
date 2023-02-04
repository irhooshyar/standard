from django.test import TestCase
import requests

class LoginCheckTestClass(TestCase):
    databases = {}
    base_url = "http://127.0.0.1:8000"

    def test_GetAllowedPanels(self):
        username = "test_user"
        my_url = self.base_url + "/get_allowed_panels/" + username + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)

    def test_CheckUserLogin_found(self):
        username = "test_user"
        password = "asdfg@1"
        user_ip = "127.0.0.1"
        my_url = self.base_url + "/CheckUserLogin/" + username + "/" + password + "/" + user_ip + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        status = req.json()["status"]
        self.assertEqual(status, "found user")

    def test_CheckUserLogin_wrongpassword(self):
        username = "test_user"
        password = "aDVrvR1"
        user_ip = "127.0.0.1"
        my_url = self.base_url + "/CheckUserLogin/" + username + "/" + password + "/" + user_ip + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        status = req.json()["status"]
        self.assertEqual(status, "wrong password")

    def test_CheckUserLogin_notfound(self):
        username = "test_user_kfkf"
        password = "asdfg@1"
        user_ip = "127.0.0.1"
        my_url = self.base_url + "/CheckUserLogin/" + username + "/" + password + "/" + user_ip + "/"
        req = requests.request("GET", my_url)
        self.assertTrue(req.ok)
        status = req.json()["status"]
        self.assertEqual(status, "not found")
