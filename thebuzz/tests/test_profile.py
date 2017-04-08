from django.test import TestCase
from thebuzz.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class ProfileTestCase(TestCase):

    def setUp(self):
        global user_id
        password = make_password("password123")
        user = User.objects.create(username="TestUser", password=password)
        user_id = user.id


    def test_profile_created_with_user(self):
        profile = Profile.objects.get(user_id = user_id)

        self.assertTrue(profile, "profile is empty")
        self.assertEqual(profile.user_id, user_id, "could not find matching profile")

    def test_updating_profile(self):
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

        self.assertEqual(updateProfile.user_id, user_id, "user id does not match")
        self.assertEqual(updateProfile.displayName, displayName, "display name does not match")
        self.assertEqual(updateProfile.firstName, fname, "first name does not match")
        self.assertEqual(updateProfile.lastName, lname, "last name does not match")
        self.assertEqual(updateProfile.email, email, "email does not match")
        self.assertEqual(updateProfile.github, github, "github does not match")
        self.assertEqual(updateProfile.bio, bio, "bio does not match")
