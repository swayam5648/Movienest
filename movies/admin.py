from django.contrib import admin
from django.contrib import messages
from movies.models import Genre, Movie, Cast, ShowDate, ShowTime, Song, Theatre, MovieRating
from bookings.models import ShowSeat
from bookings.utils import generate_show_seats

# Genre admin
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# Cast inline inside Movie admin
class CastInline(admin.TabularInline):
    model = Cast
    extra = 1

# Song inline inside Movie admin
class SongInline(admin.TabularInline):
    model = Song
    extra = 1

# Movie admin with Cast and Song inlines + average_rating
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'release_date', 'language', 'featured', 'created_at', 'average_rating')
    list_filter = ('language', 'genre', 'featured')
    search_fields = ('title', 'description')
    filter_horizontal = ('genre',)
    inlines = [SongInline, CastInline]
    readonly_fields = ('average_rating',)

    # Update average rating on save (optional)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.update_average_rating()

# Cast admin (standalone)
@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ('actor_name', 'character_name', 'movie')
    search_fields = ('actor_name', 'character_name', 'movie__title')

# ShowTime inline inside ShowDate admin
class ShowTimeInline(admin.TabularInline):
    model = ShowTime
    extra = 1

# Theatre admin
@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'total_screens')
    search_fields = ('name', 'location')
    list_filter = ('location',)

# Custom action for seat generation
@admin.action(description="Generate Seats for selected show dates")
def generate_seats_action(modeladmin, request, queryset):
    created_count = 0
    skipped = []

    for show_date in queryset:
        movie = show_date.movie
        # Use the correct related_name
        show_times = show_date.show_times.all()
        for show_time in show_times:
            if not ShowSeat.objects.filter(movie=movie, show_date=show_date.date, show_time=show_time).exists():
                generate_show_seats(movie, show_date.date, show_time)
                created_count += 1
            else:
                skipped.append(f"{movie.title} ({show_date.date} at {show_time.time.strftime('%I:%M %p')})")

    if created_count:
        messages.success(request, f"Seats created for {created_count} show time(s).")
    if skipped:
        messages.warning(request, f"Skipped (already had seats): {', '.join(skipped)}")

# ShowDate admin
@admin.register(ShowDate)
class ShowDateAdmin(admin.ModelAdmin):
    list_display = ('movie', 'date', 'theatre')
    list_filter = ('date', 'movie', 'theatre')
    search_fields = ('movie__title', 'theatre__name')
    actions = [generate_seats_action]
    inlines = [ShowTimeInline]

# ShowTime admin
@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ('show_date', 'time')
    list_filter = ('show_date__date', 'show_date__movie')
    search_fields = ('show_date__movie__title',)

# Song admin
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'movie')
    search_fields = ('title', 'movie__title')

# MovieRating admin
@admin.register(MovieRating)
class MovieRatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'rated_at')
    list_filter = ('movie', 'rating')
    search_fields = ('movie__title', 'user__email')

    # Auto update movie average rating on rating save
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.movie.update_average_rating()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        obj.movie.update_average_rating()

    def delete_queryset(self, request, queryset):
        movies = set(q.movie for q in queryset)
        super().delete_queryset(request, queryset)
        for movie in movies:
            movie.update_average_rating()
