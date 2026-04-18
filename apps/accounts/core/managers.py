from django.db import models

class SoftDeleteManager(models.Manager):
    """Filters out soft-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)