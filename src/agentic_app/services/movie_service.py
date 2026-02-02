"""Movie service with mock data for testing conversational models.

Provides a mock movie database with search and filtering capabilities
using fuzzy matching to generate realistic confidence scores.
"""

from difflib import SequenceMatcher

from agentic_app.models.domain.movie import Actor, Movie, MovieQuery
from agentic_app.models.payloads.selection import ScoredCandidate

# Matching thresholds
TITLE_MATCH_THRESHOLD = 0.5
ACTOR_MATCH_THRESHOLD = 0.5
DIRECTOR_MATCH_THRESHOLD = 0.5
ACTOR_SEARCH_THRESHOLD = 0.6
FUZZY_TITLE_THRESHOLD = 0.3


def _similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio between 0.0 and 1.0."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _contains_match(haystack: str, needle: str) -> float:
    """Check if needle is contained in haystack, return similarity score."""
    haystack_lower = haystack.lower()
    needle_lower = needle.lower()
    if needle_lower in haystack_lower:
        return 1.0
    return _similarity(haystack_lower, needle_lower)


# =============================================================================
# Mock Data: Famous Actors
# =============================================================================
ACTORS: dict[str, Actor] = {
    "dicaprio": Actor(
        id="actor_001",
        name="Leonardo DiCaprio",
        birth_year=1974,
        nationality="American",
    ),
    "bale": Actor(
        id="actor_002",
        name="Christian Bale",
        birth_year=1974,
        nationality="British",
    ),
    "freeman": Actor(
        id="actor_003",
        name="Morgan Freeman",
        birth_year=1937,
        nationality="American",
    ),
    "johansson": Actor(
        id="actor_004",
        name="Scarlett Johansson",
        birth_year=1984,
        nationality="American",
    ),
    "portman": Actor(
        id="actor_005",
        name="Natalie Portman",
        birth_year=1981,
        nationality="Israeli-American",
    ),
    "blanchett": Actor(
        id="actor_006",
        name="Cate Blanchett",
        birth_year=1969,
        nationality="Australian",
    ),
    "hanks": Actor(
        id="actor_007",
        name="Tom Hanks",
        birth_year=1956,
        nationality="American",
    ),
    "damon": Actor(
        id="actor_008",
        name="Matt Damon",
        birth_year=1970,
        nationality="American",
    ),
    "pitt": Actor(
        id="actor_009",
        name="Brad Pitt",
        birth_year=1963,
        nationality="American",
    ),
    "jackson": Actor(
        id="actor_010",
        name="Samuel L. Jackson",
        birth_year=1948,
        nationality="American",
    ),
    "ledger": Actor(
        id="actor_011",
        name="Heath Ledger",
        birth_year=1979,
        nationality="Australian",
    ),
}


