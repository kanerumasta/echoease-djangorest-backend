from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    CustomProviderAuthView,
    ProfileView,
    UserView,
    is_artist
)

from django.urls import path, re_path



urlpatterns = [
    re_path(r'^o/(?P<provider>\S+)/$', CustomProviderAuthView.as_view()),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),

    #######################################################

    path('profile/', ProfileView.as_view()),
    path('profile/<int:pk>', ProfileView.as_view()),
    path('profile/change-image',ProfileView.as_view()),
    path('whoami/', UserView.as_view()),
    path('is-artist/',is_artist),
    
]
