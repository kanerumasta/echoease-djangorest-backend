from django.db import models
from artists.models import Artist
from django.core.exceptions import ValidationError

class Availability(models.Model):
    class DaysOfWeek(models.IntegerChoices):
        SUNDAY = 0, 'Sunday'
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DaysOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        conflicting_availability = Availability.objects.filter(
            artist = self.artist,
            day_of_week = self.day_of_week,
            start_time__lt = self.end_time,
            end_time__gt = self.start_time
        )

        if conflicting_availability.exists():
            raise ValidationError('Conflicting time error.')

        conflicting_recurring = RecurringPattern.objects.filter(
            artist = self.artist,
            days_of_week__contains = self.day_of_week,
        )
        if conflicting_recurring.exists():
            raise ValidationError('This day of week already exists')


class RecurringPattern(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='recurring_availabilities')
    days_of_week = models.JSONField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
         conflicting_availabities = Availability.objects.filter(
             artist = self.artist,
             day_of_week__in = self.days_of_week
         )

         if conflicting_availabities.exists():
            conflicting_days = ', '.join([availability.get_day_of_week_display() for availability in conflicting_availabities])
            raise ValidationError(f'Artist has conflicting availability on {conflicting_days}')
