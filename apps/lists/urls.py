from django.urls import path
from . import views

app_name = 'apps.lists'

urlpatterns = [
    path('toggle/<uuid:title_id>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('', views.watchlist_view, name='watchlist'),
    path('update/<uuid:title_id>/', views.update_title_lists, name='update_title_lists'),
    path('create/', views.create_list_view, name='create_list'),
    path('custom/toggle/<uuid:title_id>/<uuid:list_id>/', views.toggle_custom_list, name='toggle_custom_list'),
    path('custom/<uuid:list_id>/', views.custom_list_detail, name='custom_list_detail'),
    
    # NEW ROUTE FOR EDITING
    path('custom/<uuid:list_id>/edit/', views.edit_list_view, name='edit_list'), 
]