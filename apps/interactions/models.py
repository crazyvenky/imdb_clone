from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.titles.models import Title

class Rating(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='ratings')
    value = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            
            models.UniqueConstraint(fields=['user', 'title'], name='unique_user_title_rating'),
     
            models.CheckConstraint(condition=models.Q(value__gte=1) & models.Q(value__lte=10), name='valid_rating_range')
        ]
    
        
    def __str__(self):
        return f"{self.user.username} rated {self.title.title} {self.value}/10"

class Review(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()

    class Meta:
        constraints = [
            # A user can only review a specific title once
            models.UniqueConstraint(fields=['user', 'title'], name='unique_user_title_review')
        ]

    def __str__(self):
        return f"Review by {self.user.username} for {self.title.title}"