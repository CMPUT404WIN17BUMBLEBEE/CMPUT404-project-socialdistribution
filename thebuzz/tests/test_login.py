from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class LoginTestCase(TestCase):

    def setUp(self):
        global user_id
        password = make_password("password123")
        user = User.objects.create(username="TestUser", password=password)
        user_id = user.id

    def test_logging_in(self):
        user = User.objects.get(id=user_id)

        response = self.client.login(username='TestUser', password='password123')
        self.assertTrue(response, "failed to log user in")

        response = self.client.get("/posts/")
        self.assertEquals(response.status_code, 200, "not able to get to posts page")

    def test_invalid_log_in(self):
        response = self.client.login(username='fakeuser', password='123')

        self.assertFalse(response, "invalid user logged in")

    def test_logging_out(self):
        user = User.objects.get(id=user_id)
        self.client.login(username='TestUser', password='password123')
        self.client.logout()

        response = self.client.get("/posts/")
        self.assertNotEqual(response.status_code, 200, "was able to get into posts page when I shouldn't have")
