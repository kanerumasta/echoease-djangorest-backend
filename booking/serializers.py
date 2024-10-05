from rest_framework import serializers
from .models import Booking
from users.serializers import UserAccountSerializer
from artists.serializers import ArtistSerializer
from artists.models import Artist, Rate



class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id','name','amount']


class BookingSerializer(serializers.ModelSerializer):
    event_date = serializers.DateField(input_formats=["%m/%d/%Y"])
    client = UserAccountSerializer(read_only=True)
    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        write_only=True
    )
    rate = serializers.PrimaryKeyRelatedField(
        queryset = Rate.objects.all(),
        write_only=True
    )
    artist_details = ArtistSerializer(source='artist', read_only=True)
    rate_details = RateSerializer(source='rate', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['formatted_event_date'] = instance.event_date.strftime('%B %d, %Y')
        representation['formatted_event_time'] = instance.event_time.strftime('%I:%M %p')
        representation['artist'] = representation.pop('artist_details')
        representation['rate'] = representation.pop('rate_details')
        return representation
