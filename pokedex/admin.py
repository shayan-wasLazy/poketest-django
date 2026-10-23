from django.contrib import admin
from .models import FavoritePokemon

@admin.register(FavoritePokemon)
class FavoritePokemonAdmin(admin.ModelAdmin):
    list_display = ("pokemon_id", "name", "primary_type", "created_at")
    search_fields = ("name",)
    ordering = ("pokemon_id",)
