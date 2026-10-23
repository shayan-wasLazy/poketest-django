"""Small, testable boundary around the external PokéAPI."""
import requests

API_BASE_URL = "https://pokeapi.co/api/v2"
TIMEOUT_SECONDS = 5


class PokemonNotFound(Exception):
    """The requested Pokémon does not exist."""


class PokemonServiceUnavailable(Exception):
    """The upstream service could not provide usable data."""


def _get_json(url):
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        if response.status_code == 404:
            raise PokemonNotFound("We couldn't find that Pokémon.")
        response.raise_for_status()
        return response.json()
    except PokemonNotFound:
        raise
    except (requests.Timeout, requests.ConnectionError) as exc:
        raise PokemonServiceUnavailable("PokéAPI is taking a break. Try again shortly.") from exc
    except requests.HTTPError as exc:
        raise PokemonServiceUnavailable("PokéAPI returned an unexpected response.") from exc
    except (requests.RequestException, ValueError) as exc:
        raise PokemonServiceUnavailable("PokéAPI returned data we couldn't read.") from exc


def normalize_pokemon(payload):
    """Convert a PokéAPI detail payload into the small shape used by the UI."""
    sprites = payload.get("sprites") or {}
    other = sprites.get("other") or {}
    artwork = (other.get("official-artwork") or {}).get("front_default")
    image = artwork or sprites.get("front_default") or ""
    types = sorted(payload.get("types") or [], key=lambda item: item.get("slot", 0))
    stats = [
        {"name": item.get("stat", {}).get("name", "unknown").replace("-", " ").title(),
         "value": int(item.get("base_stat", 0))}
        for item in payload.get("stats", [])
    ]
    return {
        "id": int(payload["id"]),
        "name": str(payload["name"]).title(),
        "image": image,
        "types": [item.get("type", {}).get("name", "unknown").title() for item in types],
        "abilities": [item.get("ability", {}).get("name", "unknown").replace("-", " ").title()
                      for item in payload.get("abilities", [])],
        "height": int(payload.get("height", 0)) / 10,
        "weight": int(payload.get("weight", 0)) / 10,
        "stats": stats,
    }


def fetch_pokemon(identifier):
    """Fetch one Pokémon by name or Pokédex number."""
    key = str(identifier).strip().lower()
    if not key or not (key.isdigit() or key.replace("-", "").isalpha()):
        raise PokemonNotFound("Enter a valid Pokémon name or Pokédex number.")
    return normalize_pokemon(_get_json(f"{API_BASE_URL}/pokemon/{key}/"))


def fetch_pokemon_collection(limit=24):
    """Fetch a lightweight list response; no per-Pokémon requests needed."""
    payload = _get_json(f"{API_BASE_URL}/pokemon?limit={int(limit)}")
    results = payload.get("results", [])
    pokemon = []
    for item in results:
        url = item.get("url", "")
        try:
            pokemon_id = int(url.rstrip("/").split("/")[-1])
        except (ValueError, IndexError):
            continue
        pokemon.append({
            "id": pokemon_id,
            "name": item.get("name", "unknown").title(),
            "image": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png",
            "types": [],
        })
    return pokemon
