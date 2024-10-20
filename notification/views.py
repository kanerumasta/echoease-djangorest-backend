from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import Notification
import time

from .serializers import (
    NotificationSerializer
)

class NotificationPagination(pagination.PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'count': self.page.paginator.count,
            'results': data
        },status=status.HTTP_200_OK)





class NotificationView(APIView):
    pagination_class = NotificationPagination

    def get(self, request, id=None):
        new = request.GET.get('new', 'False').lower() == 'true'
        old = request.GET.get('old', 'False').lower() == 'true'
        count = request.GET.get('count', 'False').lower() == 'true'
        if new:
            try:
                notifications = Notification.objects.filter(Q(user = request.user)&Q(is_read = False))
                if count:
                    unread_count = notifications.count()
                    return Response({'notifications_count': unread_count}, status=status.HTTP_200_OK)
                serializer = NotificationSerializer(notifications, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({'message':'Error fetching new notifications.'},status=status.HTTP_400_BAD_REQUEST)
        if new:
            try:
                notifications = Notification.objects.filter(Q(user = request.user)&Q(is_read = False))
                serializer = NotificationSerializer(notifications, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({'message':'Error fetching new notifications.'},status=status.HTTP_400_BAD_REQUEST)
        if old:
            try:
                notifications = Notification.objects.filter(Q(user = request.user)&Q(is_read = True))
                paginator = self.pagination_class()
                paginated_notifications = paginator.paginate_queryset(notifications, request)

                serializer = NotificationSerializer(paginated_notifications, many=True)

                return paginator.get_paginated_response(serializer.data)
            except Exception as e:
                print(e)
                return Response({'message':'Error fetching old notifications.'},status=status.HTTP_400_BAD_REQUEST)
        if id:
            notification = get_object_or_404(Notification, id = id)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            notifications = Notification.objects.filter(user = request.user)
        except Exception as e:
            print(e)
            return Response({'message':'Error fetching notifications'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, notif_id):
        notication = get_object_or_404(Notification, id=notif_id)
        notication.read()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self,request, notif_id):
        notification = get_object_or_404(Notification, id=notif_id)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationsView(APIView):
    def get(self, request, *args, **kwargs):
        notifications  = Notification.objects.filter(user = request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def mark_all_as_read(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, is_read=False)
    for notification in notifications:
        notification.read()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def clear_all_old_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, is_read=True)
    notifications.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
