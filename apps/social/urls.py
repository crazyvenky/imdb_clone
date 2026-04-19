from django.urls import path
from . import views

app_name = 'apps.social'

urlpatterns = [
    # Captures the username from the URL, e.g., /user/rgopal-681-895636/
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('user/<str:username>/', views.user_profile_view, name='profile'),
]

from django.urls import path
from . import views
