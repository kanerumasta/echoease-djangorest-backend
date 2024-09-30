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
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 20




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
                time.sleep(1.5)
                return Response(serializer.data, status=status.HTTP_200_OK)
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


@api_view(['GET'])
def clear_all(request):
    pass

