from django.urls import path
from . import views


app_name = 'events'

urlpatterns = [
    path('list/', views.EventListView.as_view(), name='event_list'),
    path('detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event_update/<int:pk>/', views.EventUpdateView.as_view(), name='event_update'),
    path('event_delete/<int:pk>/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event_create/', views.EventCreateView.as_view(), name='event_create'),
    path('event_enroll/', views.EnrollCreateView.as_view(), name='enroll_create'),
    path('event_add_to_favorite/', views.EventAddToFavoriteView.as_view(), name='event_add_to_favorite'),
    ]