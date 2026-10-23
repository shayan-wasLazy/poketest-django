import requests
import pytest
from unittest.mock import Mock, patch

from pokedex.services import (
    PokemonNotFound,
    PokemonServiceUnavailable,
    fetch_pokemon,
    fetch_pokemon_collection,
    normalize_pokemon,
)


def test_normalize_pokemon_maps_core_fields(bulbasaur_payload):
    result = normalize_pokemon(bulbasaur_payload)
    assert result["id"] == 1
    assert result["name"] == "Bulbasaur"
    assert result["image"] == "https://example.com/art.png"
    assert result["types"] == ["Grass", "Poison"]
    assert result["abilities"] == ["Overgrow", "Chlorophyll"]
    assert result["height"] == 0.7
    assert result["weight"] == 6.9
    assert result["stats"][0] == {"name": "Hp", "value": 45}


def test_normalize_pokemon_handles_missing_optional_fields():
    result = normalize_pokemon({"id": 25, "name": "pikachu"})
    assert result["image"] == ""
    assert result["types"] == []
    assert result["abilities"] == []
    assert result["stats"] == []


@patch("pokedex.services.requests.get")
def test_fetch_pokemon_uses_api_and_timeout(mock_get, bulbasaur_payload):
    response = Mock()
    response.status_code = 200
    response.json.return_value = bulbasaur_payload
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    pokemon = fetch_pokemon("Bulbasaur")

    assert pokemon["name"] == "Bulbasaur"
    mock_get.assert_called_once_with(
        "https://pokeapi.co/api/v2/pokemon/bulbasaur/", timeout=5
    )


@patch("pokedex.services.requests.get")
def test_fetch_pokemon_raises_not_found_for_404(mock_get):
    response = Mock()
    response.status_code = 404
    mock_get.return_value = response
    with pytest.raises(PokemonNotFound):
        fetch_pokemon("missingno")


@patch("pokedex.services.requests.get", side_effect=requests.Timeout)
def test_fetch_pokemon_converts_timeout_to_service_error(mock_get):
    with pytest.raises(PokemonServiceUnavailable, match="taking a break"):
        fetch_pokemon("pikachu")


@patch("pokedex.services.requests.get")
def test_fetch_pokemon_converts_server_error(mock_get):
    response = Mock()
    response.status_code = 503
    response.raise_for_status.side_effect = requests.HTTPError("503")
    mock_get.return_value = response
    with pytest.raises(PokemonServiceUnavailable, match="unexpected response"):
        fetch_pokemon("pikachu")


@patch("pokedex.services.requests.get")
def test_fetch_pokemon_rejects_bad_identifier_without_network(mock_get):
    with pytest.raises(PokemonNotFound):
        fetch_pokemon("pikachu!!!")
    mock_get.assert_not_called()


@patch("pokedex.services.requests.get")
def test_collection_builds_sprite_urls(mock_get):
    response = Mock()
    response.status_code = 200
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        ]
    }
    mock_get.return_value = response
    result = fetch_pokemon_collection(2)
    assert [item["id"] for item in result] == [1, 2]
    assert result[0]["name"] == "Bulbasaur"
    assert result[1]["image"].endswith("/2.png")


@patch("pokedex.services.requests.get")
def test_fetch_pokemon_handles_malformed_json(mock_get):
    response = Mock(status_code=200)
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("not valid JSON")
    mock_get.return_value = response
    with pytest.raises(PokemonServiceUnavailable, match="couldn't read"):
        fetch_pokemon("pikachu")
