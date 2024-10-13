from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from artists.models import Artist
from .models import Availability, RecurringPattern
from datetime import datetime
from booking.models import Booking


from .serializers import (
    AvailabilitySerializer,
    RecurringPatternSerializer
)

class AvailabilityView(APIView):
    def get(self, request, *args, **kwargs):
        artist_id = request.data.get('artist')
        artist = get_object_or_404(Artist, id = artist_id)
        serializer = AvailabilitySerializer()

    def post(self, request, *args, **kwargs):
        artist_id = request.data.get('artist')
        artist = get_object_or_404(Artist, id = artist_id)
        serializer = AvailabilitySerializer(data = request.data,context={'artist': artist})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status =status.HTTP_400_BAD_REQUEST)

class RecurringPatternView(APIView):
    def post(self, request, *args, **kwargs):
        artist_id = request.data.get('artist')
        artist = get_object_or_404(Artist, id = artist_id)
        serializer = RecurringPatternSerializer(data = request.data,context={'artist': artist})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class ArtistTimeSlotView(APIView):
    def get(self, request, artist_id, date):
        artist = get_object_or_404(Artist,id=artist_id)
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return Response({'error':'invalid date'}, status=status.HTTP_400_BAD_REQUEST)

        day_of_week = date_obj.strftime('%A')

        availability = Availability.objects.filter(
            artist = artist,
            day_of_week = Availability.DaysOfWeek[day_of_week.upper()].value,

        )
        recurring= RecurringPattern.objects.filter(
            artist = artist,
            days_of_week__contains = Availability.DaysOfWeek[day_of_week.upper()].value,
        )

        available_slots = list(availability) +  list(recurring)
        existing_bookings_for_date = Booking.objects.filter(
            artist = artist,
            event_date = date_obj
        )

        # Convert available slots and booked slots to time ranges
        available_time_ranges = [
            {
                'start_time': slot.start_time,
                'end_time': slot.end_time,
                'is_booked':False
            }
            for slot in available_slots
        ]

        booked_time_ranges = [
            {
                'start_time': booking.start_time,
                'end_time': booking.end_time,
                'is_booked':True
            }
            for booking in existing_bookings_for_date
        ]

        # Find new time slots by subtracting booked time ranges from available time ranges
        new_time_slots = []
        for available_range in available_time_ranges:
            start_time = available_range['start_time']
            end_time = available_range['end_time']

            # Split available ranges based on booked time ranges
            for booked_range in booked_time_ranges:
                booked_start = booked_range['start_time']
                booked_end = booked_range['end_time']

                if booked_start <= end_time and booked_end >= start_time:
                    # There is an overlap; break into available and booked segments
                    if start_time < booked_start:
                        # Add the unbooked portion before the booking starts
                        new_time_slots.append({
                            'start_time': start_time,
                            'end_time': booked_start,
                            'is_booked': False
                        })
                    # Add the booked portion
                    new_time_slots.append({
                        'start_time': max(start_time, booked_start),
                        'end_time': min(end_time, booked_end),
                        'is_booked': True
                    })
                    # Move the start_time forward to after the booked slot
                    start_time = booked_end

            # Add any remaining unbooked time after the booked slots
            if start_time < end_time:
                new_time_slots.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'is_booked': False
                })

        return Response(new_time_slots, status=status.HTTP_200_OK)



class ArtistScheduleView(APIView):
    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id = artist_id)
        availabilities = Availability.objects.filter(artist=artist)
        recurring_patterns = RecurringPattern.objects.filter(artist=artist)

        availability_data = [
            {
                'day_of_week': availability.day_of_week,
                'start_time':availability.start_time,
                'end_time':availability.end_time,
                'is_recurring': False,
             }
            for availability in availabilities
        ]

        recurring_data  = []
        for recurring in recurring_patterns:
            for day in recurring.days_of_week:
                recurring_data.append(
                    {
                        'day_of_week': day,
                        'start_time': recurring.start_time,
                        'end_time': recurring.end_time,
                        'is_recurring': True
                    }
                )
        all_schedules = availability_data + recurring_data

        all_schedules.sort(key=lambda x: x['day_of_week'])

        return Response(all_schedules, status=status.HTTP_200_OK)
class ArtistWeekDaysAvailableView(APIView):
    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)

        weekdays_data = []

        # Loop over the days of the week
        for day_value, day_label in Availability.DaysOfWeek.choices:
            # Check for normal availability on this day
            is_available = Availability.objects.filter(artist=artist, day_of_week=day_value).exists()

            # Check if this day is included in any recurring patterns
            is_recurring_available = RecurringPattern.objects.filter(
                artist=artist,
                days_of_week__contains=day_value
            ).exists()

            # Add data for this day
            if is_available or is_recurring_available:
                weekdays_data.append(day_value)

        return Response(weekdays_data, status=status.HTTP_200_OK)
