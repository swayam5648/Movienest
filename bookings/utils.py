from bookings.models import ShowSeat
import string

def generate_show_seats(movie, show_date, show_time):
    rows = list(string.ascii_uppercase[:10])  # A to J
    for row in rows:
        for col in range(1, 11):  # 1 to 10
            seat_number = f"{row}{col}"
            ShowSeat.objects.create(
                movie=movie,
                show_date=show_date,
                show_time=show_time, 
                seat_number=seat_number,
                row=row,
                column=col,
                is_booked=False
            )
    print(f"Created 100 seats for {movie.title} on {show_date} at {show_time}")
