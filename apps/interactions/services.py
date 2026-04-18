from django.db import transaction, models
from apps.titles.models import Title
from .models import Rating

class InteractionService:
    @staticmethod
    @transaction.atomic
    def create_or_update_rating(user, title_id, value):
        """
        Creates or updates a rating and immediately recalculates the Title's 
        denormalized avg_rating and rating_count in a single database transaction.
        """
        rating, created = Rating.objects.update_or_create(
            user=user,
            title_id=title_id,
            defaults={'value': value}
        )

        aggregate = Rating.objects.filter(title_id=title_id, is_deleted=False).aggregate(
            avg=models.Avg('value'),
            count=models.Count('id')
        )
        Title.objects.filter(id=title_id).update(
            avg_rating=aggregate['avg'] or 0.00,
            rating_count=aggregate['count'] or 0
        )
        
        return rating