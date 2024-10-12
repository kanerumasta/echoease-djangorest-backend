from django.shortcuts import render
from django.db.models import Q
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingSerializer
from django.shortcuts import get_object_or_404
from .models import Booking
from notification.models import Notification
from .permissions import IsInvolved
from rest_framework.decorators  import permission_classes
from .utils import (
    create_new_booking_notification,
    create_booking_confirmation_notification,
    create_booking_rejected_notification,
    create_booking_cancelled_notification
)
from django.utils import timezone
import datetime

class BookingView(views.APIView):
    def post(self, request):
        print(request.data)
        serializer = BookingSerializer(data = request.data)
        try:
            if serializer.is_valid():
                booking = serializer.save(client = request.user)
                booking_id = booking.id
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
        sort = request.query_params.get('sort')
        bookings = Booking.objects.filter(Q(client = request.user)|Q(artist__user = request.user))
        if status_filter:
            bookings = bookings.filter(status = status_filter)
        if sort == 'date':
            bookings = bookings.order_by('event_date','start_time')
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
    def get(self, request):
        bookings = Booking.objects.filter(
            Q(artist__user=request.user) | Q(client=request.user),
              status='approved',
                event_date__lt=datetime.datetime.now().date(),
                payment__isnull=True
             )
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
