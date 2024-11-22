from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import TemplateView
from artists.models import Artist, PortfolioItem
from django.contrib import messages
from notification.models import Notification

from dispute.models import Dispute
from users.models import UserAccount
from payment.models import Payment
from booking.models import Booking
from django.http import JsonResponse
from payment.utils import refund_payment
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from transaction.models import Transaction
from .forms import AdminUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from chat.models import Conversation, Message


class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'custom_admin/dashboard.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        # Calculating the counts
        context['reported_contents_count'] = PortfolioItem.objects.filter(reported=True).count()
        context['artist_users_count'] = UserAccount.objects.filter(role='artist').count()
        context['client_users_count'] = UserAccount.objects.filter(role='client').count()
        context['disputes_count'] = Dispute.objects.filter(is_resolved=False).count()
        context['total_users_count'] = context['artist_users_count'] + context['client_users_count']
        context['artist_users'] = UserAccount.objects.filter(role='artist')
        context['client_users'] = UserAccount.objects.filter(role='client')
        context['total_users'] = UserAccount.objects.all()
        revenue = Payment.objects.filter(payment_type="payout").aggregate(Sum("echoease_fee"))
        context['total_revenue'] = revenue['echoease_fee__sum']



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
def user_detail(request, user_id):
    # Fetch the user object
    user = get_object_or_404(UserAccount, id=user_id)

    if request.method == "POST":
        # Handle suspension
        if "suspend_user" in request.POST:
            # Mark user as suspended (or any other logic based on your model)
            user.is_active = False  # Assuming you have an `is_active` field to track suspension
            user.is_suspended = True
            user.save()
            messages.success(request, "User has been suspended successfully.")
            return redirect('user_detail', user_id=user.id)

        # Handle warning
        # elif "send_warning" in request.POST:
        #     warning_message = request.POST.get("warning_message")
        #     if warning_message:
        #         # Logic for sending the warning (e.g., email or saving it to the database)
        #         # You can store the warning message in a related model or send it via email
        #         # Example: save warning in a 'Warnings' model (implement this as per your needs)
        #         user.warnings.create(message=warning_message, sent_by=request.user)
        #         messages.success(request, "Warning has been sent to the user.")
        #         return redirect('user_detail', user_id=user.id)

    return render(request, 'custom_admin/user_detail.html', {'user': user})


from django.shortcuts import redirect

def suspend_user(request, user_id):
    # Fetch the user object
    user = get_object_or_404(UserAccount, id=user_id)

    # Check if the request method is POST (for safety)
    if request.method == "POST":
        # Mark the user as suspended
        user.is_active = False
        user.is_suspended = True
        user.save()

        # Redirect back to the user detail page after suspension
        return redirect('user_detail', user_id=user.id)

    # If it's not a POST request, respond with an error
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

from django.shortcuts import redirect

def unsuspend_user(request, user_id):
    # Fetch the user object
    user = get_object_or_404(UserAccount, id=user_id)

    # Check if the user is suspended
    if user.is_suspended:
        # Mark the user as active and unsuspended
        user.is_active = True
        user.is_suspended = False
        user.save()

        # Redirect back to the user detail page after unsuspension
        return redirect('user_detail', user_id=user.id)

    return JsonResponse({'success': False, 'message': 'User is not suspended.'})
def warn_user(request, user_id):
    # Fetch the user object
    user = get_object_or_404(UserAccount, id=user_id)
    message = request.POST.get('message')

    user.warnings = user.warnings + 1
    user.save()
    try:
        Notification.objects.create(
            user = user,
            notification_type= "warning",
            title = "Warning Issued",
            description = message
        )
    except Exception as e:
        print(e)

        # Redirect back to the user detail page after unsuspension
    return redirect('user_detail', user_id=user.id)


def reported_portfolio_items(request):
    reported_items = PortfolioItem.objects.filter(reported=True)
    return render(request, 'custom_admin/reported_portfolio_items.html', {'reported_items': reported_items})

def portfolio_item_detail(request, item_id):
    portfolio_item = get_object_or_404(PortfolioItem, id=item_id)
    return render(request, 'custom_admin/portfolio_item_detail.html', {'portfolio_item': portfolio_item})


