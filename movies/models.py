from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from django.db.models import Avg

# Genre Model
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Movie Model
class Movie(models.Model):
    LANGUAGE_CHOICES = [
        ('Marathi', 'Marathi'),
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('South', 'South'),
        ('Telugu', 'Telugu'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    genre = models.ManyToManyField(Genre, related_name='movies')
    release_date = models.DateField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='Marathi')
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('100.00'))
    featured = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title

    def update_average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
        self.average_rating = round(avg, 2)
        self.save()

# Cast Model
class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast')
    actor_name = models.CharField(max_length=100)
    character_name = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='cast_profiles/', blank=True, null=True)

    def __str__(self):
        if self.character_name:
            return f"{self.actor_name} as {self.character_name}"
        return self.actor_name

# Theatre Model
class Theatre(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    total_screens = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.location})"

# ShowDate Model
class ShowDate(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE, related_name='show_dates')

    class Meta:
        unique_together = ('movie', 'date', 'theatre')

    def __str__(self):
        return f"{self.movie.title} on {self.date} at {self.theatre.name}"

# ShowTime Model
class ShowTime(models.Model):
    show_date = models.ForeignKey(ShowDate, on_delete=models.CASCADE, related_name='show_times')
    time = models.TimeField()

    class Meta:
        unique_together = ('show_date', 'time')
        ordering = ['time']

    def __str__(self):
        return f"{self.show_date.movie.title} on {self.show_date.date} at {self.time}"

# Song Model
class Song(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='songs/')
    thumbnail = models.ImageField(upload_to='songs/thumbnails/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.movie.title}"

# Movie Rating Model
class MovieRating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self):
        return f"{self.user.email} rated {self.movie.title} - {self.rating}/10"
