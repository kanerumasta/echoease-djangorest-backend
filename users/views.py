from datetime import datetime
from django.conf import settings
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  ProfileSerializer, UserAccountSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .models import UserAccount, Profile
from django.shortcuts import get_object_or_404
import pytz
from rest_framework.permissions import AllowAny


class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access') # type: ignore
            refresh_token = response.data.get('refresh') # type: ignore
            
            response.set_cookie(
                'access', access_token,
                max_age =settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                secure=settings.AUTH_COOKIE_SECURE,
                path=settings.AUTH_COOKIE_PATH,
                samesite=settings.AUTH_COOKIE_SAMESITE
                
                )
            
            response.set_cookie(
                'refresh', refresh_token,
                max_age =settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                secure=settings.AUTH_COOKIE_SECURE,
                path=settings.AUTH_COOKIE_PATH,
                samesite=settings.AUTH_COOKIE_SAMESITE
                
                )

        return response
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access') # type: ignore
            refresh_token = response.data.get('refresh') # type: ignore

            response.set_cookie(
                'access', access_token,
                max_age =settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                secure=settings.AUTH_COOKIE_SECURE,
                path=settings.AUTH_COOKIE_PATH,
                samesite=settings.AUTH_COOKIE_SAMESITE
                
                )
            
            response.set_cookie(
                'refresh', refresh_token,
                max_age =settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                secure=settings.AUTH_COOKIE_SECURE,
                path=settings.AUTH_COOKIE_PATH,
                samesite=settings.AUTH_COOKIE_SAMESITE
                
                )

        return response   
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args,**kwargs ):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token # type: ignore
        response = super().post(request,*args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access') # type: ignore
            response.set_cookie(
                'access', access_token,
                max_age =settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                secure=settings.AUTH_COOKIE_SECURE,
                path=settings.AUTH_COOKIE_PATH,
                samesite=settings.AUTH_COOKIE_SAMESITE
                
                )
        return response
class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token # type: ignore

        return super().post(request, *args, **kwargs)
class LogoutView(APIView):
    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response
    
class ProfileView(APIView):
    def get(self,request, pk = None):
        if pk:
            user = get_object_or_404(UserAccount, pk = pk)
            profile = get_object_or_404(Profile,user = user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        profile = get_object_or_404(Profile,user = request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        


    def put(self, request):
        try:
            profile = get_object_or_404(Profile, user = request.user)
            serializer = ProfileSerializer(profile, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                profile.is_complete = True
                profile.save()  
                return Response(status = status.HTTP_204_NO_CONTENT)
            print(serializer.errors)
            return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request):
        try:
            user = request.user
            profile = get_object_or_404(Profile, user = user)
            data = request.data
            serializer = ProfileSerializer(profile,data = data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(status = status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':'error occured'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class UserView(APIView):
    def get(self, request):
        try:
            user = UserAccount.objects.get(pk = request.user.id)
            print('User',user)
            serializer = UserAccountSerializer(user)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message':'unexpected error'}, status = status.HTTP_400_BAD_REQUEST)
        

    #picking role before booking | organizer | regular | bar owner
    def patch(self, request):
        print(request.data)
        serializer = UserAccountSerializer(request.user,data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            request.user.is_roled = True
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        print(serializer.errors)

        return Response(status=status.HTTP_400_BAD_REQUEST)
        


        


@api_view(['GET'])
def is_artist(request):
    user = request.user
    if user.is_artist:
        return Response(status=status.HTTP_200_OK)
    return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def check_email(request, email):
    user = get_object_or_404(UserAccount, email = email)
    if user:
        return Response({'exists':True}, status=status.HTTP_200_OK)
    return Response({'exists':False},status=status.HTTP_200_OK)
    