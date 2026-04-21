from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.titles.models import Title

class Watchlist(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='watchlisted_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'], name='unique_watchlist_entry')
        ]

    def __str__(self):
        return f"{self.user.username}'s Watchlist: {self.title.title}"

class CustomList(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_lists')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s List: {self.name}"

class CustomListItem(BaseModel):
    custom_list = models.ForeignKey(CustomList, on_delete=models.CASCADE, related_name='items')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='listed_in')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['custom_list', 'title'], name='unique_custom_list_item')
        ]

    def __str__(self):
        return f"{self.title.title} in {self.custom_list.name}"


class SavedList(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_lists')
    custom_list = models.ForeignKey('CustomList', on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'custom_list'], name='unique_saved_list')
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.custom_list.name}"