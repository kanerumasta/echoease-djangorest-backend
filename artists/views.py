from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q,Avg, Count, When, IntegerField, Case
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
import requests
import time

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from rest_framework.exceptions import ValidationError
from .models import (ArtistApplication, Artist, Genre, IDType, ConnectionRequest, PortfolioItemMedia)
from booking.models import Booking
from .permissions import IsArtist
from django.utils import timezone
from users.serializers import UserAccountSerializer
from django.db.models import Min
from notification.utils import notify_new_sent_request, notify_accepted_request
import time
from notification.models import Notification
from django.core.mail import send_mail



from .serializers import (
                            ArtistApplicationSerializer,
                            ArtistSerializer ,
                            PortfolioItemSerializer,
                            PortfolioSerializer,
                            GenreSerializer,
                            IDTypeSerializer,
                            RateSerializer,
                            ConnectionRequestSerializer,
                            ArtistConnectionsSerializer,
                            PortfolioItemMediaSerializer,
                            RecommendedArtistSerializer,

                          )
from .models import Artist, PortfolioItem, Portfolio, Rate

class ArtistPagination(pagination.PageNumberPagination):
    page_size = 8
    max_page_size=20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
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

class ArtistView(APIView):
    pagination_class = ArtistPagination
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def patch(self, request):
        artist_id = request.data.get('artist_id')
        artist = get_object_or_404(Artist, id = artist_id)
        serializer = ArtistSerializer(artist, data = request.data,partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        data = request.data
        serializer = ArtistApplicationSerializer(data = data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
        except ValidationError as e:
            print(e)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, slug=None):
        current = request.GET.get('current', 'False').lower() == 'true'

        if current:
            user = request.user
            artist = get_object_or_404(Artist, user=user, user__is_suspended=False, user__is_deactivated=False)
            serializer = ArtistSerializer(artist, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if slug:
            artist = get_object_or_404(Artist, slug=slug, user__is_suspended=False, user__is_deactivated=False)
            serializer = ArtistSerializer(artist, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            artist = get_object_or_404(Artist, id=pk, user__is_suspended=False, user__is_deactivated=False)
            serializer = ArtistSerializer(artist, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            min_price = request.GET.get('min_price', None)
            max_price = request.GET.get('max_price', None)
            q = request.GET.get('q', None)
            genres = request.GET.get('genres', None)
            category = request.GET.get('category', None)

            artist_list = Artist.objects.filter(
                user__is_suspended=False,
                user__is_deactivated=False
            ).annotate(
                total_reviews=Count('bookings__reviews'),
                total_bookings=Count('bookings'),
                average_rating=Avg('bookings__reviews__rating'),
                genre_count=Count('genres'),
            )

            if q is not None:
                search_terms = q.split()
                query = Q()
                for term in search_terms:
                    query |= (
                        Q(stage_name__icontains=term) |
                        Q(user__first_name__icontains=term) |
                        Q(user__last_name__icontains=term)
                    )
                artist_list = artist_list.filter(query)

            if category:
                if category == 'new':
                     # For "new", filter artists with no bookings, order randomly, and limit to 10
                    artist_list = artist_list.filter(total_bookings=0).order_by('?')[:10]
                else:
                    artist_list = artist_list.annotate(
                        reputation_priority=Case(
                            When(user__reputation_score__gte=85, then=0),
                            default=1,
                            output_field=IntegerField()
                        )
                    ).order_by(
                        '-user__reputation_score',     # Users with a higher reputation score first
                        '-total_reviews',             # Artists with more bookings first
                        '-average_rating',             # Higher ratings first
                        'reputation_priority'         # Ensure high-reputation artists come before others if the score is 85 or more
                    )

                if category == 'top':
                    artist_list = artist_list.filter(
                        created_at__lte=timezone.now() - timezone.timedelta(days=3)
                    ).filter(
                        total_reviews__gte=5,
                        average_rating__gte=4.0,
                        user__reputation_score__gte=85
                    ).order_by('-total_reviews', '-average_rating', '-user__reputation_score')

                elif category == 'versatile':
                    artist_list = artist_list.filter(genre_count__gte=3).order_by('-genre_count')

                elif category == 'near':
                    if request.user.is_authenticated:
                        municipality = request.user.profile.municipality
                        artist_list = artist_list.filter(user__profile__municipality=municipality).exclude(user=request.user)

            if genres is not None:
                genres_list = genres.split(',')
                artist_list = artist_list.filter(genres__in=genres_list).distinct()

            if min_price is not None and max_price is not None:
                annotated_artists = artist_list.annotate(min_rate=Min('artist_rates__amount'))
                artist_list = annotated_artists.filter(min_rate__gte=min_price, min_rate__lte=max_price)

            paginator = self.pagination_class()
            paginated_artists = paginator.paginate_queryset(artist_list, request)
            serializer = ArtistSerializer(paginated_artists, many=True, context={'request': request})

            return paginator.get_paginated_response(serializer.data)

    # def get(self, request,pk=None, slug=None):

    #     current = request.GET.get('current', 'False').lower() == 'true'
    #     if current:
    #         user = request.user
    #         artist = get_object_or_404(Artist, user = user,user__is_suspended = False,user__is_deactivated=False)
    #         serializer = ArtistSerializer(artist,context={'request':request})
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     if slug:
    #         artist = get_object_or_404(Artist, slug = slug,user__is_suspended = False,user__is_deactivated=False)
    #         serializer = ArtistSerializer(artist,context={'request':request})
    #         return Response(serializer.data, status = status.HTTP_200_OK)
    #     if pk:
    #         artist = get_object_or_404(Artist, id = pk, user__is_suspended=False, user__is_deactivated=False)
    #         serializer = ArtistSerializer(artist,context={'request':request})
    #         return Response(serializer.data, status = status.HTTP_200_OK)
    #     else:
    #         min_price = request.GET.get('min_price', None)
    #         max_price = request.GET.get('max_price',None)
    #         q = request.GET.get('q', None)
    #         genres = request.GET.get('genres',None)
    #         category = request.GET.get('category', None)

    #         artist_list = Artist.objects.filter(user__is_suspended=False, user__is_deactivated=False).annotate(
    #                     total_reviews = Count('bookings__reviews'),
    #                     average_rating = Avg('bookings__reviews__rating'),
    #                     genre_count=Count('genres'),
    #                 )
    #         if q is not None:
    #             search_terms = q.split()
    #             query = Q()
    #             for term in search_terms:
    #                 query |= (
    #                     Q(stage_name__icontains=term) |
    #                     Q(user__first_name__icontains=term) |
    #                     Q(user__last_name__icontains=term)
    #                 )

    #             artist_list = artist_list.filter(query)



    #         if category:
    #             if category == 'new':
    #                 artist_list = artist_list.filter().order_by('created_at')
    #             if category == 'top':
    #                 artist_list = artist_list.filter(
    #                     created_at__lte = timezone.now() - timezone.timedelta(days=3)
    #                 ).filter(
    #                     total_bookings__gte=5,
    #                     average_rating__gte=4.0,
    #                     user__reputation_score__gte=85
    #                 ).order_by('-total_bookings', '-average_rating','-user__reputation_score')
    #             if category == 'versatile':
    #                 artist_list = artist_list.filter(genre_count__gte=3).order_by('-genre_count',)
    #             if category == 'near':
    #                 if request.user.is_authenticated:
    #                     municipality = request.user.profile.municipality
    #                     artist_list = artist_list.filter(user__profile__municipality=municipality).exclude(user=request.user)

    #         if genres is not None:
    #             genres_list = genres.split(',')

    #             artist_list = artist_list.filter(
    #                 genres__in=genres_list
    #             ).distinct()

    #         if min_price is not None and max_price is not None:
    #             annotated_artists = artist_list.annotate(min_rate=Min('artist_rates__amount'))
    #             artist_list = annotated_artists.filter(min_rate__gte=min_price, min_rate__lte=max_price)

    #         artist_list = artist_list.annotate(
    #             reputation_priority = Case(
    #                 When(user__reputation_score__gte=85,then=0),
    #                 default=1,
    #                 output_field=IntegerField()
    #             )
    #         ).order_by('-total_bookings','-average_rating','reputation_priority','-user__reputation_score')


    #         paginator = self.pagination_class()
    #         paginated_artists = paginator.paginate_queryset(artist_list, request)
    #         serializer = ArtistSerializer(paginated_artists, many=True, context={'request':request})

    #         return paginator.get_paginated_response(serializer.data)



class PortfolioView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        try:
            portfolio = artist.portfolio # type: ignore
        except Portfolio.DoesNotExist:
            return Response({'message':'Portfolio of this user does not exists'}, status = status.HTTP_404_NOT_FOUND)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data, status = status.HTTP_200_OK)


class PortfolioItemView(APIView):
    permission_classes=[IsArtist, IsAuthenticated]

    def post(self, request):
        serializer = PortfolioItemSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id):
        if id:
            portfolio_item = get_object_or_404(PortfolioItem, id=id)
            serializer = PortfolioItemSerializer(instance=portfolio_item,data = request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        portfolio_item = get_object_or_404(PortfolioItem, id=id)
        portfolio_item.delete()
        return Response(status=status.HTTP_200_OK)

class PortfolioItemMediaView(APIView):
    def post(self, request):
        serializer = PortfolioItemMediaSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        media = get_object_or_404(PortfolioItemMedia, id=id)
        media.delete()
        return Response({'message':'media deleted successfully'}, status=status.HTTP_200_OK)

#upload portfolio by artist
class SamplePortfolioItemView(APIView):
    def post(self, request):
        user = request.user
        artist = get_object_or_404(Artist, user = user)
        portfolio = artist.portfolio
        if not portfolio:
            return Response({'message':'portfolio not found'}, status=status.HTTP_404_NOT_FOUND)
        item = PortfolioItem.objects.create(
            title = "Sample Videos",
            description = "These are my sample videos.",
            portfolio = portfolio
        )
        serializer = PortfolioItemSerializer(item)
        return Response(serializer.data, status = status.HTTP_201_CREATED)


class ArtistApplicationView(APIView):
    #FOR ADMIN ONLY
    def get(self, request):
        #search params to only check if current user has artist application already
        check = request.GET.get('check','False').lower() == 'true'
        if check:
            application = ArtistApplication.objects.filter(user = request.user)
            if application.exists():
                return Response({'message':'You already have an artist application'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            applications = ArtistApplication.objects.all()
            serializer = ArtistApplicationSerializer(applications, many = True,context={'request':request})
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request):
    #     #check user is verified here
    #     try:
    #         user = request.user
    #         application = ArtistApplication.objects.filter(user = user)
    #         if application.exists():
    #             return Response({'message':'You already have an artist application.'},status = status.HTTP_409_CONFLICT)
    #         serializer = ArtistApplicationSerializer(data = request.data,context={'request':request})
    #         if serializer.is_valid():
    #             serializer.save(user=user)
    #             return Response(serializer.data, status = status.HTTP_201_CREATED)
    #         print(serializer.errors)
    #         return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         print(e)
    #         return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        #check user is verified here
        try:
            user = request.user
            artist = Artist.objects.filter(user = user)
            if artist.exists():
                return Response({'message':'Youre already an artist.'},status = status.HTTP_409_CONFLICT)
            serializer = ArtistApplicationSerializer(data = request.data,context={'request':request})
            if serializer.is_valid():
                new_artist = serializer.save(user=user)
                new_artist.set_account_number(new_artist.account_number)
                new_artist.account_number = ""
                new_artist.save()
                user.role = 'artist'
                user.save()

                Notification.objects.create(
                user=user,
                notification_type="application_accepted",
                title=f"Welcome to EchoEase, {user.first_name} {user.last_name}",
                description="We’re pleased to inform you that your application has been approved. Congratulations on joining EchoEase as an official Echoee! Your talent is now part of a vibrant community of artists. Start connecting with fans and venues, and showcase your music on a platform designed to elevate your artistry. Welcome aboard!"

            )




            # Send email to the user notifying them of their approval\

                subject =  'Echoease Artist Application Approval'
                message = f'Your artist application has been approved.'
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                    )
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, id):
            user = request.user
            application = get_object_or_404(ArtistApplication, id=id)
            serializer = ArtistApplicationSerializer(application, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error':'uploading video failed'},status=status.HTTP_400_BAD_REQUEST)


class GenreView(APIView):

    permission_classes = [AllowAny]
    def get(self, request, id=None):

        if id:
            genre = get_object_or_404(Genre, id = id)
            serializer = GenreSerializer(genre)
            return Response(serializer.data, status = status.HTTP_200_OK)

        try:
            genres = Genre.objects.all()
            serializer = GenreSerializer(genres, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class IDTypesView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()
    def get(self, request, pk=None):
        if pk:
            id_type = get_object_or_404(IDType, pk=pk)
            serializer = IDTypeSerializer(id_type)
            return Response(serializer.data, status=status.HTTP_200_OK)
        accepted_ids = get_list_or_404(IDType)
        serializer = IDTypeSerializer(accepted_ids, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RateView(APIView):
    def get(self, request, id):
        artist = get_object_or_404(Artist, id=id)
        rates = artist.artist_rates.all()
        serializer = RateSerializer(rates,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



    def post(self, request):
        serializer = RateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        rate_id = request.data.get('id')
        rate = get_object_or_404(Rate, id = rate_id)
        serializer = RateSerializer(rate,data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'success'}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )
    def delete(self, request, id):
        rate = get_object_or_404(Rate, id=id)
        rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConnectionRequestView(APIView):
    permission_classes = [IsArtist]
    def get(self, request, id=None):
        if id:
            pass
        status_filter  = request.query_params.get('status')
        artist = get_object_or_404(Artist, user = request.user)
        connection_requests = ConnectionRequest.objects.filter(Q(sender = artist)|Q(receiver = artist))
        if status_filter:
            connection_requests = connection_requests.filter(status = status_filter)
        serializer = ConnectionRequestSerializer(connection_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ConnectionRequestSerializer(data = request.data)
        try:
            if serializer.is_valid():
                    con_request = serializer.save()
                    try:
                        Notification.objects.create(
                            user = con_request.receiver.user,
                            notification_type = 'connection_request_accepted',
                            title = f'{con_request.sender.user.first_name} {con_request.sender.user.last_name} has sent you a connection request',
                            description = f'Click here to view and manage your connections',
                        )
                    except Exception as e:
                        pass
                    notify_new_sent_request(con_request.receiver, request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DjangoValidationError as e:
                print(e)
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        request_id = request.data['request_id']
        action = request.data.get('action')
        connection_request = get_object_or_404(ConnectionRequest, id=request_id)
        if connection_request and action:
            if action == 'accept':
                connection_request.accept()
                try:
                    Notification.objects.create(
                        user = connection_request.sender.user,
                        notification_type = 'connection_request_accepted',
                        title = f'{connection_request.receiver.user.first_name} {connection_request.receiver.user.last_name} has accepted your connection request',
                        description = f'Click here to view and manage your connections',
                    )
                except Exception as e:
                    pass
                notify_accepted_request(connection_request.sender, connection_request.receiver)
                return Response(status=status.HTTP_204_NO_CONTENT)
            if action == 'reject':
                connection_request.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request,id):
        connection_request = get_object_or_404(ConnectionRequest, id=id)
        connection_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReceivedConnectionRequestView(APIView):
    def get(self,request):
        status_filter = request.query_params.get('status')
        artist = get_object_or_404(Artist, user = request.user)
        connection_requests = ConnectionRequest.objects.filter(receiver = artist)
        if status_filter:
            connection_requests = connection_requests.filter(status = status_filter)
        serializer = ConnectionRequestSerializer(connection_requests, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)


class SentConnectionRequestView(APIView):
    def get(self, request):
        status_filter = request.query_params.get('status')
        artist = get_object_or_404(Artist, user = request.user)
        connection_requests = ConnectionRequest.objects.filter(sender = artist)
        if status_filter:
            connection_requests = connection_requests.filter(status = status_filter)
        serializer = ConnectionRequestSerializer(connection_requests, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)


class DisconnectArtistView(APIView):
    def delete(self,request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        artist_user = get_object_or_404(Artist, user = request.user)
        artist_user.connections.remove(artist)
        connection_request = ConnectionRequest.objects.filter(
            Q(sender=artist_user, receiver=artist) | Q(sender=artist, receiver=artist_user)
        )
        connection_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowingView(APIView):
    def get(self, requests,artist_id, *args, **kwargs):
        artist = get_object_or_404(Artist, pk = artist_id)
        artist_user = artist.user
        if artist_user is None:
            return Response({'message':'Artist User Not Found'},status=status.HTTP_404_NOT_FOUND)
        artist_followed = artist_user.artists_followed
        serializer = ArtistSerializer(artist_followed.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def follow(request):
    user = request.user
    artist = get_object_or_404(Artist, pk=request.data.get("artist"))
    if user not in artist.followers.all():
        artist.followers.add(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def unfollow(request):
    user = request.user
    artist = get_object_or_404(Artist, pk=request.data.get("artist"))
    if user in artist.followers.all():
        artist.followers.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_recommended_artists(request):
    artist = get_object_or_404(Artist, user=request.user)

    # Get artists who already have a connection request (pending or accepted)
    connection_requests = ConnectionRequest.objects.filter(
        Q(sender=artist) | Q(receiver=artist),
        status__in=['pending', 'accepted','rejected']
    ).values_list('receiver_id', 'sender_id')

    # Flatten the result to get a list of artist IDs
    artist_ids_with_requests = set([item for sublist in connection_requests for item in sublist])

    # Query artists by the same genre, excluding current artist, existing connections, and those with a connection request
    artists_by_genre = Artist.objects.filter(
        genres__in=artist.genres.all(),
        status='active'
    ).exclude(
        id=artist.pk
    ).exclude(
        connections=artist
    ).exclude(
        id__in=artist_ids_with_requests
    ).distinct()

    # Query artists with mutual connections, excluding current artist, existing connections, and those with a connection request
    artists_by_mutual = Artist.objects.filter(
        connections__in=artist.connections.all(),
        status='active'
    ).exclude(
        id=artist.pk
    ).exclude(
        connections=artist
    ).exclude(
        id__in=artist_ids_with_requests
    ).distinct()

    # Combine both queries using union
    recommended_artists = artists_by_genre.union(artists_by_mutual)

    # Serialize the recommended artists
    serializer = RecommendedArtistSerializer(recommended_artists, many=True, context={'current_artist': artist})

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_genre(request, id):
    artist = get_object_or_404(Artist, user=request.user)
    genre = get_object_or_404(Genre, id=id)
    artist.genres.remove(genre)
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def add_genre(request, id):
    artist = get_object_or_404(Artist, user=request.user)
    genre = get_object_or_404(Genre, id=id)
    artist.genres.add(genre)
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def set_date_unavailable(request):
    date = request.data.get('date')
    try:
        date_obj = timezone.datetime.strptime(date,'%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)



class ArtistFollowersView(APIView):
    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        serializer = UserAccountSerializer(artist.followers, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReportPortfolioItemView(APIView):
    def post(self, request, item_id):
        item = get_object_or_404(PortfolioItem, pk= item_id)
        item.reported = True
        item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class MyArtistConnectionsView(APIView):
    def get(self, request):
        artist = get_object_or_404(Artist, user=request.user)
        try:
            serializer = ArtistConnectionsSerializer(artist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message':'error fetching your connections'}, status=status.HTTP_400_BAD_REQUEST)

class ArtistConnectionsView(APIView):
    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        try:
            serializer = ArtistConnectionsSerializer(artist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message':'error fetching connections of this artist'}, status=status.HTTP_400_BAD_REQUEST)
