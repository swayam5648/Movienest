from django.urls import path
from movies.views import home, movie_list, movie_detail, marathi_movies, telgu_movies ,search_movies, hindi_movies, submit_rating_view
urlpatterns = [
    path('', home, name='home'),  # Home page = Featured movies
    path('all/', movie_list, name='all_movies'),  # all movies (if needed)
    path('marathi/', marathi_movies, name='marathi_movies'),  # only Marathi
    path('hindi/', hindi_movies, name='hindi_movies'),  # only Hindi
    path('telgu/', telgu_movies, name='telgu_movies'),  # only Telgu
    path('movie/<int:pk>/', movie_detail, name='movie_detail'),  # Detail page
    path('movie/<int:movie_id>/rate/', submit_rating_view, name='submit_rating'),
    path('search/', search_movies, name='search_movies'),
]
