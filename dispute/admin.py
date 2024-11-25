# admin.py
from django.contrib import admin
from .models import Dispute, DisputeEvidence
from django.utils.html import format_html


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'resolve_dispute')
    actions = ['mark_as_resolved', 'apply_suspension','decrease_reputation']

    # Action to resolve disputes
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} dispute(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark selected disputes as resolved"

    # Action to impose a penalty
    def apply_suspension(self, request, queryset):
        for dispute in queryset:
            if dispute.dispute_type == 'artist':
                dispute.booking.client.suspend()
                self.message_user(request, f"Artist/s suspended")
            elif dispute.dispute_type == 'client':
                dispute.booking.artist.user.suspend()
                self.message_user(request, f"Client/s suspended")
        updated = queryset.update(status='resolved')
    apply_suspension.short_description = "Suspend user in selected disputes"

    def decrease_reputation(self, request, queryset):
        for dispute in queryset:
            if dispute.dispute_type == 'artist':
                dispute.booking.client.decrease_reputation(5)
                self.message_user(request, f"Artist's reputation decreased")
            elif dispute.dispute_type == 'client':
                dispute.booking.artist.user.decrease_reputation(5)
                self.message_user(request, f"Client's reputation decreased")
        updated = queryset.update(status='resolved')

    # Helper method to make resolve option clickable
    def resolve_dispute(self, obj):
        return format_html('<a class="button" href="{}">Resolve</a>', f'/admin/dispute/dispute/{obj.id}/change/')
    resolve_dispute.short_description = "Resolve Dispute"


admin.site.register(DisputeEvidence)
