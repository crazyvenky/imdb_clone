from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from apps.core.models import BaseModel
from apps.people.models import Person

class Genre(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Title(BaseModel):
    class TitleType(models.TextChoices):
        MOVIE = 'MV', 'Movie'
        TV_SHOW = 'TV', 'TV Show'
        EPISODE = 'EP', 'Episode'

    type = models.CharField(max_length=2, choices=TitleType.choices, default=TitleType.MOVIE, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Self-referential FK for TV Episodes linking to their TV Show
    parent_title = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='episodes'
    )
    
    release_date = models.DateField(null=True, blank=True, db_index=True)
    runtime_minutes = models.PositiveIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='titles')
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    # --- NEW TMDB FIELDS ---
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    popularity = models.FloatField(default=0.0)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    trailer_key = models.CharField(max_length=100, null=True, blank=True)

    # Denormalized Aggregates (Updated via Interactions Service later)
    avg_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)

    # PostgreSQL FTS (Uncomment if using Postgres locally)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        # These indexes make searching and sorting lightning fast
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['-popularity']),
        ]

    def __str__(self):
        return self.title

    # Dynamic URL Property - Saves EC2 storage by hotlinking TMDB's CDN
    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        elif self.poster: # Fallback to local uploaded poster if it exists
            return self.poster.url
        return None
class TitleCast(BaseModel):
    """Bridge table connecting a Person to a Title with a specific role."""
    class RoleType(models.TextChoices):
        ACTOR = 'ACT', 'Actor'
        DIRECTOR = 'DIR', 'Director'
        WRITER = 'WRT', 'Writer'

    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='cast_members')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='credits')
    role = models.CharField(max_length=3, choices=RoleType.choices)
    character_name = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            # Prevents the exact same person from being added as the exact same character twice
            models.UniqueConstraint(fields=['title', 'person', 'role', 'character_name'], name='unique_cast_role')
        ]
        indexes = [
            models.Index(fields=['title', 'role']),
        ]

    def __str__(self):
        return f"{self.person.name} - {self.get_role_display()} in {self.title.title}"