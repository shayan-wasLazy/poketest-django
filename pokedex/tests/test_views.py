import pytest
from unittest.mock import patch
from django.urls import reverse

from pokedex.models import FavoritePokemon
from pokedex.services import PokemonNotFound, PokemonServiceUnavailable


@pytest.mark.django_db
@patch("pokedex.views.fetch_pokemon_collection")
def test_home_renders_cards(mock_collection, client):
    mock_collection.return_value = [
        {"id": 1, "name": "Bulbasaur", "image": "https://example.com/1.png", "types": []},
        {"id": 4, "name": "Charmander", "image": "https://example.com/4.png", "types": []},
    ]
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert b"Bulbasaur" in response.content
    assert b"Charmander" in response.content


@pytest.mark.django_db
@patch("pokedex.views.fetch_pokemon_collection")
def test_home_search_filters_collection(mock_collection, client):
    mock_collection.return_value = [
        {"id": 1, "name": "Bulbasaur", "image": "", "types": []},
        {"id": 4, "name": "Charmander", "image": "", "types": []},
    ]
    response = client.get(reverse("home"), {"q": "char"})
    assert response.status_code == 200
    assert b"Charmander" in response.content
    assert b"Bulbasaur" not in response.content


@pytest.mark.django_db
@patch("pokedex.views.fetch_pokemon")
def test_detail_renders_normalized_pokemon(mock_fetch, client):
    mock_fetch.return_value = {
        "id": 25, "name": "Pikachu", "image": "https://example.com/pika.png",
        "types": ["Electric"], "abilities": ["Static"], "height": 0.4, "weight": 6.0,
        "stats": [{"name": "Hp", "value": 35}],
    }
    response = client.get(reverse("pokemon_detail", args=["pikachu"]))
    assert response.status_code == 200
    assert b"Pikachu" in response.content
    assert b"Electric" in response.content


@pytest.mark.django_db
@patch("pokedex.views.fetch_pokemon")
def test_detail_returns_404_for_unknown_pokemon(mock_fetch, client):
    mock_fetch.side_effect = PokemonNotFound
    response = client.get(reverse("pokemon_detail", args=["unknownmon"]))
    assert response.status_code == 404


@pytest.mark.django_db
@patch("pokedex.views.fetch_pokemon")
def test_detail_returns_503_when_api_is_down(mock_fetch, client):
    mock_fetch.side_effect = PokemonServiceUnavailable("upstream down")
    response = client.get(reverse("pokemon_detail", args=["pikachu"]))
    assert response.status_code == 503
    assert b"upstream down" in response.content


@pytest.mark.django_db
def test_add_favorite_creates_record(client):
    response = client.post(reverse("add_favorite"), {
        "pokemon_id": "25", "name": "pikachu",
        "sprite_url": "https://example.com/pikachu.png", "primary_type": "electric",
    })
    assert response.status_code == 302
    assert FavoritePokemon.objects.filter(pokemon_id=25, name="pikachu").exists()


@pytest.mark.django_db
def test_add_favorite_is_idempotent_for_same_pokemon(client):
    client.post(reverse("add_favorite"), {"pokemon_id": "25", "name": "pikachu"})
    client.post(reverse("add_favorite"), {"pokemon_id": "25", "name": "pikachu"})
    assert FavoritePokemon.objects.filter(pokemon_id=25).count() == 1


@pytest.mark.django_db
def test_add_favorite_rejects_invalid_id(client):
    client.post(reverse("add_favorite"), {"pokemon_id": "not-a-number", "name": "pikachu"})
    assert FavoritePokemon.objects.count() == 0


@pytest.mark.django_db
def test_remove_favorite_deletes_record(client):
    favorite = FavoritePokemon.objects.create(pokemon_id=1, name="bulbasaur")
    response = client.post(reverse("remove_favorite", args=[1]))
    assert response.status_code == 302
    assert not FavoritePokemon.objects.filter(pk=favorite.pk).exists()


@pytest.mark.django_db
def test_favorites_page_shows_saved_pokemon(client):
    FavoritePokemon.objects.create(pokemon_id=1, name="bulbasaur")
    response = client.get(reverse("favorites"))
    assert response.status_code == 200
    assert b"Bulbasaur" in response.content
