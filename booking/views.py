from django.shortcuts import render
from django.db.models import Q, Exists, OuterRef
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status,pagination
from .serializers import BookingSerializer
from django.shortcuts import get_object_or_404
from .models import Booking
from notification.models import Notification
from .permissions import IsInvolved
from rest_framework.decorators  import permission_classes
from artists.models import Artist
from payment.models import Payment
from notification.utils import (
    notify_artist_of_new_booking,
    notify_client_of_accepted_booking,
    notify_artist_of_paid_downpayment,
)
from .utils import (
    create_new_booking_notification,
    create_booking_confirmation_notification,
    create_booking_rejected_notification,
    create_booking_cancelled_notification
)
from django.utils import timezone
import datetime

class BookingPagination(pagination.PageNumberPagination):
    page_size = 10
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

    @permission_classes([IsInvolved])
    def get(self, request, id=None):
        if id:
            booking = get_object_or_404(Booking, id=id)
            self.check_object_permissions(request, booking)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)

        status_filter = request.query_params.get('status')
        bookings = Booking.objects.filter(Q(client=request.user) | Q(artist__user=request.user))

        # Apply the status filter if it is provided
        if status_filter:
            bookings = bookings.filter(status=status_filter)

        # Only paginate if we're retrieving all bookings
        if not status_filter:
            paginator = self.pagination_class()
            paginated_bookings = paginator.paginate_queryset(bookings, request)
            serializer = BookingSerializer(paginated_bookings, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If status_filter is provided, return all matching bookings without pagination
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingConfirmView(views.APIView):
    @permission_classes([IsInvolved])
    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        if not booking.is_pending:
            return Response({'message':'this booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        booking.approve()
        create_booking_confirmation_notification(id)
        notify_client_of_accepted_booking(client=booking.client,booking=booking)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookingRejectView(views.APIView):
    @permission_classes([IsInvolved])
    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        if not booking.is_pending:
            return Response({'message':'this booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        booking.reject()
        create_booking_rejected_notification(id)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookingCancelView(views.APIView):
    @permission_classes([IsInvolved])
    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)
        if not booking.is_pending:
            return Response({'message':'this booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        booking.cancel()
        create_booking_cancelled_notification(id)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
                event_date__lt=datetime.datetime.now().date(),
             ).filter(
                ~Exists(final_payment_exists)
             )
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
class UpcomingEventsView(views.APIView):
    def get(self, request):
        print()
        bookings = Booking.objects.filter(
            Q(artist__user=request.user) | Q(client=request.user),
              status='approved',
            event_date__gt=datetime.datetime.now().date()
             ).order_by('event_date','start_time')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingHistoryView(views.APIView):
    pass
