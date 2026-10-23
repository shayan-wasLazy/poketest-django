from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import FavoritePokemon
from .services import (
    PokemonNotFound,
    PokemonServiceUnavailable,
    fetch_pokemon,
    fetch_pokemon_collection,
)


def home(request):
    query = request.GET.get("q", "").strip()
    selected_type = request.GET.get("type", "").strip().lower()
    error = ""
    pokemon = []
    try:
        pokemon = fetch_pokemon_collection(limit=36)
    except PokemonServiceUnavailable as exc:
        error = str(exc)

    # Search/filter the lightweight collection in the browser; keep server-side
    # filtering for query parameters so links and automated tests remain useful.
    if query:
        pokemon = [item for item in pokemon if query.lower() in item["name"].lower()
                   or query == str(item["id"])]
    if selected_type:
        # The collection endpoint doesn't include types; cards show their type
        # after the detail page is opened. Avoid pretending this filter is exact.
        messages.info(request, "Type filtering is available after Pokémon data loads on the client.")
    favorite_ids = set(FavoritePokemon.objects.values_list("pokemon_id", flat=True))
    return render(request, "pokedex/home.html", {
        "pokemon": pokemon,
        "query": query,
        "selected_type": selected_type,
        "error": error,
        "favorite_ids": favorite_ids,
    })


def pokemon_detail(request, identifier):
    try:
        pokemon = fetch_pokemon(identifier)
    except PokemonNotFound:
        return render(request, "pokedex/not_found.html", status=404)
    except PokemonServiceUnavailable as exc:
        return render(request, "pokedex/error.html", {"error": str(exc)}, status=503)
    pokemon["primary_type"] = pokemon["types"][0].lower() if pokemon["types"] else ""
    pokemon["is_favorite"] = FavoritePokemon.objects.filter(pokemon_id=pokemon["id"]).exists()
    return render(request, "pokedex/detail.html", {"pokemon": pokemon})


def favorites(request):
    return render(request, "pokedex/favorites.html", {
        "favorites": FavoritePokemon.objects.all(),
    })


@require_POST
def add_favorite(request):
    try:
        pokemon_id = int(request.POST.get("pokemon_id", ""))
        name = request.POST.get("name", "").strip().lower()
    except (TypeError, ValueError):
        messages.error(request, "That Pokémon could not be saved.")
        return redirect("home")
    if pokemon_id < 1 or not name or len(name) > 80:
        messages.error(request, "That Pokémon could not be saved.")
        return redirect("home")
    sprite_url = request.POST.get("sprite_url", "").strip()
    primary_type = request.POST.get("primary_type", "").strip().lower()[:30]
    FavoritePokemon.objects.update_or_create(
        pokemon_id=pokemon_id,
        defaults={"name": name, "sprite_url": sprite_url, "primary_type": primary_type},
    )
    messages.success(request, f"{name.title()} was added to your collection.")
    return redirect(request.POST.get("next") or "favorites")


@require_POST
def remove_favorite(request, pokemon_id):
    favorite = get_object_or_404(FavoritePokemon, pokemon_id=pokemon_id)
    favorite.delete()
    messages.success(request, "Pokémon removed from your collection.")
    return redirect("favorites")
