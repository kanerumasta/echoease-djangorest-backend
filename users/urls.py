from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    CustomProviderAuthView,
    VerifyProfileView,
    ProfileView,
    is_profile_complete,
    is_artist,
)

from django.urls import path, re_path



urlpatterns = [
    re_path(r'^o/(?P<provider>\S+)/$', CustomProviderAuthView.as_view()),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('account/', VerifyProfileView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/is-complete', is_profile_complete),
    path('profile/change-image',ProfileView.as_view()),
    path('users/me/is-artist',is_artist),
    
]
