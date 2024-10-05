from django.urls import path
from .views import (
    BookingView,
    BookingCancelView,
    BookingConfirmView,
    BookingRejectView
)


urlpatterns = [
    path('', BookingView.as_view()),
    path('<int:id>',BookingView.as_view()),
    path('<int:id>/confirm',BookingConfirmView.as_view()),
    path('<int:id>/reject',BookingRejectView.as_view()),
    path('<int:id>/cancel',BookingCancelView.as_view()),
]
