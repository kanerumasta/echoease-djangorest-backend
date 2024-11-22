from django.urls import path
from .views import *
urlpatterns=[

    path('blocked-conversations',BlockUserView.as_view()),
    path('blocked-conversations/<str:conversation_code>/<int:user_id>', BlockUserView.as_view()),
    path('unblock-conversation',UnblockUserView.as_view()),
    path('unread-messages-count', get_unread_messages_count),
    path('conversations', ConversationsView.as_view()),
    path('conversations/<str:code>', ConversationDetailView.as_view()),
    path('conversations/<str:code>/read',set_conversation_read), #mark all conversation as read
    path('<str:code>', ConversationView.as_view(),name='conversation-detail'),
    path('slug/<str:slug>', ConversationView.as_view()),
    path('admin-chat/', AdminChatSupportView.as_view(), name='admin_chat_support'),
    # path('<str:code>/messages', MessagesView.as_view(),name='message-list'),
]
