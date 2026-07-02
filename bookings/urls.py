from django.urls import path
from bookings import views

urlpatterns = [
    path('movie/<int:movie_id>/book/<int:show_date_id>/<int:show_time_id>/', views.book_ticket, name='book_ticket'),
    path('movie/<int:movie_id>/select_showtime/', views.select_showtime, name='select_showtime'),
    path('select-seats/<int:booking_id>/', views.select_seats_view, name='select_seats'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('ticket/<int:booking_id>/download/', views.generate_ticket_pdf, name='download_ticket_pdf'),
]
