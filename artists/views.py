from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import AnonymousUser

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from rest_framework.exceptions import ValidationError
from .models import ArtistApplication, Artist, Genre, IDType
from .permissions import IsArtist


from .serializers import (
                            ArtistApplicationSerializer,
                            ArtistSerializer ,
                            PortfolioItemSerializer,
                            PortfolioSerializer,
                            GenreSerializer,
                            IDTypeSerializer,
                            RateSerializer
                          )
from .models import Artist, PortfolioItem, Portfolio, Rate


class ArtistView(APIView):
     #ADD ISVERIFIED USER HERE

    def get_permissions(self):
        print(self.request.method)
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

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
        current = request.GET.get('current', 'False').lower() == 'true'
        print(current)
        if current:
            user = request.user

            artist = get_object_or_404(Artist, user = user)
            serializer = ArtistSerializer(artist)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
    permission_classes=[AllowAny]
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
        print(request.data)
        serializer = PortfolioItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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

        #search params to only check if current user has artist application already
        check = request.GET.get('check','False').lower() == 'true'
        if check:
            application = ArtistApplication.objects.filter(user = request.user)
            if application.exists():
                return Response({'message':'You already have an artist application'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
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
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            print(serializer.errors)
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


class IDTypesView(APIView):

    def get_permissions(self):
        print(self.request.method)
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()
    def get(self, request, pk=None):
        if pk:
            id_type = get_object_or_404(IDType, pk=pk)
            serializer = IDTypeSerializer(id_type)
            return Response(serializer.data, status=status.HTTP_200_OK)
        accepted_ids = get_list_or_404(IDType)
        serializer = IDTypeSerializer(accepted_ids, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RateView(APIView):
    def get(self, request, id):
        artist = get_object_or_404(Artist, id=id)
        rates = artist.artist_rates.all()
        serializer = RateSerializer(rates,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



    def post(self, request):
        print(request.data)
        serializer = RateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def follow(request):
    user = request.user
    artist = get_object_or_404(Artist, pk=request.data.get("artist"))
    if user not in artist.followers.all():
        artist.followers.add(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def unfollow(request):
    user = request.user
    artist = get_object_or_404(Artist, pk=request.data.get("artist"))
    if user in artist.followers.all():
        artist.followers.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)
