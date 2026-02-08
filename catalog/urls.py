"""catalog URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.apiListView, name="api-list"),
    path("api/<int:apiId>/", views.apiDetailView, name="api-detail"),
]
