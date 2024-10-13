from .models import Availability, RecurringPattern
from rest_framework import serializers

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'

    def validate(self, data):
         artist = self.context['artist']
         start_time = data.get('start_time') # type: ignore
         end_time = data.get('end_time')
         if start_time >= end_time:
             raise serializers.ValidationError("The start time must be before the end time.")

         overlap_recurring = RecurringPattern.objects.filter(
            artist = artist,
             days_of_week__contains=data.get('day_of_week'),
        )
         if overlap_recurring.exists():
             raise serializers.ValidationError("This availability slot overlaps with an existing recurring pattern.")

         overlap_count = Availability.objects.filter(
             artist=artist,
             day_of_week = data.get('day_of_week'),
         ).count()
         if overlap_count > 0:
             raise serializers.ValidationError("This availability slot overlaps with an existing availability slot.")
         return data


class RecurringPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringPattern
        fields = '__all__'

    def validate(self, data):
         artist = self.context['artist']
         start_time = data.get('start_time')
         end_time = data.get('end_time')
         if start_time >= end_time:
             raise serializers.ValidationError("The start time must be before the end time.")
         overlap_count = Availability.objects.filter(
             artist=artist,
             day_of_week__in=data.get('days_of_week'),
         ).count()
         if overlap_count > 0:
             raise serializers.ValidationError("This recurring pattern overlaps with an existing recurring pattern.")
         return data
