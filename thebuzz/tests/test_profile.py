from django.test import TestCase
from thebuzz.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class ProfileTestCase(TestCase):
    user_id = 0
    def setUp(self):
        global user_id
        password = make_password("password123")
        user = User.objects.create(username="TestUser", password=password)
        user_id = user.id


    def test_profile_created_with_user(self):
        global user_id
        profile = Profile.objects.get(user_id = user_id)

        self.assertEqual(profile.user_id, user_id)

    def test_updating_profile(self):
        global user_id
        profile = Profile.objects.get(user_id = user_id)
        displayName = "TEST USER"
        fname = "Fname"
        lname = "Lname"
        email = "testuser@gmail.com"
        github = "https://github.com/testuser"
        bio = "Stuff about me"

        profile.displayName = displayName
        profile.firstName = fname
        profile.lastName = lname
        profile.email = email
        profile.github = github
        profile.bio = bio
        profile.save()

        updateProfile = Profile.objects.get(user_id = user_id)
        self.assertEqual(updateProfile.user_id, user_id)
        self.assertEqual(updateProfile.displayName, displayName)
        self.assertEqual(updateProfile.firstName, fname)
        self.assertEqual(updateProfile.lastName, lname)
        self.assertEqual(updateProfile.email, email)
        self.assertEqual(updateProfile.github, github)
        self.assertEqual(updateProfile.bio, bio)