# =============================================================================
# Mock Data: Movies
# =============================================================================
MOVIES: list[Movie] = [
    Movie(
        id="mov_001",
        title="Inception",
        year=2010,
        director="Christopher Nolan",
        genres=["Sci-Fi", "Thriller", "Action"],
        cast=[ACTORS["dicaprio"]],
        rating=8.8,
        runtime_minutes=148,
    ),
    Movie(
        id="mov_002",
        title="The Dark Knight",
        year=2008,
        director="Christopher Nolan",
        genres=["Action", "Crime", "Drama"],
        cast=[ACTORS["bale"], ACTORS["ledger"], ACTORS["freeman"]],
        rating=9.0,
        runtime_minutes=152,
    ),
    Movie(
        id="mov_003",
        title="Batman Begins",
        year=2005,
        director="Christopher Nolan",
        genres=["Action", "Adventure"],
        cast=[ACTORS["bale"], ACTORS["freeman"]],
        rating=8.2,
        runtime_minutes=140,
    ),
    Movie(
        id="mov_004",
        title="The Dark Knight Rises",
        year=2012,
        director="Christopher Nolan",
        genres=["Action", "Adventure"],
        cast=[ACTORS["bale"]],
        rating=8.4,
        runtime_minutes=164,
    ),
    Movie(
        id="mov_005",
        title="Titanic",
        year=1997,
        director="James Cameron",
        genres=["Drama", "Romance"],
        cast=[ACTORS["dicaprio"]],
        rating=7.9,
        runtime_minutes=194,
    ),
    Movie(
        id="mov_006",
        title="Interstellar",
        year=2014,
        director="Christopher Nolan",
        genres=["Sci-Fi", "Adventure", "Drama"],
        cast=[ACTORS["damon"]],
        rating=8.7,
        runtime_minutes=169,
    ),
    Movie(
        id="mov_007",
        title="The Departed",
        year=2006,
        director="Martin Scorsese",
        genres=["Crime", "Thriller", "Drama"],
        cast=[ACTORS["dicaprio"], ACTORS["damon"]],
        rating=8.5,
        runtime_minutes=151,
    ),
    Movie(
        id="mov_008",
        title="Forrest Gump",
        year=1994,
        director="Robert Zemeckis",
        genres=["Drama", "Romance"],
        cast=[ACTORS["hanks"]],
        rating=8.8,
        runtime_minutes=142,
    ),
    Movie(
        id="mov_009",
        title="Saving Private Ryan",
        year=1998,
        director="Steven Spielberg",
        genres=["War", "Drama"],
        cast=[ACTORS["hanks"], ACTORS["damon"]],
        rating=8.6,
        runtime_minutes=169,
    ),
    Movie(
        id="mov_010",
        title="Pulp Fiction",
        year=1994,
        director="Quentin Tarantino",
        genres=["Crime", "Drama"],
        cast=[ACTORS["jackson"]],
        rating=8.9,
        runtime_minutes=154,
    ),
    Movie(
        id="mov_011",
        title="Black Swan",
        year=2010,
        director="Darren Aronofsky",
        genres=["Thriller", "Drama"],
        cast=[ACTORS["portman"]],
        rating=8.0,
        runtime_minutes=108,
    ),
    Movie(
        id="mov_012",
        title="The Avengers",
        year=2012,
        director="Joss Whedon",
        genres=["Action", "Sci-Fi", "Adventure"],
        cast=[ACTORS["johansson"], ACTORS["jackson"]],
        rating=8.0,
        runtime_minutes=143,
    ),
    Movie(
        id="mov_013",
        title="Lost in Translation",
        year=2003,
        director="Sofia Coppola",
        genres=["Drama", "Romance"],
        cast=[ACTORS["johansson"]],
        rating=7.7,
        runtime_minutes=102,
    ),
    Movie(
        id="mov_014",
        title="The Lord of the Rings: The Fellowship of the Ring",
        year=2001,
        director="Peter Jackson",
        genres=["Fantasy", "Adventure"],
        cast=[ACTORS["blanchett"]],
        rating=8.8,
        runtime_minutes=178,
    ),
    Movie(
        id="mov_015",
        title="Fight Club",
        year=1999,
        director="David Fincher",
        genres=["Drama", "Thriller"],
        cast=[ACTORS["pitt"]],
        rating=8.8,
        runtime_minutes=139,
    ),
]


