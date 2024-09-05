from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from .models import ArtistApplication, Artist, Genre
from .permissions import IsArtist


from .serializers import (
                            ArtistApplicationSerializer,
                            ArtistSerializer ,
                            PortfolioItemSerializer, 
                            PortfolioSerializer,
                            GenreSerializer,
                          )
from .models import Artist, PortfolioItem, Portfolio


class ArtistView(APIView):
    permission_classes = [IsAuthenticated] #ADD ISVERIFIED USER HERE
    def post(self, request):
        data = request.data
        serializer = ArtistApplicationSerializer(data = data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
        except ValidationError as e:
            print(e)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

    def get(self, request,pk=None, slug=None):
        if slug:
            artist = get_object_or_404(Artist, slug = slug)
            serializer = ArtistSerializer(artist)
            return Response(serializer.data, status = status.HTTP_200_OK)
        if pk:
            artist = get_object_or_404(Artist, id = pk)
            serializer = ArtistSerializer(artist)
            return Response(serializer.data, status = status.HTTP_200_OK)
        else:
            artist_list = Artist.objects.all()
            serializer = ArtistSerializer(artist_list, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)

            
class PortfolioView(APIView):
    permission_classes=[IsArtist, IsAuthenticated]

    def get(self, request, artist_id):

        artist = get_object_or_404(Artist, id=artist_id)
        try:
            portfolio = artist.portfolio # type: ignore
        except Portfolio.DoesNotExist:
            return Response({'message':'Portfolio of this user does not exists'}, status = status.HTTP_404_NOT_FOUND)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data, status = status.HTTP_200_OK)
    

class PortfolioItemView(APIView):
    permission_classes=[IsArtist, IsAuthenticated]

    def post(self, request):
        artist = Artist.objects.get(user = request.user)
        portfolio = artist.portfolio # type: ignore
        data = request.data.copy()
        data['portfolio'] = portfolio.id
        serializer = PortfolioItemSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def put(self, request, id):
        if id:
            portfolio_item = get_object_or_404(PortfolioItem, id=id)
            serializer = PortfolioItemSerializer(instance=portfolio_item,data = request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
class ArtistApplicationView(APIView):
    #FOR ADMIN ONLY
    def get(self, request):
        try:
            applications = ArtistApplication.objects.all()
            serializer = ArtistApplicationSerializer(applications, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        #check user is verified here
        try:
            user = request.user
            print(request.data)
            application = ArtistApplication.objects.filter(user = user)
            if application.exists():
                return Response({'message':'You already have an artist application.'},status = status.HTTP_409_CONFLICT)
            serializer = ArtistApplicationSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({'message':'Your application is in process.'}, status = status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GenreView(APIView):
    def get(self, request, id=None):
       
        if id:
            genre = get_object_or_404(Genre, id = id)
            serializer = GenreSerializer(genre)
            return Response(serializer.data, status = status.HTTP_200_OK)
        
        try:
            genres = Genre.objects.all()
            serializer = GenreSerializer(genres, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


