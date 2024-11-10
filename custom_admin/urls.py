from django.urls import path
from .views import DashboardView

urlpatterns = [
    path('admin-dashboard', DashboardView.as_view(), name='admin-dashboard'),
]
