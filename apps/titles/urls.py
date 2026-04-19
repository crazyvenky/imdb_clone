from django.urls import path
from . import views

app_name = 'apps.titles'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('<uuid:pk>/', views.movie_detail_view, name='movie_detail'),
    path('browse/', views.browse_view, name='browse'),
]
