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
from .serializers import VerifyProfileSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import UserAccount
from django.shortcuts import get_object_or_404



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
        
            


# @api_view('GET')
# def get_profile_pic(request, email):
#     user = get_object_or_404(UserAccount, email = email)
#     # if user:
#     #     user.