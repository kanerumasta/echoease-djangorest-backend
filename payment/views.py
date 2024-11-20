from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from booking.models import Booking
from django.http import Http404
from payment.models import Payment, Refund
from decimal import Decimal, InvalidOperation
from django.conf import settings
from pprint import pprint
import base64
import requests
from notification.utils import notify_artist_of_paid_downpayment,notify_artist_of_paid_final_payment, notify_refunded_payment
from notification.models import Notification
from django.conf import settings
from .utils import send_payout, create_payment_invoice, get_invoice_details, is_valid_payment_type, refund_payment
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from transaction.models import Transaction
from django.http import JsonResponse
from dispute.models import Dispute

USER = settings.AUTH_USER_MODEL

class CreateInvoiceView(APIView):
    def post(self, request):
        booking_id = request.data.get('booking_id')
        payment_type = request.data.get('payment_type')
        redirect_url = request.data.get('redirect_url')
        valid_payment_type = is_valid_payment_type(payment_type)
        if not valid_payment_type:
             return Response({'message':'Not a valid payment type'},status=status.HTTP_400_BAD_REQUEST)
        if not booking_id or not payment_type or not redirect_url:
            return Response({'message':'Missing booking_id and payment_type'},status=status.HTTP_400_BAD_REQUEST)
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.amount is not None:
            if payment_type == 'downpayment':
                has_downpayment = Payment.objects.filter(payment_type='downpayment',booking=booking).exists()
                if has_downpayment:
                    return Response({'message':'Downpayment already exists'},status=status.HTTP_400_BAD_REQUEST)
                amount = booking.amount * Decimal(0.20)
            if payment_type == 'final_payment':
                downpayment = Payment.objects.filter(booking = booking, payment_type = 'downpayment').first()
                if not downpayment:
                    return Response({'message':'No downpayment found'},status=status.HTTP_400_BAD_REQUEST)
                has_final_payment = Payment.objects.filter(payment_type='final_payment',booking=booking)
                if has_final_payment:
                    return Response({'message':'Final payment already exists'},status=status.HTTP_400_BAD_REQUEST)
                amount = booking.amount - downpayment.amount

            invoice_url = create_payment_invoice(
                reference_id=booking.booking_reference,
                amount= float(amount),
                customer_email=booking.client.email,
                payment_type=payment_type,
                redirect_url=redirect_url
                )
            if invoice_url is not None:
                return Response({"invoice_url": invoice_url}, status=status.HTTP_200_OK)
        return Response({'message':'ERROR creating invoice'},status=status.HTTP_400_BAD_REQUEST)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

@csrf_exempt
@require_POST
def invoice_webhook(request):
    try:
        # Parse the JSON payload
        data = json.loads(request.body)
        print("Webhook received:", data)

        # Extract relevant fields from the webhook data
        invoice_id = data.get("id")
        booking_reference = data.get("external_id")
        status = data.get("status")
        amount = data.get("amount")
        payer_email = data.get("payer_email")
        payment_method = data.get("payment_method")
        payment_channel = data.get("payment_channel")

        # Validate required fields
        if not all([invoice_id, booking_reference, status, amount]):
            print('invoice_id', invoice_id)
            print('booking_reference', booking_reference)
            print('status', status)
            print('amount', amount)
            print("Missing required fields in the webhook data")
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Retrieve the booking object, return 404 if not found
        try:
            booking = Booking.objects.get(booking_reference=booking_reference)
        except Booking.DoesNotExist:
            print(f"Booking not found for booking_reference: {booking_reference}")
            return JsonResponse({"error": "Booking not found"}, status=404)

        # Retrieve the invoice details from Xendit (make sure to handle this gracefully)
        invoice_details = get_invoice_details(invoice_id=invoice_id)
        if invoice_details is None:
            print(f"Invoice details not found for invoice_id: {invoice_id}")
            return JsonResponse({"error": "Invoice details not found"}, status=404)

        # Extract metadata if available
        metadata = invoice_details.get("metadata", {})
        if not metadata:
            print(f"No metadata found for invoice_id: {invoice_id}")

        # Process payment if the status is 'PAID' and metadata is present
        if status == "PAID" and metadata:
            payment_type = metadata.get('payment_type')
            if payment_type:
                    # Create payment entry in the database
                payment = Payment.objects.create(
                    user = booking.client,
                    payment_status='paid',
                    booking=booking,
                    payment_id = invoice_id,
                    amount=amount,
                    net_amount=amount,
                    payment_method=payment_method,
                    payer_channel=payment_channel,
                    payer_email=payer_email,
                    payment_type=payment_type,
                    title=f'{'final_payment' if payment_type == 'final payment' else payment_type} for Booking {booking.artist.user.first_name} {booking.artist.user.last_name}'
                )
                payment.payment_reference  = f'PAY{payment.pk:06d}'
                payment.save()
                booking.status = 'approved'
                booking.save()
                print(f"Payment recorded for booking_reference: {booking_reference}")
                if payment_type == 'downpayment':
                    try:
                        notification = Notification.objects.create(
                            notification_type = 'downpayment_paid',
                            user = booking.artist.user,
                            title="Downpayment Received! Your Event is Ready!",
                            description=f"Great news! Echoer {booking.client.first_name.title()} {booking.client.last_name.title()} has successfully paid the downpayment for your confirmed booking . Your event is now all set and ready to go. We’re excited for the big day!",  # type: ignore
                            booking=booking
                        )
                        notify_artist_of_paid_downpayment(artist=booking.artist.user, booking=booking)
                    except Exception as e:
                        print("failed create notification")
                #Send Dibursement if final payment
                if payment_type == 'final_payment' and booking.amount is not None:
                    payout_amount = booking.amount - (booking.amount * Decimal(0.05))
                    payout = send_payout(amount=payout_amount,booking_id=booking.pk, channel_code="PH_GCASH")#CHANGE

            else:
                print(f"Payment type not found in metadata for booking_reference: {booking_reference}")
        else:
            print(f"Payment not processed or invalid status for booking_reference: {booking_reference}")

        return JsonResponse({"status": "success"}, status=200)

    except json.JSONDecodeError:
        print("Invalid JSON in the webhook payload")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print("Unexpected error in webhook processing:", str(e))
        return JsonResponse({"error": "Server error"}, status=500)

