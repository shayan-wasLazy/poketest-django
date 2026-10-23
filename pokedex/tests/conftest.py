import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def bulbasaur_payload():
    return {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "sprites": {
            "front_default": "https://example.com/bulbasaur.png",
            "other": {"official-artwork": {"front_default": "https://example.com/art.png"}},
        },
        "types": [
            {"slot": 2, "type": {"name": "poison"}},
            {"slot": 1, "type": {"name": "grass"}},
        ],
        "abilities": [{"ability": {"name": "overgrow"}}, {"ability": {"name": "chlorophyll"}}],
        "stats": [
            {"base_stat": 45, "stat": {"name": "hp"}},
            {"base_stat": 49, "stat": {"name": "attack"}},
        ],
    }
