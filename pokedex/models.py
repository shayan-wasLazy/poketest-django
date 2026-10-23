from django.db import models

class FavoritePokemon(models.Model):
    pokemon_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=80)
    sprite_url = models.URLField(blank=True)
    primary_type = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"#{self.pokemon_id} {self.name.title()}"
