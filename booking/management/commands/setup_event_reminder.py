from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Sets up the periodic task for sending event reminders'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        task_exists = PeriodicTask.objects.filter(name='Send Payment Reminders Every Minute').exists()
        expire_task_exists = PeriodicTask.objects.filter(name='Expire Bookings').exists()


        if not task_exists:
            PeriodicTask.objects.create(
                interval=schedule,
                name='Send Event Reminders Every Minute',
                task='booking.tasks.send_payment_reminders',
            )
            self.stdout.write(self.style.SUCCESS('Periodic task created.'))
        else:
            self.stdout.write(self.style.WARNING('Periodic task already exists.'))

        if not expire_task_exists:
            PeriodicTask.objects.create(
                interval=schedule,
                name='Expire Bookings',
                task='booking.tasks.expire_bookings',
            )
            self.stdout.write(self.style.SUCCESS('Periodic task created for expiring bookings.'))
        else:
            self.stdout.write(self.style.WARNING('Periodic task for expiring bookings already exists.'))
