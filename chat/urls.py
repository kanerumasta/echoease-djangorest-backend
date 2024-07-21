from django.urls import path
from .views import *
urlpatterns=[
    path('', ConversationView.as_view(),name='conversation-list'),
    path('<str:code>', ConversationView.as_view(),name='conversation-detail'),
    path('<str:code>/messages', MessagesView.as_view(),name='message-list'),

]