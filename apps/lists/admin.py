from django.contrib import admin
from .models import Watchlist, CustomList, CustomListItem, SavedList 


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
    search_fields = ('user__username', 'title__title')
    list_filter = ('created_at',)

@admin.register(CustomList)
class CustomListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('is_public', 'created_at')

@admin.register(CustomListItem)
class CustomListItemAdmin(admin.ModelAdmin):
    list_display = ('custom_list', 'title', 'created_at')
    search_fields = ('custom_list__name', 'title__title')
    list_filter = ('created_at',)

@admin.register(SavedList)
class SavedListAdmin(admin.ModelAdmin):
    list_display = ('user', 'custom_list', 'created_at')
    search_fields = ('user__username', 'custom_list__name')