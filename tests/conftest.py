"""Shared pytest fixtures for all tests.

Provides common fixtures for movie service, sample data,
and conversational model instances.
"""

import pytest

from agentic_app.models.domain.movie import Actor, Movie, MovieQuery
from agentic_app.services.movie_service import ACTORS, MOVIES, MovieService


@pytest.fixture
def movie_service() -> MovieService:
    """Provide a MovieService instance with default mock data."""
    return MovieService()


@pytest.fixture
def all_actors() -> dict[str, Actor]:
    """Provide the full actor dictionary."""
    return ACTORS


@pytest.fixture
def all_movies() -> list[Movie]:
    """Provide the full movies list."""
    return MOVIES


@pytest.fixture
def sample_movie() -> Movie:
    """Provide a single sample movie (Inception)."""
    return Movie(
        id="mov_001",
        title="Inception",
        year=2010,
        director="Christopher Nolan",
        genres=["Sci-Fi", "Thriller", "Action"],
        cast=[ACTORS["dicaprio"]],
        rating=8.8,
        runtime_minutes=148,
    )


@pytest.fixture
def sample_actor() -> Actor:
    """Provide a single sample actor (DiCaprio)."""
    return ACTORS["dicaprio"]


@pytest.fixture
def empty_query() -> MovieQuery:
    """Provide an empty MovieQuery with no filters."""
    return MovieQuery()


@pytest.fixture
def title_query() -> MovieQuery:
    """Provide a MovieQuery with only title filter."""
    return MovieQuery(title="Inception")


@pytest.fixture
def actor_query() -> MovieQuery:
    """Provide a MovieQuery with only actor filter."""
    return MovieQuery(actor_name="DiCaprio")


@pytest.fixture
def genre_query() -> MovieQuery:
    """Provide a MovieQuery with only genre filter."""
    return MovieQuery(genre="Sci-Fi")


@pytest.fixture
def multi_criteria_query() -> MovieQuery:
    """Provide a MovieQuery with multiple filters."""
    return MovieQuery(
        genre="Drama",
        actor_name="Tom Hanks",
        year_from=1990,
        year_to=1999,
    )


@pytest.fixture
def batman_query() -> MovieQuery:
    """Provide a MovieQuery that matches multiple Batman movies."""
    return MovieQuery(title="Batman")
