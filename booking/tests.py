from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Artist, Rate, Booking
from datetime import datetime, time
from decimal import Decimal
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

User = get_user_model()

class BookingModelTestCase(TestCase):
    def setUp(self):
        # Create Users
        self.user = User.objects.create_user(
           email="testuser@example.com", password="password"
        )
        self.client_user = User.objects.create_user(
           email="clientuser@example.com", password="password"
        )

        # Create Artist
        self.artist = Artist.objects.create(user=self.user, stage_name="Test Artist")

        # Create Rate for Booking
        self.rate = Rate.objects.create(
            artist=self.artist,
            name="Booking Fee",
            description="Fee for booking the artist",
            amount=Decimal("1000.00"),
        )

    def test_create_booking(self):
        # Create a Booking for the artist
        booking = Booking.objects.create(
            artist=self.artist,
            client=self.client_user,
            amount=self.rate.amount,
            event_name="Christmas Concert",
            event_date="2024-12-25",
            start_time="18:00",
            end_time="21:00",
            rate=self.rate,
            province="Metro Manila",
            municipality="Quezon City",
            barangay="Barangay 1",
            street="Main St",
            landmark="Near the mall"
        )

        # Check that the booking was created and associated correctly
        self.assertEqual(booking.artist, self.artist)
        self.assertEqual(booking.client, self.client_user)
        self.assertEqual(booking.amount, Decimal("1000.00"))
        self.assertEqual(booking.event_name, "Christmas Concert")
        self.assertEqual(booking.event_date, '2024-12-25')
        self.assertEqual(booking.start_time,'18:00')
        self.assertEqual(booking.end_time, '21:00')
        self.assertEqual(booking.status, 'pending')  # Default status is 'pending'
        self.assertEqual(booking.province, "Metro Manila")
        self.assertEqual(booking.municipality, "Quezon City")
        self.assertEqual(booking.barangay, "Barangay 1")
        self.assertEqual(booking.street, "Main St")
        self.assertEqual(booking.landmark, "Near the mall")
        self.assertEqual(booking.full_address, "Main St, Metro Manila, Quezon City, Barangay 1 @ Near the mall")

    def test_booking_approval(self):
        # Create a Booking for the artist
        booking = Booking.objects.create(
            artist=self.artist,
            client=self.client_user,
            amount=self.rate.amount,
            event_name="Christmas Concert",
            event_date="2024-12-25",
            start_time="18:00",
            end_time="21:00",
            rate=self.rate,
            province="Metro Manila",
            municipality="Quezon City",
            barangay="Barangay 1",
            street="Main St",
            landmark="Near the mall"
        )

        # Approve the booking
        booking.approve()
        booking.refresh_from_db()

        # Ensure the status has changed to 'awaiting_downpayment'
        self.assertEqual(booking.status, 'awaiting_downpayment')

    def test_booking_cancel(self):
        # Create a Booking for the artist
        booking = Booking.objects.create(
            artist=self.artist,
            client=self.client_user,
            amount=self.rate.amount,
            event_name="Christmas Concert",
            event_date="2024-12-25",
            start_time="18:00",
            end_time="21:00",
            rate=self.rate,
            province="Metro Manila",
            municipality="Quezon City",
            barangay="Barangay 1",
            street="Main St",
            landmark="Near the mall"
        )

        # Cancel the booking by the client
        booking.cancel(cancelled_by='client')
        booking.refresh_from_db()

        # Ensure the booking status is 'cancelled' and cancelled_by is 'client'
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(booking.cancelled_by, 'client')

    def test_invalid_booking_cancel(self):
        # Create a Booking for the artist
        booking = Booking.objects.create(
            artist=self.artist,
            client=self.client_user,
            amount=self.rate.amount,
            event_name="Christmas Concert",
            event_date="2024-12-25",
            start_time="18:00",
            end_time="21:00",
            rate=self.rate,
            province="Metro Manila",
            municipality="Quezon City",
            barangay="Barangay 1",
            street="Main St",
            landmark="Near the mall"
        )

        # Mark booking as completed
        booking.complete()
        booking.refresh_from_db()

        # Attempt to cancel the booking (should raise a IntegrityError)
        with self.assertRaises(ValidationError):
            booking.cancel(cancelled_by='client')

    def test_booking_time_validation(self):
        # Try creating a booking with invalid times (start time >= end time)
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                artist=self.artist,
                client=self.client_user,
                amount=self.rate.amount,
                event_name="Invalid Event",
                event_date="2024-12-25",
                start_time="22:00",
                end_time="20:00",  # Invalid: end time is before start time
                rate=self.rate,
                province="Metro Manila",
                municipality="Quezon City",
                barangay="Barangay 1",
                street="Main St",
                landmark="Near the mall"
            )
