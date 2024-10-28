from django.urls import path
from .views import DisputeView, DisputeEvidenceView


urlpatterns = [
    path('', DisputeView.as_view()),
    path('<int:booking_id>', DisputeView.as_view()),
    path('evidences', DisputeEvidenceView.as_view()),
]
