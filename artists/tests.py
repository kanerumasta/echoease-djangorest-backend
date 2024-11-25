from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import (
    IDType,
    Genre,
    ArtistApplication,
    Artist,
    Portfolio,
    PortfolioItem,
    PortfolioItemMedia,
    Rate,
    ConnectionRequest,
)
from django.db.utils  import IntegrityError

User = get_user_model()

class IDTypeModelTest(TestCase):
    def test_create_id_type(self):
        id_type = IDType.objects.create(name="Passport")
        self.assertEqual(str(id_type), "Passport")
        self.assertIsInstance(id_type, IDType)

class GenreModelTest(TestCase):
    def test_create_genre(self):
        genre = Genre.objects.create(name="Pop")
        self.assertEqual(str(genre), "Pop")
        self.assertIsInstance(genre, Genre)


class ArtistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="artistuser@example.com",
            password="password011456",
            first_name="TestArtist",
            last_name="TestArtist"
            )

    def test_create_artist(self):
        artist = Artist.objects.create(user=self.user, stage_name="Test Artist")
        self.assertEqual(artist.user, self.user)
        self.assertEqual(artist.stage_name, "Test Artist")
        self.assertEqual(str(artist), f"{self.user.first_name} {self.user.last_name}".title())

    def test_encrypted_account_number(self):
        artist = Artist.objects.create(user=self.user)
        artist.set_account_number("123456789")
        self.assertIsNotNone(artist.encrypted_account_number)
        self.assertEqual(artist.get_account_number(), "123456789")


class ConnectionRequestModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="artist1@example.com",
            password="password",
            first_name="Artist1",
            last_name="Artist1"
            )
        self.user2 = User.objects.create_user(
            email="artist2@example.com",
            password="password",
            first_name="Artist2",
            last_name="Artist2")
        self.artist1 = Artist.objects.create(user=self.user1, stage_name="Artist1")
        self.artist2 = Artist.objects.create(user=self.user2, stage_name="Artist2")

    def test_create_connection_request(self):
        request = ConnectionRequest.objects.create(sender=self.artist1, receiver=self.artist2)
        self.assertEqual(request.status, "pending")
        self.assertEqual(str(request), f"{self.artist1} to {self.artist2} - {request.status}")



    def test_accept_connection_request(self):
        request = ConnectionRequest.objects.create(sender=self.artist1, receiver=self.artist2)
        request.accept()
        self.assertEqual(request.status, "accepted")
        self.assertIn(self.artist2, self.artist1.connections.all())

    def test_reject_connection_request(self):
        request = ConnectionRequest.objects.create(sender=self.artist1, receiver=self.artist2)
        request.reject()
        self.assertEqual(request.status, "rejected")

    def test_duplicate_request_validation(self):
        ConnectionRequest.objects.create(sender=self.artist1, receiver=self.artist2)
        with self.assertRaises(IntegrityError):
            ConnectionRequest.objects.create(sender=self.artist1, receiver=self.artist2)  # Should raise ValidationError

class PortfolioModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolio_user@example.com",
            password="password",
            first_name="Portfolio",
            last_name="User")
        self.artist = Artist.objects.create(user=self.user, stage_name="Portfolio Artist")

    def test_create_portfolio(self):
        self.assertIsNotNone(self.artist.portfolio)

    def test_single_portfolio_creation(self):
        # Ensure only one portfolio per artist
        with self.assertRaises(IntegrityError):
            Portfolio.objects.create(artist=self.artist)

class RateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolio_user@example.com",
            password="password",
            first_name="Portfolio",
            last_name="User")
        self.artist = Artist.objects.create(user=self.user, stage_name="Rated Artist")

    def test_create_rate(self):
        rate = Rate.objects.create(artist=self.artist, name="Performance", amount=200.00)
        self.assertEqual(rate.artist, self.artist)
        self.assertEqual(rate.name, "Performance")
        self.assertEqual(rate.amount, 200.00)
