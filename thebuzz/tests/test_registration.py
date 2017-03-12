from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class RegistrationTestCase(TestCase):
    user_id = 0

    def setUp(self):
        global user_id
        password = make_password("password123")
        user = User.objects.create(username="TestUser", password=password)
        user_id = user.id

    def test_get_register(self):
        response = self.client.get("/register/")

        self.assertEquals(response.status_code, 200, "not able to get to register page")

        user_form = response.context["form"]
        profile_form = response.context["profileForm"]

        self.assertTrue(user_form, "user/password fields do not exist")
        self.assertTrue(profile_form, "profile fields do not exist")
        self.assertTemplateUsed(response, "registration/registration_form.html", "incorrect template used")
        self.assertEqual(response.resolver_match.func.__name__, "register", "incorrect function view used")
