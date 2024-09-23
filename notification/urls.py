from django.urls import path
from .views import (
    NotificationView,


)

urlpatterns = [
    path('',NotificationView.as_view()),
    path('<int:id>', NotificationView.as_view()),
    path('<int:notif_id>/read', NotificationView.as_view()),
    path('<int:notif_id>/delete', NotificationView.as_view()),
]