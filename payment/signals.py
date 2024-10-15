from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from transaction.models import Transaction


@receiver(post_save, sender=Payment)
def create_payment_transaction(sender, instance, created, **kwargs):
    if created:
        transaction_type = instance.payment_type
        print('Payment transaction type',transaction_type)

        try:
            # Handling different types of payments
            if transaction_type == 'downpayment':
                # Logic for downpayment
                transaction = Transaction.objects.create(
                    transaction_type=transaction_type,
                    status='completed',
                    booking=instance.booking,
                    client=instance.booking.client,
                    amount=instance.amount,
                    service_fee=instance.service_fee,  # May or may not include a service fee
                    payment_gateway=instance.payment_gateway,
                    payment_intent_id=instance.payment_intent_id,
                    payer_email=instance.payer_email,
                    payer_name=instance.payer_name,
                    net_amount=instance.net_amount  # Adjust according to downpayment logic
                )

            elif transaction_type == 'full_payment':
                # Logic for full payment
                transaction = Transaction.objects.create(
                    transaction_type=transaction_type,
                    status='completed',
                    booking=instance.booking,
                    client=instance.booking.client,
                    amount=instance.amount,
                    service_fee=instance.service_fee,  # Full payment may include different fees
                    payment_gateway=instance.payment_gateway,
                    payment_intent_id=instance.payment_intent_id,
                    payer_email=instance.payer_email,
                    payer_name=instance.payer_name,
                    net_amount=instance.net_amount
                )

            elif transaction_type == 'refund':
                # Logic for refund
                refund_amount = -abs(instance.amount)  # Refund is usually a negative amount
                transaction = Transaction.objects.create(
                    transaction_type=transaction_type,
                    status='completed',
                    booking=instance.booking,
                    client=instance.booking.client,
                    amount=refund_amount,  # Negative amount for refund
                    service_fee=0,  # Refunds usually don't have a service fee
                    payment_gateway=instance.payment_gateway,
                    payment_intent_id=instance.payment_intent_id,
                    payer_email=instance.payer_email,
                    payer_name=instance.payer_name,
                    net_amount=refund_amount
                )

            # Save the transaction
            transaction.save()

        except Exception as e:
            print(f'Error creating transaction in signals: {e}')
