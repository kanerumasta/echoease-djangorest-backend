from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from .models import ArtistApplication, Artist
from .permissions import IsArtist


from .serializers import (
                            ArtistApplicationSerializer,
                            ArtistSerializer ,
                            PortfolioItemSerializer, 
                            PortfolioSerializer,
                            FollowArtistSerializer,
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
    def post(self, request):
        #check user is verified here
        try:
        
            user = request.user
            print(request.data)
            serializer = ArtistApplicationSerializer(data = request.data)
            if serializer.is_valid(raise_exception = True):
                print(serializer.validated_data)
                serializer.validated_data['user'] = user
                serializer.save()
                return Response({'message':'Your application is in process.'}, status = status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_artist(request):
    user = request.user
    serializer = FollowArtistSerializer(data = request.data)

    try:
        if serializer.is_valid(raise_exception=True):
            artist_id = serializer.validated_data
            artist = get_object_or_404(Artist, id=serializer.validated_data.get('artist_id')) # type: ignore
            if artist and user is not AnonymousUser:
                artist.followers.add(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        print(e)
        print('ERROR:failed to follow artist')
        return Response({'message':'fail to follow artist'}, status= status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def unfollow_artist(request):
    user = request.user
    serializer = FollowArtistSerializer(data = request.data)

    try:
        if serializer.is_valid(raise_exception=True):
            artist_id = serializer.validated_data
            artist = get_object_or_404(Artist, id=serializer.validated_data.get('artist_id')) # type: ignore
            if artist and user is not AnonymousUser:
                artist.followers.remove(user)
                print(artist.followers.count())
                return Response(status=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        print(e)
        print('ERROR:failed to follow artist')
        return Response({'message':'fail to follow artist'}, status= status.HTTP_400_BAD_REQUEST)

        
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsArtist])
def get_my_artist_profile(request):
    try:

        user = request.user
        artist = get_object_or_404(Artist, id = user.id)
        serializer = ArtistSerializer(artist)
        return Response(serializer.data, status = status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'message ':'unexpected error occured'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
