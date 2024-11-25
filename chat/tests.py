from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from datetime import datetime
from django.utils import timezone

User = get_user_model()

class ConversationModelTestCase(TestCase):

    def setUp(self):
        # Create Users without username field
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password"
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="password"
        )

        # Create Conversation
        self.conversation = Conversation.objects.create()

        # Add participants to the conversation
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_conversation(self):
        # Verify that the conversation was created and the participants are set correctly
        self.assertEqual(self.conversation.participants.count(), 2)
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())

    def test_conversation_str_method(self):
        # Verify that the string representation of the conversation is its UUID
        self.assertEqual(str(self.conversation), str(self.conversation.code))

    def test_last_message_property(self):
        # Create messages for the conversation
        message1 = Message.objects.create(
            conversation=self.conversation,
            content="Hello!",
            author=self.user1,
            is_read=True
        )
        message2 = Message.objects.create(
            conversation=self.conversation,
            content="Hi there!",
            author=self.user2,
            is_read=False
        )

        # Verify that the last message is returned correctly
        self.assertEqual(self.conversation.last_message, "Hi there!")

    def test_last_message_time_property(self):
        # Create messages for the conversation
        message1 = Message.objects.create(
            conversation=self.conversation,
            content="Hello!",
            author=self.user1,
            created_at=timezone.make_aware(datetime(2024, 11, 23, 10, 0))
        )
        message2 = Message.objects.create(
            conversation=self.conversation,
            content="Hi there!",
            author=self.user2,
            created_at=timezone.make_aware(datetime(2024, 11, 23, 10, 30))
        )

        # Verify the last message time property returns the correct time format
        print(self.conversation.last_message_time)
        self.assertEqual(self.conversation.last_message_time, "10:30 AM")
