from django.urls import path
from .views import *
urlpatterns=[
    path('conversations', ConversationsView.as_view()),
    path('conversations/<str:code>', ConversationDetailView.as_view()),
    path('<str:code>', ConversationView.as_view(),name='conversation-detail'),
    path('slug/<str:slug>', ConversationView.as_view()),
    # path('<str:code>/messages', MessagesView.as_view(),name='message-list'),
]
