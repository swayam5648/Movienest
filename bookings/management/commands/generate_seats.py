from django.core.management.base import BaseCommand
from movies.models import Movie, ShowTime
from bookings.models import ShowSeat
from datetime import datetime

class Command(BaseCommand):
    help = 'Generate 10x10 seats for a movie, show date, and show time'

    def add_arguments(self, parser):
        parser.add_argument('movie_id', type=int, help="Movie ID")
        parser.add_argument('show_date', type=str, help="Show date in YYYY-MM-DD format")
        parser.add_argument('show_time_id', type=int, help="ShowTime ID")

    def handle(self, *args, **kwargs):
        try:
            movie = Movie.objects.get(id=kwargs['movie_id'])
            show_date = datetime.strptime(kwargs['show_date'], "%Y-%m-%d").date()
            show_time = ShowTime.objects.get(id=kwargs['show_time_id'])
        except Movie.DoesNotExist:
            return self.stderr.write(self.style.ERROR("❌ Invalid movie ID."))
        except ShowTime.DoesNotExist:
            return self.stderr.write(self.style.ERROR("❌ Invalid show time ID."))
        except ValueError:
            return self.stderr.write(self.style.ERROR("❌ Invalid date format. Use YYYY-MM-DD."))

        rows, cols = "ABCDEFGHIJ", range(1, 11)
        created_count = 0

        for r in rows:
            for c in cols:
                seat_number = f"{r}{c}"
                obj, created = ShowSeat.objects.get_or_create(
                    movie=movie,
                    show_date=show_date,
                    show_time=show_time,
                    seat_number=seat_number,
                    row=r,
                    column=c
                )
                if created:
                    created_count += 1

        # Convert time to AM/PM format
        formatted_time = show_time.time.strftime('%I:%M %p')  # 12-hour format with AM/PM

        self.stdout.write(self.style.SUCCESS(
            f"✅ {created_count} seats created for '{movie.title}' on {show_date} at {formatted_time}"
        ))
