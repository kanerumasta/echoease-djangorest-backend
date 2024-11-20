from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import TemplateView
from artists.models import Artist
from django.contrib import messages
from notification.models import Notification

from dispute.models import Dispute
from users.models import UserAccount
from payment.models import Payment
from booking.models import Booking
from payment.utils import refund_payment
from django.utils import timezone

class DashboardView(TemplateView):
    template_name = 'custom_admin/dashboard.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        # Calculating the counts
        context['artist_users_count'] = UserAccount.objects.filter(role='artist').count()
        context['client_users_count'] = UserAccount.objects.filter(role='client').count()
        context['disputes_count'] = Dispute.objects.all().count()
        context['total_users_count'] = context['artist_users_count'] + context['client_users_count']
        context['artist_users'] = UserAccount.objects.filter(role='artist')
        context['client_users'] = UserAccount.objects.filter(role='client')
        context['total_users'] = UserAccount.objects.all()

        # Replace the value with your actual sales logic
        context['total_sales'] = 5000

        return context
class DisputesView(TemplateView):
    template_name = 'custom_admin/disputes.html'

    def get_context_data(self, **kwargs: Any):
        context =  super().get_context_data(**kwargs)
        context['disputes'] = Dispute.objects.order_by('is_resolved', '-created_at')
        return context

class DisputeDetailView(TemplateView):
    template_name = 'custom_admin/dispute_detail.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        dispute_id = kwargs.get('dispute_id')
        # Retrieve the specific dispute by its ID
        dispute = get_object_or_404(Dispute, id=dispute_id)
        print(dispute)

        downpayment = Payment.objects.filter(payment_type='downpayment',booking=dispute.booking, is_refunded=False).first()
        context['dispute'] = dispute
        context['downpayment'] = downpayment
        return context

def refund_payment_view(request, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        reason = request.POST.get('reason')
        payment_id = request.POST.get('payment_id')

        if not payment_id:
            # Handle invalid payment_id (empty or None)
            return render(request, 'custom_admin/dispute_detail.html', {'dispute': dispute, 'error': 'Invalid payment ID.'})

        payment = get_object_or_404(Payment, pk=payment_id)

        # Process the refund
        success = refund_payment(amount, payment.payment_id, payment_id, reason)

        if success:
            # Refund successful, you can mark the payment as refunded
            Payment.objects.filter(id=payment_id).update(is_refunded=True)
            dispute.resolution = 'Refund'
            return redirect('dispute_detail', dispute_id=dispute.id)
        else:
            # Handle failure
            return render(request, 'custom_admin/dispute_detail.html', {'dispute': dispute, 'error': 'Refund failed'})

    return render(request, 'custom_admin/dispute_detail.html', {'dispute': dispute})


def resolve_dispute(request, dispute_id):
    # Retrieve the dispute object
    dispute = get_object_or_404(Dispute, id=dispute_id)
    resolution = request.POST.get('resolution')

    if not dispute.is_resolved:  # Only mark it as resolved if it's not already resolved
        dispute.is_resolved = True
        dispute.date_resolved = timezone.now()
        dispute.status="resolved"
        dispute.resolution = resolution
        dispute.save()  # Save the changes

    return redirect('dispute_detail', dispute_id=dispute.id)

def decrease_reputation_score(request, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id)
    points = request.POST.get('points')

    # Validate points input
    try:
        points = int(points)
        if points <= 0:
            raise ValueError("Points must be greater than zero.")
    except (ValueError, TypeError):
        messages.error(request, "Invalid points value.")
        return redirect('dispute_detail', dispute_id=dispute.pk)

    # Decrease reputation based on dispute type
    if dispute.dispute_type == 'client':
        user = get_object_or_404(UserAccount, id=dispute.booking.artist.user.pk)
    else:  # Assume 'artist' for other dispute types
        user = get_object_or_404(UserAccount, id=dispute.booking.client.pk)


    user.decrease_reputation(points)
    dispute.resolution = "Decreased Reputation"
    dispute.status = 'resolved'
    dispute.is_resolved = True
    dispute.save()
    try:
        Notification.objects.create(
            user = user,
            notification_type= "reputation",
            title = "Reputation Update",
            description = f"Your reputation has been decreased by {points} points due to a dispute."
        )
    except Exception as e:
        print(e)
    messages.success(request, f"{points} points were successfully deducted from {user.first_name}'s reputation.")
    return redirect('dispute_detail', dispute_id=dispute.pk)
