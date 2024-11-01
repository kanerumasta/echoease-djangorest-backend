# admin.py
from django.contrib import admin
from .models import Dispute
from django.utils.html import format_html

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'penalty', 'resolve_dispute', 'impose_penalty')
    actions = ['mark_as_resolved', 'apply_penalty']

    # Action to resolve disputes
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} dispute(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark selected disputes as resolved"

    # Action to impose a penalty
    def apply_penalty(self, request, queryset):
        updated = queryset.update(penalty=100.00)
        self.message_user(request, f"{updated} dispute(s) had penalties imposed.")
    apply_penalty.short_description = "Impose a penalty on selected disputes"

    # Helper method to make resolve option clickable
    def resolve_dispute(self, obj):
        return format_html('<a class="button" href="{}">Resolve</a>', f'/admin/yourapp/dispute/{obj.id}/change/')
    resolve_dispute.short_description = "Resolve Dispute"

    # Helper method to make impose penalty clickable
    def impose_penalty(self, obj):
        return format_html('<a class="button" href="{}">Impose Penalty</a>', f'/admin/yourapp/dispute/{obj.id}/change/')
    impose_penalty.short_description = "Impose Penalty"
