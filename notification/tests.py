from django.test import TestCase
from django.contrib.auth import get_user_model
from booking.models import Booking
from artists.models import Artist, Rate
from .models import Notification
from datetime import timedelta,date
from django.utils import timezone


USER = get_user_model()

class NotificationModelTestCase(TestCase):

    def setUp(self):
        # Create a User for testing
               # Create artist and client users
        self.client_user = USER.objects.create_user(email="aasdfas@gmail.com", password="asdfas", first_name="Long", last_name="Mejia")
        self.artist_user = USER.objects.create_user(email="artistuser@gmail.com", password="testpassword", first_name="John", last_name="Cena")


        # Create Artist and Rate for Booking
        self.artist = Artist.objects.create(user=self.artist_user, stage_name="Artist Name")
        self.rate = Rate.objects.create(artist=self.artist, name="Test Rate", amount=100.00)

        # Create a Booking
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        self.booking = Booking.objects.create(
            artist=self.artist,
            client=self.client_user,
            rate=self.rate,
            amount=self.rate.amount,
            start_time=start_time,
            end_time=end_time,
            event_date=date.today()  # Ensure event_date is set properly
        )

    def test_create_notification(self):
        # Create a Notification for booking confirmation
        notification = Notification.objects.create(
            user=self.client_user,
            notification_type="booking_confirmation",
            title="Booking Confirmation",
            description="Your booking has been confirmed.",
            booking=self.booking
        )

        # Test if the notification is created correctly
        self.assertEqual(notification.user, self.client_user)
        self.assertEqual(notification.notification_type, "booking_confirmation")
        self.assertEqual(notification.title, "Booking Confirmation")
        self.assertEqual(notification.description, "Your booking has been confirmed.")
        self.assertEqual(notification.booking, self.booking)

    def test_notification_read_status(self):
        # Create a Notification for a new follower
        notification = Notification.objects.create(
            user=self.client_user,
            notification_type="new_follower",
            title="New Follower",
            description="You have a new follower.",
            follower=self.client_user
        )

        # Test if the notification is unread initially
        self.assertFalse(notification.is_read)

        # Mark the notification as read
        notification.read()

        # Test if the notification is read
        self.assertTrue(notification.is_read)

    def test_notification_ordering(self):
        # Create multiple Notifications
        notification_1 = Notification.objects.create(
            user=self.client_user,
            notification_type="booking_rejected",
            title="Booking Rejected",
            description="Your booking was rejected.",
            booking=self.booking
        )
        notification_2 = Notification.objects.create(
            user=self.client_user,
            notification_type="message",
            title="New Message",
            description="You have a new message.",
            message="Hello, this is a message."
        )

        # Create a Notification that is read
        notification_3 = Notification.objects.create(
            user=self.client_user,
            notification_type="payment_reminder",
            title="Payment Reminder",
            description="Reminder to make your payment.",
            booking=self.booking,
            is_read=True
        )

        # Test that notifications are ordered by read status (unread first) and then by created_at
        notifications = Notification.objects.all()

        # Assert that the first notification is unread
        self.assertEqual(notifications[0], notification_1)
        self.assertEqual(notifications[1], notification_2)
        self.assertEqual(notifications[2], notification_3)

    def test_create_notification_without_booking(self):
        # Create a Notification for a new follower without a booking
        notification = Notification.objects.create(
            user=self.client_user,
            notification_type="new_follower",
            title="New Follower",
            description="You have a new follower.",
            follower=self.client_user
        )

        # Test if the notification is created correctly without a booking
        self.assertEqual(notification.user, self.client_user)
        self.assertEqual(notification.notification_type, "new_follower")
        self.assertEqual(notification.title, "New Follower")
        self.assertEqual(notification.description, "You have a new follower.")
        self.assertIsNone(notification.booking)
