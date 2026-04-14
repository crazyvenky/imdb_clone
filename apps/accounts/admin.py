from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    # This tells the admin panel to show our custom fields alongside the default ones
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Profile Info', {'fields': ('bio', 'avatar', 'location', 'website', 'date_of_birth')}),
    )

admin.site.register(User, CustomUserAdmin)  
