from django.urls import path
from .views import (
    BookingView,
    BookingCancelView,
    BookingConfirmView,
    BookingRejectView,
    PendingPaymentsView,
    UpcomingEventsView,
    BookingDetailView,
    BookingPDFView
)


urlpatterns = [
    path('', BookingView.as_view()),
    path('<int:id>',BookingDetailView.as_view()),
    path('<int:id>/pdf',BookingPDFView.as_view()),
    path('<int:id>/confirm',BookingConfirmView.as_view()),
    path('<int:id>/reject',BookingRejectView.as_view()),
    path('<int:id>/cancel',BookingCancelView.as_view()),
    path('pending-payments',PendingPaymentsView.as_view()),
    path('upcoming-events',UpcomingEventsView.as_view()),
]
