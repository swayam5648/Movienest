from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timesince import timesince
from datetime import datetime
from bookings.models import Booking, BookingUser, ShowSeat, Review
from movies.models import Movie, ShowDate, ShowTime
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io
from django.db.models import Sum
from bookings.forms import ProfileForm
from payment.models import Payment  
import io
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

def select_showtime(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # Fetch show dates with related theatre and showtimes in one go
    show_dates = (
        ShowDate.objects
        .filter(movie=movie)
        .select_related('theatre')                 # theatre एकाच query मध्ये
        .prefetch_related('show_times')            # त्या theatre चे सर्व showtimes
        .order_by('date')
    )

    context = {
        'movie': movie,
        'show_dates': show_dates,
    }
    return render(request, 'bookings/select_showtime.html', context)

# Step 1: Book Ticket with available show dates
@login_required
def book_ticket(request, movie_id, show_date_id, show_time_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    show_date = get_object_or_404(ShowDate, pk=show_date_id, movie=movie)
    show_time = get_object_or_404(ShowTime, pk=show_time_id, show_date=show_date)

    if request.method == 'POST':
        try:
            ticket_count = int(request.POST.get('ticket_count', 1))
            if ticket_count < 1 or ticket_count > 10:
                raise ValueError("Ticket count must be between 1 and 10.")
        except (ValueError, TypeError):
            messages.error(request, "Please select a valid number of tickets (1-10).")
            return redirect(request.path)

        # ✅ Correct assignment of ForeignKey
        booking = Booking.objects.create(
            user=request.user,
            movie=movie,
            show_date=show_date.date,
            show_time=show_time,
        )

        attendees_created = 0
        for i in range(1, ticket_count + 1):
            name = request.POST.get(f'user_name_{i}')
            email = request.POST.get(f'user_email_{i}')
            phone = request.POST.get(f'user_phone_{i}')
            if name and email and phone:
                BookingUser.objects.create(
                    booking=booking,
                    name=name,
                    email=email,
                    phone=phone
                )
                attendees_created += 1
            else:
                messages.warning(request, f"Details missing for attendee #{i}, skipping.")

        if attendees_created == 0:
            messages.error(request, "No valid attendee information provided.")
            booking.delete()
            return redirect(request.path)

        # messages.success(
        #     request,
        #     f"Booking confirmed for {movie.title} on {show_date.date} at {show_time.time.strftime('%I:%M %p')}."
        # )
        return redirect('select_seats', booking_id=booking.id)

    return render(request, 'bookings/book_ticket.html', {
        'movie': movie,
        'show_date': show_date,
        'show_time': show_time,
        'ticket_range': range(1, 11),
    })


@login_required
def select_seats_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    show_time_obj = booking.show_time 

    seats = ShowSeat.objects.filter(
        movie=booking.movie,
        show_date=booking.show_date,
        show_time=show_time_obj  # Now it works!
    )

    rows = "ABCDEFGHIJ"
    cols = range(1, 11)

    seat_map = {}
    for row in rows:
        for col in cols:
            seat = seats.filter(row=row, column=col).first()
            seat_map[f"{row}{col}"] = seat

    if request.method == 'POST':
        selected_ids = [sid for sid in request.POST.getlist('seats') if sid.strip()]

        if not selected_ids:
            messages.error(request, "Please select at least one seat before confirming.")
            return redirect(request.path)

        max_seats = booking.attendees.count()
        if len(selected_ids) > max_seats:
            messages.error(request, f"You can only select {max_seats} seat(s) for this booking.")
            return redirect(request.path)

        selected_seats = list(ShowSeat.objects.filter(id__in=selected_ids, is_booked=False))

        if len(selected_seats) != len(selected_ids):
            messages.error(request, "Some seats were already booked. Please try again.")
            return redirect(request.path)

        booking.seats.set(selected_seats)
        ShowSeat.objects.filter(id__in=[seat.id for seat in selected_seats]).update(is_booked=True)

          # Avoid circular import
        payment = Payment.objects.create(
            user=request.user,
            booking=booking,
            amount=booking.movie.price * len(selected_seats)
        )

        return redirect('payment:payment_page', payment_id=payment.id)

    return render(request, 'bookings/select_seats.html', {
        'booking': booking,
        'movie': booking.movie,
        'show_date': booking.show_date,
        'seat_map': seat_map,
        'rows': rows,
        'cols': cols,
    })

# User Dashboard
@login_required
def user_dashboard(request):
    user = request.user

    bookings = Booking.objects.filter(user=user).prefetch_related('seats', 'movie')
    booking_count = bookings.count()
    total_payment = Payment.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    review_count = Review.objects.filter(user=user).count()

    context = {
        'booking_count': booking_count,
        'total_payment': total_payment,
        'review_count': review_count,
        'bookings': bookings
    }
    return render(request, 'bookings/user_dashboard.html', context)

# My Bookings
@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).prefetch_related('seats', 'movie')

    return render(request, 'bookings/my_bookings.html', {
        'bookings': bookings
    })

# Edit profile
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')  
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'bookings/edit_profile.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'bookings/profile.html')

# Review
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'bookings/my_reviews.html', {'reviews': reviews})


# Cancel Booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
    return redirect('user_dashboard')

# Generate Ticket
@login_required
def generate_ticket_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    movie_poster = None
    if booking.movie.poster:
        movie_poster = request.build_absolute_uri(booking.movie.poster.url)
    else:
        movie_poster = "https://via.placeholder.com/350x500"

    template_path = 'bookings/ticket_pdf_template.html'
    context = {
        'booking': booking,
        'movie_poster': movie_poster,
    }
    html = render_to_string(template_path, context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")), dest=response
    )

    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response
