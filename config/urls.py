from django.contrib import admin
from django.urls import path
from pokedex import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("pokemon/<str:identifier>/", views.pokemon_detail, name="pokemon_detail"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/add/", views.add_favorite, name="add_favorite"),
    path("favorites/<int:pokemon_id>/remove/", views.remove_favorite, name="remove_favorite"),
]
