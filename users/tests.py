from django.test import TestCase
from unittest.mock import patch
from .models import UserAccount, Profile

class UserAccountModelTest(TestCase):
    def setUp(self):
        # Create a user explicitly
        self.user = UserAccount.objects.create_user(
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="client",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertEqual(self.user.full_name, "Test User")

    def test_user_roles(self):
        self.assertTrue(self.user.is_client)
        self.assertFalse(self.user.is_artist)

    def test_decrease_reputation(self):
        initial_score = self.user.reputation_score
        self.user.decrease_reputation(20)
        self.assertEqual(self.user.reputation_score, max(initial_score - 20, 0))

    def test_increase_reputation(self):
        initial_score = self.user.reputation_score
        self.user.increase_reputation(10)
        self.assertEqual(self.user.reputation_score, initial_score + 10)

    def test_suspend_user(self):
        self.user.suspend()
        self.assertTrue(self.user.is_suspended)

    def test_create_superuser(self):
        admin = UserAccount.objects.create_superuser(
            email="admin@example.com", password="adminpassword", first_name="Admin", last_name="User"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, "admin")


class ProfileModelTest(TestCase):
    def setUp(self):
        # Create a user explicitly
        self.user = UserAccount.objects.create_user(
            email="profileuser@example.com",
            password="password123",
            first_name="Profile",
            last_name="User",
        )

        # Ensure no profile exists already for this user (clear the signal)
        Profile.objects.filter(user=self.user).delete()

        # Create a profile explicitly for the test
        self.profile = Profile.objects.create(user=self.user, gender="Male", country="Philippines")

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.gender, "Male")
        self.assertEqual(self.profile.country, "Philippines")
        self.assertEqual(str(self.profile), f"P-{self.user}")

    def test_profile_is_complete(self):
        self.assertFalse(self.profile.is_complete)
        self.profile.is_complete = True
        self.profile.save()
        self.assertTrue(self.profile.is_complete)
