from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import pagination
from rest_framework import status
from rest_framework.response import Response
from .models import Transaction
from django.shortcuts import get_object_or_404
from artists.models import Artist
from .serializers import TransactionSerializer

class TransactionPagination(pagination.PageNumberPagination):
    page_size = 5
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



class TransactionView(APIView):
    pagination_class = TransactionPagination
    def get(self, request,pk=None, *args, **kwargs):
        if pk:
            transaction = get_object_or_404(Transaction, pk=pk)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.user.role == 'artist':
            artist = get_object_or_404(Artist, user = request.user)
            transactions = Transaction.objects.filter(artist=artist)
        transactions = Transaction.objects.filter(client = request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(transactions, request)
        serializer = TransactionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
