
from django.conf import settings
import requests
from users.models import BusinessBoost
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  ProfileSerializer, UserAccountSerializer, ChangeNameSerializer
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
        print(request.data)
        try:
            user = request.user
            profile = get_object_or_404(Profile, user = user)
            data = request.data
            serializer = ProfileSerializer(profile,data = data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(status = status.HTTP_200_OK)
            print(serializer.errors)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':'error occured'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(APIView):
    def get(self, request, id = None):
        if id:
            user = get_object_or_404(UserAccount, id=id)
            if user.is_staff or user.is_superuser or not user.is_active:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = UserAccountSerializer(user, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            user = UserAccount.objects.get(pk = request.user.id)
            print('User',user)
            serializer = UserAccountSerializer(user,context={'request':request})
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message':'unexpected error'}, status = status.HTTP_400_BAD_REQUEST)


    #picking role before booking | organizer | regular | bar owner
    def patch(self, request):
        serializer = UserAccountSerializer(request.user,data = request.data, partial = True, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            request.user.is_roled = True
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        print(serializer.errors)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateUserView(APIView):
    def patch(self, request):
        user = request.user
        serializer = ChangeNameSerializer(user,data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetView(APIView):
    def post(self, request):
        try:
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')

            user = request.user

            if new_password and old_password:

                if not user.check_password(old_password):
                    return Response({'message':'password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                print('old and new password')
                return Response({'message':'old password and new password is required'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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

@api_view(['POST'])
def initiate_boost_auth(request):
    redirect_uri = request.data.get('redirect_uri')
    if not redirect_uri:
        return Response({'error':'redirect_uri is required'},status = status.HTTP_400_BAD_REQUEST)

    url = f'https://www.facebook.com/v13.0/dialog/oauth?client_id={settings.FACEBOOK_CLIENT_ID}&redirect_uri={redirect_uri}&scope=pages_manage_posts,publish_pages,pages_show_list,pages_read_engagement'

    return Response({'url':url}, status = status.HTTP_200_OK)


@api_view(['POST'])
def authorize_business_boost(request):
    user = request.user
    code = request.data.get('code')
    redirect_uri = request.data.get('redirect_uri')

    if not code or not redirect_uri:
        return Response({'error':'code and redirect_uri are required'},status = status.HTTP_400_BAD_REQUEST)

    #exchange code with app access token
    print('client id', settings.FACEBOOK_CLIENT_ID)
    exchange_url = f"https://graph.facebook.com/v13.0/oauth/access_token?client_id={settings.FACEBOOK_CLIENT_ID}&redirect_uri={redirect_uri}&client_secret={settings.FACEBOOK_CLIENT_SECRET}&code={code}"

    print('URL', exchange_url)

    response = requests.get(exchange_url)
    response_data = response.json()
    print(response_data)
    access_token = response_data.get('access_token')
    if not access_token:
        return Response({'error':'Failed to exchange code for access token'},status = status.HTTP_400_BAD_REQUEST)

    #fetch facebook page details (page_id, page_name, etc. weewww)
    page_url = f"https://graph.facebook.com/v13.0/me/accounts?access_token={access_token}"
    page_response = requests.get(page_url)
    page_data = page_response.json()
    if not page_data or 'data' not in page_data:
        return Response({'error':'Failed to fetch page details'},status = status.HTTP_400_BAD_REQUEST)
    #extract page details from returned data
    page_id = page_data['data'][0]['id']
    page_name = page_data['data'][0]['name']
    page_access_token = page_data['data'][0]['access_token']

    try:
        #create business boost record if it doesn't exist
        business_boost, created = BusinessBoost.objects.get_or_create(
            user = user,
            defaults={
                'page_id': page_id,
                'page_name': page_name,
                'is_active': True,
            }
        )
        if not created:
            business_boost.page_id = page_id
            business_boost.page_name = page_name
            business_boost.is_active = True
        business_boost.set_access_token(page_access_token)
        user.business_boost_opted = True
        business_boost.save()
        user.save()
        return Response({'message':'Success'}, status = status.HTTP_200_OK)
    except Exception as e:
        return Response({'error':'Failed to create business boost record'},status = status.HTTP_500_INTERNAL_SERVER_ERROR)