@csrf_exempt
@require_POST
def payout_webhook(request):
    try:
        data = json.loads(request.body)
        pprint(data)
        status = data['data']['status']
        reference_id = data['data']['reference_id']
        payment_method = data['data']['channel_category']
        payment_channel = data['data']['channel_code']
        amount = data['data']['amount']
        print('status', status)
        if status == 'SUCCEEDED':
            if reference_id:
                try:
                    booking = Booking.objects.get(booking_reference=reference_id)
                except Exception as e:
                    print('ERROR',e)
                    return JsonResponse({'message':'Error'}, status=400)
            if booking is not None:
                booking_client:USER = booking.client
                payment = Payment.objects.create(
                            user = booking.artist.user,
                            payment_status='paid',
                            booking=booking,
                            amount=amount,
                            net_amount=amount,
                            payment_method=payment_method,
                            payer_channel=payment_channel,
                            payment_type="payout",
                            title=f'Booking payment from {booking_client.first_name} {booking_client.last_name}'

                        )
                payment.payment_reference  = f'PAY{payment.pk:06d}'
                payment.save()
                booking.complete()

                #add reputation if no dispute booking
                disputes = Dispute.objects.filter(booking = booking)
                if not disputes.exists():
                    user = booking.artist.user
                    user.increase_reputation(5)
                    user.save()
                    if user.reputation_score > 100:
                        user.reputation_score = 100
                        user.save()
                    try:
                        Notification.objects.create(
                            user=user,
                            notification_type= "reputation",
                            title="Reputation Points Increased",
                            description=f"Congratulations! You've earned 5 reputation points for your successful payment. Your total reputation score is now {user.reputation_score} out of 100.",  # type: ignore
)
                    except Exception as e:
                        print(e)


                notification = Notification.objects.create(
                            notification_type = 'dibursement_received',
                            user = booking.artist.user,
                            title=f"Your booking with Echoer {booking_client.first_name} {booking_client.last_name} is fully paid. Please check your connected bank or wallet account.",
                            description=f"Great news! Echoer {booking.client.first_name.title()} {booking.client.last_name.title()} has successfully paid for your confirmed booking!",  # type: ignore
                            booking=booking
                        )
                notify_artist_of_paid_final_payment(artist=booking.artist.user, booking=booking)
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({'message':'Error'}, status=400)
    except Exception as e:
        print('ERROR', e)
        return JsonResponse({'message':'Error'}, status=400)

@csrf_exempt
@require_POST
def refund_success_webhook(request):
    try:
        # Parse request body
        response = json.loads(request.body)
        pprint(response)

        # Extract necessary data
        data = response.get('data', {})
        payment_id = data.get('metadata', {}).get('payment_id')
        amount = data.get('amount')
        reason = data.get('reason')
        refund_id = data.get('id')

        # Validate required fields
        if not all([payment_id, amount, reason, refund_id]):
            return JsonResponse({"status": "error", "message": "Invalid payload"}, status=400)

        # Retrieve the associated payment
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"Payment not found with ID {payment_id}"}, status=404)

        # Create refund record
        refund = Refund.objects.create(
            payment=payment,
            refund_id=refund_id,
            amount=amount,
            reason=reason,
        )

        # Create transaction record
        Transaction.objects.create(
            transaction_type='refund',
            user=payment.user,
            amount=amount,
            payment=payment,
            title=f'Refund Received for Payment #{payment.payment_reference}',
            booking=payment.booking,
        )

        payment_user:USER = payment.user

        # Notify the user about the refund
        notify_refunded_payment(user=payment.user)

        # Create notification record
        Notification.objects.create(
            notification_type='refund_received',
            user=payment.user,
            title=f"Refund Received for Payment #{payment.payment_reference}",
            description=(
                f"{payment_user.first_name.title()} {payment_user.last_name.title()}, "
                f"you received a refund for your booking payment of PHP {amount:.2f}. "
                f"The reason for the refund is: {reason}."
            ),
            booking=payment.booking
        )

        return JsonResponse({"status": "success"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
    except Exception as e:
        print(f"Error processing refund webhook: {e}")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)


@csrf_exempt
@require_POST
def refund_failed_webhook(request):
    try:
        response = json.loads(request.body)
        data = response['data']
        amount = data['amount']
        print(response)

        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"status": "error"}, status=400)
