from django.urls import path
from .views import DashboardView,user_detail,suspend_user,decrease_reputation_score, DisputesView, DisputeDetailView, refund_payment_view, resolve_dispute,unsuspend_user, warn_user,reported_portfolio_items,portfolio_item_detail,delete_portfolio_item,ignore_portfolio_item,revenue_details,admin_users_management,create_admin_view,edit_admin_view,delete_admin_view, chat_support_list, conversation_detail

urlpatterns = [
    path('admin-dashboard', DashboardView.as_view(), name='admin-dashboard'),
    path('disputes', DisputesView.as_view(), name='disputes'),
    path('detail/<int:dispute_id>', DisputeDetailView.as_view(), name='dispute_detail'),
 path('disputes/<int:dispute_id>/refund/', refund_payment_view, name='refund_payment'),
  path('dispute/<int:dispute_id>/resolve/', resolve_dispute, name='resolve_dispute'),
  path('dispute/<int:dispute_id>/reputation_decrease/', decrease_reputation_score, name='decrease_reputation'),
  path('user/<int:user_id>/', user_detail, name='user_detail'),
  path('users/<int:user_id>/suspend/', suspend_user, name='suspend_user'),
  path('users/<int:user_id>/unsuspend/',unsuspend_user, name='unsuspend_user'),
  path('users/<int:user_id>/warn/',warn_user, name='warn_user'),
    path('reported-items/',reported_portfolio_items, name='reported_portfolio_items'),
    path('reported-items/<int:item_id>/',portfolio_item_detail, name='reported_portfolio_item_detail'),
     path('portfolio-item/<int:item_id>/delete/', delete_portfolio_item, name='delete_portfolio_item'),
    path('portfolio-item/<int:item_id>/ignore/', ignore_portfolio_item, name='ignore_portfolio_item'),
     path('revenue/', revenue_details, name='revenue-details'),
      path('admin_users/', admin_users_management, name='admin_users'),  # Manage Admin Users
    path('create_admin/', create_admin_view, name='create_admin'),  # Create Admin User
    path('edit_admin/<int:user_id>/',edit_admin_view, name='edit_admin'),  # Edit Admin User
    path('delete_admin/<int:user_id>/',delete_admin_view, name='delete_admin'),  # Delete Admin User
    path('chats/',chat_support_list, name='chat_list'),
    path('chats/<str:conversation_code>/', conversation_detail, name='chat_detail'),
]
