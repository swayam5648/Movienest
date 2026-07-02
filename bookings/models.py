from django.db import models
from django.conf import settings
from movies.models import Movie, ShowTime

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    show_date = models.DateField()
    show_time = models.ForeignKey(ShowTime, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seats = models.ManyToManyField('ShowSeat', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.movie.title} ({self.show_date} {self.show_time.time})"

    class Meta:
        ordering = ['-created_at']


class BookingUser(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='attendees')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.email})"


class ShowSeat(models.Model):
    SEAT_TYPES = [
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('wheelchair', 'Wheelchair'),
    ]
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    show_date = models.DateField()
    show_time = models.ForeignKey(ShowTime, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    row = models.CharField(max_length=2, default='A')
    column = models.IntegerField(default=1)
    is_booked = models.BooleanField(default=False)
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES, default='regular')

    def __str__(self):
        return f"{self.movie.title} | {self.show_date} {self.show_time.time} | Seat {self.seat_number} ({self.seat_type})"

    class Meta:
        unique_together = ('movie', 'show_date', 'show_time', 'seat_number')
        ordering = ['row', 'column']


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.movie.title} ({self.rating}★)"
