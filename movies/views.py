from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from movies.models import Movie, ShowDate, ShowTime, Cast, Song, Cast, MovieRating
from bookings.models import Review
from django.db.models import Avg

# Featured movies for homepage
def home(request):
    featured_movies = Movie.objects.filter(featured=True).annotate(avg_rating=Avg('ratings__rating'))
    return render(request, 'movies/home.html', {'featured_movies': featured_movies})

# All movies (optional)
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movies.html', {'movies': movies})

# Only Marathi movies
def marathi_movies(request):
    movies = Movie.objects.filter(language="Marathi").order_by('-release_date')
    return render(request, 'movies/marathi_movies.html', {'movies': movies})

# Only Hindi movies
def hindi_movies(request):
    Movies = Movie.objects.filter(language="Hindi").order_by('-release_date')
    return render(request, 'movies/hindi_movies.html', {'movies': Movies})

# Only Telgu movies
def telgu_movies(request):
    Movies = Movie.objects.filter(language="Telugu").order_by('-release_date')
    return render(request, 'movies/Telgu_movies.html', {'movies': Movies})

# Movie detail
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    show_dates = ShowDate.objects.filter(movie=movie).prefetch_related('show_times').order_by('date')
    songs = movie.songs.all()
    cast = movie.cast.all()
    return render(request, 'movies/movie_detail.html', {'movie': movie, 'show_dates': show_dates, 'songs': songs, 'cast': cast,})

# Search Movies
def search_movies(request):
    query = request.GET.get('q')
    if query:
        movies = Movie.objects.filter(title__icontains=query)
    else:
        movies = Movie.objects.all()
    return render(request, 'movies/search_result.html', {'movies': movies, 'query': query})

# Rating
@login_required
def submit_rating_view(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        rating_obj, created = MovieRating.objects.get_or_create(user=request.user, movie=movie)
        rating_obj.rating = rating_value
        rating_obj.save()
        return redirect('movie_detail', pk=movie.id) 
    else:
        try:
            existing_rating = MovieRating.objects.get(user=request.user, movie=movie)
        except MovieRating.DoesNotExist:
            existing_rating = None

        return render(request, 'movies/submit_rating.html', {
            'movie': movie,
            'existing_rating': existing_rating,
        })