def delete_portfolio_item(request, item_id):
    """Handles deletion of a reported portfolio item."""
    portfolio_item = get_object_or_404(PortfolioItem, id=item_id)
    portfolio_item.delete()

    artist = portfolio_item.portfolio.artist
    try:
        Notification.objects.create(
            user = artist.user,
            notification_type= "reports",
            title = "Content Removed Due To Violation",
            description = f"We've reviewed a report about your content and found that it violates EchoEase's guidelines. As a result, the content has been removed. Please review our guidelines to avoid similar issues in the future. Continued violations may result in further actions on your account."

        )
    except Exception as e:
        print(e)
    return redirect('reported_portfolio_items')

def ignore_portfolio_item(request, item_id):
    """Handles ignoring a reported portfolio item."""
    portfolio_item = get_object_or_404(PortfolioItem, id=item_id)
    portfolio_item.reported = False  # Assuming there is an `is_reported` field
    artist = portfolio_item.portfolio.artist
    try:
        Notification.objects.create(
            user = artist.user,
            notification_type= "reports",
            title = "Reports Review Update",
            description = f"Upon reviewing your reported content of {artist.user.first_name.title()} {artist.user.last_name.title()}, our team found no violations of EchoEase guidelines. No action has been taken at this time. Thank You!"
        )
    except Exception as e:
        print(e)
    portfolio_item.save()
    return redirect('reported_portfolio_items')


def revenue_details(request):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Revenue calculations
    revenue_today = Payment.objects.filter(
       payment_date__date=today.date(),
        payment_type = "payout"
    ).aggregate(total=Sum('echoease_fee'))['total'] or 0

    revenue_week = Payment.objects.filter(
       payment_date__date__gte=start_of_week.date(),
         payment_type = "payout"
    ).aggregate(total=Sum('echoease_fee'))['total'] or 0

    revenue_month = Payment.objects.filter(
       payment_date__date__gte=start_of_month,
        payment_type = "payout"
    ).aggregate(total=Sum('echoease_fee'))['total'] or 0

    revenue_year = Payment.objects.filter(
       payment_date__date__gte=start_of_year,
        payment_type = "payout"
    ).aggregate(total=Sum('echoease_fee'))['total'] or 0

    # Get all transactions
    transactions = Transaction.objects.filter(payment__payment_type="payout").order_by('-created_at')

    context = {
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,
        'revenue_year': revenue_year,
        'transactions': transactions,
    }
    return render(request, 'custom_admin/revenue_details.html', context)


# View to display and manage admin users
def admin_users_management(request):
    admin_users = UserAccount.objects.filter(is_superuser=True)  # Fetch all superusers (admin users)
    return render(request, 'custom_admin/admin_users_management.html', {
        'admin_users': admin_users,
    })

# View to create a new admin user
def create_admin_view(request):
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_superuser = True  # Set the user as an admin
            user.is_staff = True  # Admins should also be staff
            user.save()
            messages.success(request, 'Admin user created successfully!')
            return redirect('admin_users')
    else:
        form = AdminUserCreationForm()

    return render(request, 'custom_admin/create_admin.html', {'form': form})

# View to edit an admin user
def edit_admin_view(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    if request.method == "POST":
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        messages.success(request, 'Admin user updated successfully!')
        return redirect('admin_users')

    return render(request, 'custom_admin/edit_admin.html', {'user': user})

# View to delete an admin user
def delete_admin_view(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    user.delete()
    messages.success(request, 'Admin user deleted successfully!')
    return redirect('admin_users')
@login_required
def chat_support_list(request):
    conversations = Conversation.objects.filter(participants=request.user)  # Adjust filter based on your model
    for conversation in conversations:
        # Find the partner in the conversation
        partner = conversation.participants.exclude(id=request.user.id).first()
        # Add the partner to the conversation object or to a list
        conversation.partner = partner
    context = {
        'conversations': conversations,

    }
    return render(request, 'custom_admin/chat_list.html', context)

@login_required
def conversation_detail(request, conversation_code):
    conversation = get_object_or_404(Conversation, code=conversation_code)
    # Find the partner (exclude the current user)
    partner = conversation.participants.exclude(id=request.user.id).first()
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    print(partner)

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            # Create a new message for the conversation
            new_message = Message.objects.create(
                conversation=conversation,
                content=message_content,
                author=request.user
            )
            new_message.save()

            return redirect('chat_detail', conversation_code=conversation.code)

    context = {
        'conversation': conversation,
        'messages': messages,
        'partner':partner
    }
    return render(request, 'custom_admin/chat_detail.html', context)
