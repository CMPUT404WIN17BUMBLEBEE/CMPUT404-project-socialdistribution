from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from thebuzz.models import Profile

class FriendsTestCase(TestCase):

    def setUp(self):
        global profile1, profile2, profile3, profile4, profile5
        #Setting up some users to use for friending and unfriending
        password = make_password("password123")
        user1 = User.objects.create(username="TestUser1", password=password)
        profile1 = Profile.objects.get(user_id = user1.id)
        profile1.displayName="TestUser1"
        profile1.save()
        user2 = User.objects.create(username="TestUser2", password=password)
        profile2 = Profile.objects.get(user_id = user2.id)
        profile2.displayName="TestUser2"
        profile2.save()
        user3 = User.objects.create(username="TestUser3", password=password)
        profile3 = Profile.objects.get(user_id = user3.id)
        profile3.displayName="TestUser3"
        profile3.save()
        user4 = User.objects.create(username="TestUser4", password=password)
        profile4 = Profile.objects.get(user_id = user4.id)
        profile4.displayName="TestUser4"
        profile4.save()
        user5 = User.objects.create(username="TestUser5", password=password)
        profile5 = Profile.objects.get(user_id = user5.id)
        profile5.displayName="TestUser5"
        profile5.save()

    def test_following(self):
        self.assertFalse(profile1.get_all_following(), "should not be following anyone")

        profile1.follow(profile2)
        profile1.save()

        profile1.follow(profile3)
        profile1.save()

        following = profile1.get_all_following()
        self.assertEqual(following[0], profile2, "not following TestUser2")
        self.assertEqual(following[1], profile3, "not following TestUser3")

    def test_be_followed(self):
        self.assertFalse(profile1.get_all_followers(), "no one should be following")

        profile4.follow(profile1)
        profile4.save()

        profile5.follow(profile1)
        profile5.save()

        profile1.add_user_following_me(profile4)
        profile1.save()
        profile1.add_user_following_me(profile5)
        profile1.save()

        followers = profile1.get_all_followers()
        self.assertEqual(followers[0], profile4, "TestUser4 is not following")
        self.assertEqual(followers[1], profile5, "TestUser5 is not following")

    def test_friends(self):
        profile1.follow(profile2)
        profile1.save()

        profile4.follow(profile1)
        profile4.save()
        profile1.add_user_following_me(profile4)
        profile1.save()

        self.assertFalse(profile1.get_all_friends(), "TestUser1 should not have friends")
        profile1.friend(profile4)
        profile1.save()
        self.assertTrue(profile1.get_all_friends(), "TestUser1 should have friends")

        self.assertFalse(profile2.get_all_friends(), "TestUser2 should not have friends")
        profile2.friend(profile1)
        profile2.save()
        self.assertTrue(profile2.get_all_friends()), "TestUser2 should have friends"

        profile1Friends = profile1.get_all_friends()
        self.assertEqual(len(profile1Friends), 2, "TestUser1 should have 2 friend")
        self.assertEqual(profile1Friends[0], profile2, "TestUser1 should have TestUser2 as friend")
        self.assertEqual(profile1Friends[1], profile4, "TestUser1 should have TestUser4 as friend")

        profile2Friends = profile2.get_all_friends()
        self.assertEqual(len(profile2Friends), 1, "TestUser2 should have 1 friend")
        self.assertEqual(profile2Friends[0], profile1, "TestUser1 should have TestUser1 as friend")

        profile2.unfriend(profile1)
        self.assertFalse(profile2.get_all_friends(), "TestUser2 should not have friends")
        profile1Friends = profile1.get_all_friends()
        self.assertEqual(len(profile1Friends), 1, "TestUser1 should only have 1 friend now")
        self.assertEqual(profile1Friends[0], profile4, "TestUser1 should have TestUser4 as friend")
