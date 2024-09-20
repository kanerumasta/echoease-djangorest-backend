from django.urls import path
from .views import BookingView


urlpatterns = [
    path('', BookingView.as_view()),
    path('<int:pk>',BookingView.as_view()),
]