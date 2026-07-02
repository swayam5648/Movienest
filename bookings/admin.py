from django.contrib import admin
from bookings.models import Booking, BookingUser, Review, ShowSeat
# from bookings.seat_utils import generate_show_seats
from movies.models import ShowDate

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'show_date', 'show_time', 'ticket_count', 'created_at']
    list_filter = ['show_date', 'movie']
    search_fields = ['user__email', 'movie__title']

    def ticket_count(self, obj):
        return obj.attendees.count()  # related_name='attendees'
    ticket_count.short_description = 'Tickets'

@admin.register(BookingUser)
class BookingUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'booking']
    search_fields = ['name', 'email', 'phone']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'movie__title', 'comment')

@admin.register(ShowSeat)
class ShowSeatAdmin(admin.ModelAdmin):
    list_display = ['movie', 'show_date', 'show_time', 'seat_number', 'row', 'column', 'seat_type', 'is_booked']
    list_filter = ['show_date', 'show_time', 'seat_type', 'is_booked', 'movie']
    search_fields = ['seat_number', 'row', 'movie__title']
    list_editable = ['is_booked', 'seat_type']


