from django.test import TestCase
from django.contrib.auth import get_user_model
from booking.models import Booking
from artists.models import Artist, Rate
from payment.models import Payment, Refund
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta,date

USER = get_user_model()

class PaymentRefundTestCase(TestCase):
    def setUp(self):
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

        # Create a Payment for the Booking
        self.payment = Payment.objects.create(
            user=self.client_user,
            title="Test Payment",
            payment_reference="REF12345",
            payment_status="completed",
            booking=self.booking,
            amount=Decimal("100.00"),
            net_amount=Decimal("95.00"),
            payment_type="final_payment",
        )

    def test_create_payment(self):
        self.assertEqual(self.payment.booking, self.booking)
        self.assertEqual(self.payment.amount, Decimal("100.00"))
        self.assertEqual(self.payment.payment_status, "completed")

    def test_create_refund(self):
        # Create a refund
        refund = Refund.objects.create(
            payment=self.payment,
            refund_id="REFUND12345",
            amount=Decimal("50.00"),
            reason="Overpayment",
        )

        self.assertEqual(refund.payment, self.payment)
        self.assertEqual(refund.amount, Decimal("50.00"))
        self.assertEqual(refund.reason, "Overpayment")
