from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import ReviewsSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import Review
from artists.models import Artist
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from booking.models import Booking

class ReviewsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReviewsSerializer(data = request.data)
        booking = get_object_or_404(Booking, pk = request.data.get('booking'))
        if serializer.is_valid():
            serializer.save()
            booking.is_reviewed = True
            booking.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArtistReviews(APIView):
    def get(self, request,artist_id, *args, **kwargs):
        artist = get_object_or_404(Artist, pk = artist_id)
        reviews = Review.objects.filter(booking__artist=artist).aggregate(Avg('rating'))
        print(reviews)
        return Response(reviews, status=status.HTTP_200_OK)
