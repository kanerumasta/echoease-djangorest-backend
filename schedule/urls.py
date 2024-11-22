from django.urls import path
from .views import (
    AvailabilityView,
    RecurringPatternView,
    ArtistScheduleView,
    ArtistTimeSlotView,
    ArtistWeekDaysAvailableView,
    CombinedAvailabilityView,
    ArtistUnavailableDatesView
    )

urlpatterns = [
    path('availabilities', AvailabilityView.as_view()),
    path('availabilities/<int:availability_id>', AvailabilityView.as_view()),
    path('recurring-patterns', RecurringPatternView.as_view()),
    path('recurring-patterns/<int:recurring_id>', RecurringPatternView.as_view()),
    path('combined-availability/<int:artist_id>', CombinedAvailabilityView.as_view()),
    path('artist-schedule/<int:artist_id>', ArtistScheduleView.as_view()),
    path('artist-weekdays/<int:artist_id>', ArtistWeekDaysAvailableView.as_view()),
    path('artist-time-slot/<int:artist_id>/<str:date>', ArtistTimeSlotView.as_view()),
    path('artist-unavailable-dates', ArtistUnavailableDatesView.as_view()),
    path('artist-unavailable-dates/<int:artist_id>', ArtistUnavailableDatesView.as_view()),
    path('artist-unavailable-dates/delete/<int:id>', ArtistUnavailableDatesView.as_view()),
]
