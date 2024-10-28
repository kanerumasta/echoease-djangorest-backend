from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from .serializers import (
    DisputeSerializer,
    DisputeEvidenceSerializer
)
from rest_framework import status
from rest_framework.response import Response
from booking.models import Booking
from artists.models import Artist

# Create your views here.


class DisputeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DisputeSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        if booking:
            disputes = booking.disputes.all()
            serializer = DisputeSerializer(disputes,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message':'An error occured'},status=status.HTTP_400_BAD_REQUEST)

class DisputeEvidenceView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DisputeEvidenceSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
