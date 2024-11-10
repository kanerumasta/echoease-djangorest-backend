from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from artists.models import Artist

class DashboardView(TemplateView):
    template_name = 'custom_admin/dashboard.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['echoee_count'] = Artist.objects.count()
        return context
