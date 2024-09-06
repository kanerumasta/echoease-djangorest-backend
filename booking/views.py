from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingSerializer

class BookingView(views.APIView):
    def post(self, request):
        serializer = BookingSerializer(data = request.data)
        try:
                
            if serializer.is_valid():
                serializer.save(client = request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
