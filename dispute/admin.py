from django.contrib import admin
from .models import ClientDispute, ArtistDispute, Dispute, DisputeEvidence
# Register your models here.
admin.site.register(ClientDispute)
admin.site.register(ArtistDispute)
admin.site.register(Dispute)
admin.site.register(DisputeEvidence)
