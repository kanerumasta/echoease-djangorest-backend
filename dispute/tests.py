from django.test import TestCase
from django.contrib.auth import get_user_model
from booking.models import Booking
from artists.models import Artist, Rate
from .models import Dispute, DisputeEvidence, ArtistDispute, ClientDispute
from datetime import timedelta, date
from django.utils import timezone


USER = get_user_model()


class DisputeModelTestCase(TestCase):
    def setUp(self):
        # Create a User and Artist for testing
        self.client = USER.objects.create_user(first_name="John", last_name="Cena", email="jooh@gmail.com", password="testpassword")
        self.user = USER.objects.create_user(email="testuser@gmail.com", password="testpassword")
        self.artist = Artist.objects.create(user=self.user, stage_name="Artist Name")

        # Create a Rate for the Booking
        self.rate = Rate.objects.create(
            artist=self.artist,
            name="Test Rate",
            amount=100.00  # Ensure this is not None
        )

        # Define start_time and end_time
        start_time = timezone.now() + timedelta(days=1)  # 1 day from now
        end_time = start_time + timedelta(hours=2)  # 2 hours after start_time

        # Create a Booking object using the created Rate
        self.booking = Booking.objects.create(
            artist=self.artist,
            event_date=date(2024, 12, 25),
            client=self.client,
            rate=self.rate,
            amount=self.rate.amount,
            start_time=start_time,  # Ensure start_time is set
            end_time=end_time,      # Ensure end_time is set
        )

        # Create other required objects for the dispute tests
        self.dispute = Dispute.objects.create(
            dispute_type='artist',
            booking=self.booking,
            artist=self.artist,
            description="Test Dispute"
        )

        self.client_dispute = ClientDispute.objects.create(
            booking=self.booking,
            client=self.user,
            reason="performance_quality",
            description="Test Client Dispute"
        )

        self.artist_dispute = ArtistDispute.objects.create(
            booking=self.booking,
            artist=self.artist,
            reason="no_show",
            description="Test Artist Dispute"
        )

    def test_create_dispute(self):
        # Create a dispute
        dispute = Dispute.objects.create(
            dispute_type="artist",
            booking=self.booking,
            artist=self.artist,
            client=self.user,
            reason="performance_quality",
            description="The performance quality was subpar.",
            status="open"
        )

        # Test dispute was created correctly
        self.assertEqual(dispute.booking, self.booking)
        self.assertEqual(dispute.artist, self.artist)
        self.assertEqual(dispute.client, self.user)
        self.assertEqual(dispute.reason, "performance_quality")
        self.assertEqual(dispute.status, "open")

    def test_create_dispute_evidence(self):
        # Create a dispute evidence
        dispute = Dispute.objects.create(
            dispute_type="artist",
            booking=self.booking,
            artist=self.artist,
            client=self.user,
            reason="no_show",
            description="The artist did not show up for the event.",
            status="under_review"
        )

        evidence = DisputeEvidence.objects.create(
            media_type="image",
            description="Screenshot of missed call",
            dispute=dispute,
            file="path/to/file.jpg"
        )

        # Test evidence was created correctly
        self.assertEqual(evidence.dispute, dispute)
        self.assertEqual(evidence.media_type, "image")
        self.assertEqual(evidence.description, "Screenshot of missed call")

    def test_create_artist_dispute(self):
        # Create an artist dispute
        artist_dispute = ArtistDispute.objects.create(
            booking=self.booking,
            artist=self.artist,
            reason="cancellation",
            description="Artist canceled last minute.",
            status="open"
        )

        # Test artist dispute was created correctly
        self.assertEqual(artist_dispute.booking, self.booking)
        self.assertEqual(artist_dispute.artist, self.artist)
        self.assertEqual(artist_dispute.reason, "cancellation")
        self.assertEqual(artist_dispute.status, "open")

    def test_create_client_dispute(self):
        # Create a client dispute
        client_dispute = ClientDispute.objects.create(
            booking=self.booking,
            client=self.user,
            reason="miscommunication",
            description="There was a miscommunication about the time.",
            status="open"
        )

        # Test client dispute was created correctly
        self.assertEqual(client_dispute.booking, self.booking)
        self.assertEqual(client_dispute.client, self.user)
        self.assertEqual(client_dispute.reason, "miscommunication")
        self.assertEqual(client_dispute.status, "open")

    def test_dispute_status_change(self):
        # Create a dispute and change its status
        dispute = Dispute.objects.create(
            dispute_type="client",
            booking=self.booking,
            artist=self.artist,
            client=self.user,
            reason="no_show",
            description="Artist failed to show up.",
            status="under_review"
        )

        # Change the status to resolved
        dispute.status = "resolved"
        dispute.is_resolved = True
        dispute.date_resolved = "2024-11-25"
        dispute.resolution = "Artist failed to attend the event."
        dispute.save()

        # Test the status and resolution
        dispute.refresh_from_db()
        self.assertEqual(dispute.status, "resolved")
        self.assertTrue(dispute.is_resolved)
        self.assertEqual(dispute.resolution, "Artist failed to attend the event.")

    def test_str_method_in_dispute(self):
        # Create a dispute and check its string representation
        dispute = Dispute.objects.create(
            dispute_type="client",
            booking=self.booking,
            artist=self.artist,
            client=self.user,
            reason="performance_quality",
            description="The performance quality was subpar.",
            status="under_review"
        )

        # Assuming the string method of the Dispute model is: f'{self.booking}-{self.dispute_type}'
        self.assertEqual(str(dispute), f'{self.booking}-{dispute.dispute_type}')
