from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import ReviewsSerializer
from rest_framework import status, pagination
from rest_framework.response import Response
from .models import Review
from artists.models import Artist
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from booking.models import Booking

class ReviewsPagination(pagination.PageNumberPagination):
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

class ReviewsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReviewsSerializer(data = request.data)
        booking = get_object_or_404(Booking, pk = request.data.get('booking'))
        print(request.data)
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

class ArtistListReview(APIView):
    pagination_class = ReviewsPagination
    def get(self,request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        reviews = Review.objects.filter(booking__artist=artist)
        paginator = self.pagination_class()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewsSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)
