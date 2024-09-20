from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from .serializers import ClientDisputeSerializer, ArtistDisputeSerializer
from rest_framework import status
from rest_framework.response import Response
from booking.models import Booking
from artists.models import Artist

# Create your views here.


class ClientDisputeView(APIView):
    def get(self, request, pk=None):
        pass

    def post(self, request):
        if str(request.user.id) != request.data.get('client'):
            return Response({'message':'user and client do not match'}, status=status.HTTP_400_BAD_REQUEST)
        booking = get_object_or_404(Booking, pk = request.data.get('booking'))
        print(booking.client)
        print(request.user)
        if booking.client != request.user:
            return Response({'message':'user is not the booking client'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ClientDisputeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ArtistDisputeView(APIView):
    def get(self, request, pk=None):
        pass

    def post(self, request):
        artist = get_object_or_404(Artist, pk=request.data.get('artist'))
        if not artist.user ==request.user:
            return Response({'message':'user and artists user do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking = get_object_or_404(Booking, pk = request.data.get('booking'))
        if not booking.artist == artist:
            return Response({'message':'booking artist and requester artist do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not booking.status == 'approved':
            return Response({'message':'Booking is not yet confirmed'}, status = status.HTTP_400_BAD_REQUEST)
        
        serializer = ArtistDisputeSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    