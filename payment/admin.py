from django.contrib import admin
from .models import Payment, Refund


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__', 'payment_status', 'booking_id')
    actions =['refund_payments']

    def booking_id(self, obj):
        return obj.booking.pk

    # def refund_payments(self, request, queryset):
    #     for payment in queryset:
    #         if not payment.is_refunded:
    #             try:
    #                 payment.refund()
    #                 self.message_user(request, f"Refunded payment {payment.id}")

    #             except Exception as e:
    #                 self.message_user(request, f"Faild to refund payment {payment.id}", level="error")
    #         else:
    #             self.message_user(request, f"This payment has already been refunded : {payment.id} ", level="error")
    # refund_payments.short_description = "Refund Selected Payments"


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Refund )
