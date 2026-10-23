# PokéTest — Django + pytest Quality Assurance Lab

A responsive Pokémon explorer built to demonstrate automated testing for Django applications. The app uses PokéAPI for live data, stores favorites locally, and tests external HTTP calls with mocks so the test suite does not depend on the live service.

## Features
- Responsive Pokédex UI with search, type filters, Pokémon cards and detail pages.
- Detail view with types, abilities, base stats and artwork.
- Favorites stored in Django's database.
- Graceful handling of missing Pokémon, timeouts and upstream API failures.
- pytest unit and Django client tests; external HTTP calls are mocked.
- HTML coverage reports via pytest-cov.
- GitHub Actions CI workflow.

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000.

## Run tests

```powershell
pytest
pytest --cov=pokedex --cov-report=term-missing --cov-report=html
```

Open `htmlcov/index.html` to inspect line coverage. Coverage shows which lines ran; it does **not** prove assertions are meaningful or that requirements are correct.

## Testing concepts demonstrated
- **Testing pyramid:** many focused unit tests, fewer request/database integration tests, and a small number of end-to-end checks.
- **Unit tests:** validate API payload normalization and type filtering in isolation.
- **Integration/API tests:** use Django's test client and test database to verify route behavior and favorites.
- **Fixtures:** reusable sample payloads and Django clients.
- **Mocks:** patch the API service's HTTP request boundary to simulate success, 404, 500, and timeout responses without network access.

## Project layout

```
config/                 Django project configuration
pokedex/                app, API client, models, views and tests
templates/              responsive HTML templates
static/css/styles.css   UI styling
.github/workflows/      CI test workflow
pytest.ini              pytest and coverage configuration
```

## API
Uses the public [PokéAPI](https://pokeapi.co/docs/v2) endpoint `https://pokeapi.co/api/v2/pokemon/{name-or-id}/`. No API key is required.

## Notes
- The first page requests a curated set of Pokémon from PokéAPI, then filters the loaded collection in the browser for a snappy experience.
- Live pages require an internet connection; tests do not.
- This is an educational project, not affiliated with Nintendo, Game Freak or The Pokémon Company.
