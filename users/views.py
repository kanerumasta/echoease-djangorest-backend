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
from .serializers import VerifyProfileSerializer, ProfileSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import UserAccount, Profile
from django.shortcuts import get_object_or_404
import pytz


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
    def put(self, request):
        try:
            user = request.user
            profile = get_object_or_404(Profile, user = user)
            data = request.data
            if 'dob' in data:
                try:
                    iso_date_str = data['dob']
                    print(iso_date_str)
                    date_obj = datetime.fromisoformat(iso_date_str.replace('Z', '+00:00'))
                    local_tz = pytz.timezone('Asia/Manila')
                    date_obj_utc = date_obj.astimezone(pytz.UTC)
                    print(date_obj_utc)
                    date_obj_local = date_obj_utc.astimezone(local_tz)

                    formatted_date = date_obj.strftime('%Y-%m-%d')
                    data['dob'] = formatted_date
                except ValueError:
                    return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
            print(data)
            serializer = ProfileSerializer(profile, data = request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                profile.is_complete = True
                profile.save()
                return Response(status = status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            print(e)
            return Response({'message':'error occured'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
   

class VerifyProfileView(APIView):

    def put(self, request):
        user = request.user
        try:
            profile = user.profile
            serializer = VerifyProfileSerializer(profile,data = request.data)
        except:
            return Response({'detail':'Profile not found'}, status = status.HTTP_404_NOT_FOUND)
        
        if serializer.is_valid():
            serializer.save()
            user.is_verified = True
            user.save()
            return Response({},status = status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET'])
def is_artist(request):   
    user = request.user
    print(user)
    print(user.is_artist)
    if user.is_artist:
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    return Response({'message':'error'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def is_profile_complete(request):
    user = request.user
    profile = get_object_or_404(Profile, user = user)
    if profile.is_complete:
        return Response(status = status.HTTP_204_NO_CONTENT)
    return Response(status = status.HTTP_400_BAD_REQUEST)

