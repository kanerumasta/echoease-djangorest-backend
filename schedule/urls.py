from django.urls import path
from .views import (
    AvailabilityView,
    RecurringPatternView,
    ArtistScheduleView,
    ArtistTimeSlotView,
    ArtistWeekDaysAvailableView
    )

urlpatterns = [
    path('availabilities', AvailabilityView.as_view()),
    path('recurring-patterns', RecurringPatternView.as_view()),
    path('artist-schedule/<int:artist_id>', ArtistScheduleView.as_view()),
    path('artist-weekdays/<int:artist_id>', ArtistWeekDaysAvailableView.as_view()),
    path('artist-time-slot/<int:artist_id>/<str:date>', ArtistTimeSlotView.as_view())
]
