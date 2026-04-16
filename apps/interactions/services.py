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
        # 1. Create or update the user's rating
        rating, created = Rating.objects.update_or_create(
            user=user,
            title_id=title_id,
            defaults={'value': value}
        )

        # 2. Ask Postgres to calculate the new average and count
        aggregate = Rating.objects.filter(title_id=title_id, is_deleted=False).aggregate(
            avg=models.Avg('value'),
            count=models.Count('id')
        )

        # 3. Save the new average directly onto the Movie table
        Title.objects.filter(id=title_id).update(
            avg_rating=aggregate['avg'] or 0.00,
            rating_count=aggregate['count'] or 0
        )
        
        return rating