from django.urls import path
from .views import DashboardView,decrease_reputation_score, DisputesView, DisputeDetailView, refund_payment_view, resolve_dispute

urlpatterns = [
    path('admin-dashboard', DashboardView.as_view(), name='admin-dashboard'),
    path('disputes', DisputesView.as_view(), name='disputes'),
    path('detail/<int:dispute_id>', DisputeDetailView.as_view(), name='dispute_detail'),
 path('disputes/<int:dispute_id>/refund/', refund_payment_view, name='refund_payment'),
  path('dispute/<int:dispute_id>/resolve/', resolve_dispute, name='resolve_dispute'),
  path('dispute/<int:dispute_id>/reputation_decrease/', decrease_reputation_score, name='decrease_reputation'),
]
