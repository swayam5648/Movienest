from django.core.management.base import BaseCommand
from bookings.models import Booking
from datetime import date

class Command(BaseCommand):
    help = 'Deactivate expired bookings whose show_date is in the past'

    def handle(self, *args, **kwargs):
        today = date.today()
        expired_bookings = Booking.objects.filter(show_date__lt=today, is_active=True)
        count = expired_bookings.update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f'{count} bookings marked as inactive.'))