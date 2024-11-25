from django.urls import path
from .views import (
    NotificationView,
    NotificationsView,
    mark_all_as_read,
    clear_all_old_notifications


)

urlpatterns = [
    path('',NotificationView.as_view()),
    path('<int:id>', NotificationView.as_view()),
    path('<int:notif_id>/read', NotificationView.as_view()),
    path('<int:notif_id>/delete', NotificationView.as_view()),
    path('mark-all-as-read',mark_all_as_read ),
    path('clear-all-old-notifications', clear_all_old_notifications)
]
