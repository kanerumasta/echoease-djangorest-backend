from django.contrib import admin
from .models import Booking
    # artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # event_name = models.CharField(max_length=100)
    # event_date = models.DateField()
    # event_time = models.TimeField()
    # created_at = models.DateField(auto_now_add=True)
    # updated_at = models.DateField(auto_now=True)
    # is_completed = models.BooleanField(default=False)
    # rate = models.ForeignKey(Rate, on_delete=models.CASCADE, null=True, blank=True)
    # province = models.CharField(max_length=255, null=True, blank=True)
    # municipality = models.CharField(max_length=255, null=True, blank=True)
    # barangay = models.CharField(max_length=255, null=True, blank=True)
    # street = models.CharField(max_length=255, null=True, blank=True)
    # landmark = models.CharField(max_length=255, null=True, blank=True)

class BookingAdmin(admin.ModelAdmin):
    list_display=['id', 'artist','client','event_name','event_date','full_address', 'status']
    list_display_links=['id', 'artist','client','event_name','event_date']

    def full_address(self, obj):
        return obj.full_address

    full_address.short_description = 'Event Address'

admin.site.register(Booking, BookingAdmin)
