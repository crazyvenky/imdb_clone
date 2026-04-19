from django.urls import path
from . import views

app_name = 'apps.search'

urlpatterns = [
    path('', views.search_results_view, name='results'),
]
