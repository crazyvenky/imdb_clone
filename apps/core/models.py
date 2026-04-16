import uuid
from django.db import models
from django.utils import timezone
from .managers import SoftDeleteManager

class BaseModel(models.Model):
    """Abstract base model with UUID, timestamps, and soft delete."""
    
    # Security & Indexing: UUIDs prevent URL scraping, db_index speeds up sorting
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Apply our custom manager
    objects = SoftDeleteManager()
    all_objects = models.Manager() # Fallback to view deleted records if needed in Admin

    class Meta:
        abstract = True # This tells Django NOT to create a standalone table for this model

    def soft_delete(self):
        """Custom method to safely remove a record from the active site."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])