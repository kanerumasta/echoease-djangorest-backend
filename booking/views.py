from django.shortcuts import render
from django.db.models import Q, Exists, OuterRef
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status,pagination
from .serializers import BookingSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Booking
from notification.models import Notification
from .permissions import IsInvolved
from rest_framework.decorators  import permission_classes
from artists.models import Artist
from payment.models import Payment
from datetime import timedelta, datetime
from django.utils.timezone import now, make_aware

from payment.utils import refund_payment, send_compensation_fee
from notification.utils import (
    notify_artist_of_new_booking,
    notify_client_of_accepted_booking,
    notify_artist_of_paid_downpayment,
    notify_client_of_cancelled_booking,
    notify_client_of_rejected_booking,

)
from django.http import FileResponse
from .utils import (
    create_new_booking_notification,
    create_booking_confirmation_notification,
    create_booking_rejected_notification,

    # generate_booking_pdf
)
from decimal import Decimal


class BookingPagination(pagination.PageNumberPagination):
    page_size = 6
    max_page_size=20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'count': self.page.paginator.count,
            'results': data
        },status=status.HTTP_200_OK)






class BookingView(views.APIView):
    pagination_class = BookingPagination
    def post(self, request):
        artist_id = request.data.get('artist')
        artist = get_object_or_404(Artist, id = artist_id)
        serializer = BookingSerializer(data = request.data)
        try:
            if serializer.is_valid():
                booking = serializer.save(client = request.user)
                booking_id = booking.id # type: ignore
                notify_artist_of_new_booking(artist=artist.user, booking = booking)
                create_new_booking_notification(booking_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        status_filter = request.query_params.get('status', None)
        q = request.query_params.get('q', None)
        sort_by = request.query_params.get('sort_by', None)
        sort_order = request.query_params.get('sort_order', None) #asc or desc
        paginate = request.query_params.get('paginate', False)
        bookings = Booking.objects.filter(Q(client=request.user) | Q(artist__user=request.user))

        if q is not None:
            search_terms = q.split()
            query = Q()
            for term in search_terms:
                query |= (
                    Q(booking_reference__icontains=term) |
                    Q(event_name__icontains=term) |
                    Q(client__first_name__icontains=term) |
                    Q(client__last_name__icontains=term) |
                    Q(artist__user__first_name__icontains=term) |
                    Q(artist__user__last_name__icontains=term) |
                    Q(status__icontains=term)
                )
            bookings = bookings.filter(query)

        # Apply the status filter if it is provided
        if status_filter is not None:
            statuses = status_filter.split(',')
            bookings = bookings.filter(status__in=statuses)
        if sort_by is not None:
            order = f'{"-" if sort_order == "desc" else "" }{sort_by}'
            bookings = bookings.order_by(order)

        # Only paginate if we're retrieving all bookings
        if str(paginate).lower() == 'true':
            paginator = self.pagination_class()
            paginated_bookings = paginator.paginate_queryset(bookings, request)
            serializer = BookingSerializer(paginated_bookings, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If status_filter is provided, return all matching bookings without pagination
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookingDetailView(views.APIView):
    permission_classes = [IsAuthenticated, IsInvolved]
    def get(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        self.check_object_permissions(request, booking)
        serializer = BookingSerializer(booking, context={'request':request})

        #make notification as read
        notifications = Notification.objects.filter(booking=booking,user = request.user)
        for notif in notifications:
            if not notif.is_read:
                notif.read()
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookingConfirmView(views.APIView):
    permission_classes = [IsAuthenticated, IsInvolved]
    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        if not booking.is_pending:
            return Response({'message':'this booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        booking.approve()
        create_booking_confirmation_notification(id)
        notify_client_of_accepted_booking(client=booking.client,booking=booking)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookingRejectView(views.APIView):
    permission_classes=[IsAuthenticated, IsInvolved]
    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        reason = request.data.get('reason','No reason stated.')
        if not booking.is_pending:
            return Response({'message':'this booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        booking.decline_reason = reason
        booking.reject()
        booking.save()
        create_booking_rejected_notification(id)
        notify_client_of_rejected_booking(user=booking.client, booking=booking)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookingCancelView(views.APIView):
    permission_classes = [IsAuthenticated, IsInvolved]

    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        cancel_reason = request.data.get('cancel_reason', 'No reason stated')
        event_date = booking.event_date
        today = datetime.now().date()

        if booking.is_completed:
            return Response({'message': 'This booking is already completed and cannot be canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.client == request.user:
            cancelled_by = 'client'
        elif booking.artist.user == request.user:
            cancelled_by = 'artist'
        else:
            return Response({'message': 'You do not have permission to cancel this booking.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status == 'approved':
            downpayment = Payment.objects.filter(booking=booking, payment_type='downpayment').first()
            if downpayment is None:
                return Response({'message': 'No downpayment found for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

            if cancelled_by == 'client':
                start_range = event_date - timedelta(days=6)
                end_range = event_date - timedelta(days=2)

                if start_range <= today <= end_range:  # Within 2-6 days
                    amount = downpayment.amount * Decimal(0.5)
                elif today < start_range:  # More than 6 days before
                    amount = downpayment.amount - Decimal(50)  # Adjust amount
                else:  # Less than 2 days before
                    amount = Decimal(0)
                    compensation_amount = downpayment.amount - 50
                    send_compensation_fee(booking_id=booking.pk, amount=compensation_amount, channel_code=booking.artist.channel_code)

            elif cancelled_by == 'artist':
                amount = downpayment.amount - 50

            if amount > 0:
                refundSuccess = refund_payment(
                    amount=amount,
                    invoice_id=downpayment.payment_id,
                    payment_id=downpayment.pk,
                    reason="CANCELLATION"
                )

                if refundSuccess:
                    booking.status = 'cancelled'
                    booking.cancelled_by = cancelled_by
                    booking.cancel_reason = cancel_reason
                    booking.save()

        # Perform the cancellation
        booking.cancel(cancelled_by=cancelled_by)
        booking.cancel_reason = cancel_reason
        booking.save()

        # Create notification
        if cancelled_by == 'client':
            notification = Notification.objects.create(
                notification_type='booking_cancelled',
                user=booking.artist.user,  # Notify the artist when the client cancels
                title=f"Booking Cancelled: #{booking.booking_reference}",
                description=f"{booking.client.first_name.title()} canceled their booking on {booking.event_date.strftime('%Y-%m-%d')}.",
                booking=booking
            )
        else:
            notification = Notification.objects.create(
                notification_type='booking_cancelled',
                user=booking.client,  # Notify the client when the artist cancels
                title=f"Booking Cancelled: #{booking.booking_reference}",
                description=f"{booking.artist.user.first_name.title()} canceled your booking on {booking.event_date.strftime('%Y-%m-%d')}.",
                booking=booking
            )

        # Check if notification was successfully created
        if not notification:
            return Response({'message': 'Failed to create notification.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Log the created notification for debugging
        print("Notification Created:", notification)

        # Create additional notifications (e.g., for internal system)
        if cancelled_by == 'client':
            notify_client_of_cancelled_booking(user=booking.artist.user, booking=booking)
        elif cancelled_by == 'artist':
            notify_client_of_cancelled_booking(user=booking.client, booking=booking)

        return Response({'message': 'Booking cancellation successful, notification sent.'}, status=status.HTTP_200_OK)



class PendingPaymentsView(views.APIView):
    pagination_class = BookingPagination
    def get(self, request):
        final_payment_exists = Payment.objects.filter(
            booking = OuterRef('pk'),
            payment_type = 'final_payment'
        )
        bookings = Booking.objects.filter(
            Q(artist__user=request.user) | Q(client=request.user),
              status='approved',
                event_date__lt=datetime.now().date(),
             ).filter(
                ~Exists(final_payment_exists)
             )
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UpcomingEventsView(views.APIView):
    def get(self, request):
        bookings = Booking.objects.filter(
            Q(artist__user=request.user) | Q(client=request.user),
              status='approved',
            event_date__gt=datetime.now().date()
             ).order_by('event_date','start_time')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingHistoryView(views.APIView):
    pass