class MovieService:
    """Service for searching and retrieving movie data.

    Provides methods for querying the mock movie database
    with fuzzy matching and filtering capabilities.
    """

    def __init__(self, movies: list[Movie] | None = None) -> None:
        """Initialize with optional custom movie list.

        Args:
            movies: Custom movie list. Defaults to built-in mock data.
        """
        super().__init__()
        self._movies = movies if movies is not None else MOVIES
        self._movies_by_id = {m.id: m for m in self._movies}

    def get_all_movies(self) -> list[Movie]:
        """Return all movies in the database."""
        return list(self._movies)

    def get_by_id(self, movie_id: str) -> Movie | None:
        """Get a movie by its unique ID.

        Args:
            movie_id: The movie's unique identifier.

        Returns:
            The movie if found, None otherwise.
        """
        return self._movies_by_id.get(movie_id)

    def get_by_actor(self, actor_name: str) -> list[Movie]:
        """Get all movies featuring an actor.

        Args:
            actor_name: Full or partial actor name.

        Returns:
            List of movies where the actor appears.
        """
        results: list[Movie] = []
        for movie in self._movies:
            for actor in movie.cast:
                if _contains_match(actor.name, actor_name) > ACTOR_SEARCH_THRESHOLD:
                    results.append(movie)
                    break
        return results

    def get_by_genre(self, genre: str) -> list[Movie]:
        """Get all movies in a genre.

        Args:
            genre: Genre name to filter by.

        Returns:
            List of movies in the genre, sorted by rating descending.
        """
        genre_lower = genre.lower()
        results = [
            movie
            for movie in self._movies
            if any(g.lower() == genre_lower for g in movie.genres)
        ]
        return sorted(results, key=lambda m: m.rating, reverse=True)

    def fuzzy_match_title(self, title: str) -> list[ScoredCandidate[Movie]]:
        """Find movies with fuzzy title matching.

        Args:
            title: Search term for title matching.

        Returns:
            List of scored candidates, sorted by score descending.
        """
        candidates: list[ScoredCandidate[Movie]] = []
        for movie in self._movies:
            score = _contains_match(movie.title, title)
            if score > FUZZY_TITLE_THRESHOLD:
                candidates.append(
                    ScoredCandidate[Movie](
                        item=movie,
                        score=score,
                        match_reason=f"Title similarity: {score:.0%}",
                    )
                )
        return sorted(candidates, key=lambda c: c.score, reverse=True)

    @staticmethod
    def _check_filters(movie: Movie, query: MovieQuery) -> bool:
        """Check year and rating filters."""
        if query.year_from is not None and movie.year < query.year_from:
            return False
        if query.year_to is not None and movie.year > query.year_to:
            return False
        return not (query.min_rating is not None and movie.rating < query.min_rating)

    @staticmethod
    def _score_movie(
        movie: Movie, query: MovieQuery
    ) -> tuple[bool, list[float], list[str]]:
        """Score a movie against query criteria.

        Returns:
            Tuple of (matches, scores, reasons).
        """
        scores: list[float] = []
        reasons: list[str] = []

        # Title matching
        if query.title is not None:
            title_score = _contains_match(movie.title, query.title)
            if title_score < TITLE_MATCH_THRESHOLD:
                return False, [], []
            scores.append(title_score)
            reasons.append(f"title={title_score:.0%}")

        # Actor matching
        if query.actor_name is not None:
            actor_scores = [
                _contains_match(actor.name, query.actor_name) for actor in movie.cast
            ]
            if not actor_scores or max(actor_scores) < ACTOR_MATCH_THRESHOLD:
                return False, [], []
            scores.append(max(actor_scores))
            reasons.append(f"actor={max(actor_scores):.0%}")

        # Director matching
        if query.director_name is not None:
            director_score = _contains_match(movie.director, query.director_name)
            if director_score < DIRECTOR_MATCH_THRESHOLD:
                return False, [], []
            scores.append(director_score)
            reasons.append(f"director={director_score:.0%}")

        # Genre matching
        if query.genre is not None:
            genre_lower = query.genre.lower()
            if not any(g.lower() == genre_lower for g in movie.genres):
                return False, [], []
            scores.append(1.0)
            reasons.append("genre=match")

        return True, scores, reasons

    def search(self, query: MovieQuery) -> list[ScoredCandidate[Movie]]:
        """Search movies with multiple criteria.

        Applies all non-None filters and scores results based on
        how well they match the query criteria.

        Args:
            query: Search parameters.

        Returns:
            List of scored candidates matching all criteria.
        """
        if query.is_empty():
            return [
                ScoredCandidate[Movie](
                    item=movie,
                    score=movie.rating / 10.0,
                    match_reason="All movies (no filter)",
                )
                for movie in sorted(self._movies, key=lambda m: m.rating, reverse=True)
            ]

        candidates: list[ScoredCandidate[Movie]] = []
        for movie in self._movies:
            if not MovieService._check_filters(movie, query):
                continue

            matches, scores, reasons = MovieService._score_movie(movie, query)
            if not matches:
                continue

            final_score = sum(scores) / len(scores) if scores else movie.rating / 10.0
            candidates.append(
                ScoredCandidate[Movie](
                    item=movie,
                    score=final_score,
                    match_reason=", ".join(reasons) if reasons else "Filters passed",
                )
            )

        return sorted(candidates, key=lambda c: c.score, reverse=True)
