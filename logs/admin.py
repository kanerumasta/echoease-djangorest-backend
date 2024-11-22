from django.contrib import admin
from .models import UserLogs, TransactionLogs

admin.site.register(UserLogs)
admin.site.register(TransactionLogs)
