from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from apps.core.models import BaseModel

class Person(BaseModel):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # We will use Pillow for this later
    headshot = models.ImageField(upload_to='people/', null=True, blank=True)
    
    # PostgreSQL FTS (Uncomment if using Postgres locally)
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector'], name='person_search_gin'),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name