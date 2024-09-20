from django.shortcuts import render
from django.db.models import Q
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingSerializer
from django.shortcuts import get_list_or_404, get_object_or_404
from .models import Booking
from .permissions import IsInvolved
from rest_framework.decorators  import permission_classes

class BookingView(views.APIView):
    def post(self, request):
        print(request.data)
        serializer = BookingSerializer(data = request.data)
        try:      
            if serializer.is_valid():
                serializer.save(client = request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @permission_classes([IsInvolved])
    def get(self, request, pk=None):
        user = request.user
        if pk:
            booking = get_object_or_404(Booking, pk=pk)
            self.check_object_permissions(request, booking)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        bookings = Booking.objects.filter(Q(client=user)|Q(artist__user = user))
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class BookingHistoryView(views.APIView):
    pass
    
