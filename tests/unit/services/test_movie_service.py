"""Tests for MovieService search and filtering functionality.

Tests the mock movie service including fuzzy matching,
multi-criteria search, and scored candidate generation.
"""


from agentic_app.models.domain.movie import MovieQuery
from agentic_app.services.movie_service import MovieService


class TestMovieServiceBasics:
    """Basic MovieService functionality tests."""

    def test_get_all_movies(self, movie_service: MovieService) -> None:
        """get_all_movies returns all movies."""
        movies = movie_service.get_all_movies()
        assert len(movies) == 15  # We have 15 movies in mock data

    def test_get_by_id_found(self, movie_service: MovieService) -> None:
        """get_by_id returns movie when found."""
        movie = movie_service.get_by_id("mov_001")
        assert movie is not None
        assert movie.title == "Inception"

    def test_get_by_id_not_found(self, movie_service: MovieService) -> None:
        """get_by_id returns None when not found."""
        movie = movie_service.get_by_id("nonexistent")
        assert movie is None


class TestMovieServiceActorSearch:
    """Tests for actor-based movie search."""

    def test_get_by_actor_dicaprio(self, movie_service: MovieService) -> None:
        """Find all DiCaprio movies."""
        movies = movie_service.get_by_actor("DiCaprio")
        assert len(movies) >= 3
        titles = [m.title for m in movies]
        assert "Inception" in titles
        assert "Titanic" in titles
        assert "The Departed" in titles

    def test_get_by_actor_partial_name(self, movie_service: MovieService) -> None:
        """Partial actor name should still match."""
        movies = movie_service.get_by_actor("Bale")
        assert len(movies) >= 3
        titles = [m.title for m in movies]
        assert "The Dark Knight" in titles
        assert "Batman Begins" in titles

    def test_get_by_actor_full_name(self, movie_service: MovieService) -> None:
        """Full actor name should match."""
        movies = movie_service.get_by_actor("Tom Hanks")
        assert len(movies) >= 2
        titles = [m.title for m in movies]
        assert "Forrest Gump" in titles
        assert "Saving Private Ryan" in titles

    def test_get_by_actor_no_matches(self, movie_service: MovieService) -> None:
        """Unknown actor returns empty list."""
        movies = movie_service.get_by_actor("Unknown Actor")
        assert len(movies) == 0


class TestMovieServiceGenreSearch:
    """Tests for genre-based movie search."""

    def test_get_by_genre_scifi(self, movie_service: MovieService) -> None:
        """Find all sci-fi movies."""
        movies = movie_service.get_by_genre("Sci-Fi")
        assert len(movies) >= 3
        titles = [m.title for m in movies]
        assert "Inception" in titles
        assert "Interstellar" in titles
        assert "The Avengers" in titles

    def test_get_by_genre_sorted_by_rating(self, movie_service: MovieService) -> None:
        """Genre results should be sorted by rating descending."""
        movies = movie_service.get_by_genre("Drama")
        # Verify sorted by rating
        ratings = [m.rating for m in movies]
        assert ratings == sorted(ratings, reverse=True)

    def test_get_by_genre_case_insensitive(self, movie_service: MovieService) -> None:
        """Genre search should be case insensitive."""
        movies_lower = movie_service.get_by_genre("action")
        movies_upper = movie_service.get_by_genre("ACTION")
        movies_mixed = movie_service.get_by_genre("Action")
        assert len(movies_lower) == len(movies_upper) == len(movies_mixed)

    def test_get_by_genre_no_matches(self, movie_service: MovieService) -> None:
        """Unknown genre returns empty list."""
        movies = movie_service.get_by_genre("Musical")
        assert len(movies) == 0


class TestMovieServiceFuzzyTitleMatch:
    """Tests for fuzzy title matching."""

    def test_exact_title_match(self, movie_service: MovieService) -> None:
        """Exact title match returns high score."""
        candidates = movie_service.fuzzy_match_title("Inception")
        assert len(candidates) >= 1
        assert candidates[0].item.title == "Inception"
        assert candidates[0].score >= 0.9

    def test_partial_title_match(self, movie_service: MovieService) -> None:
        """Partial title returns matching candidates."""
        candidates = movie_service.fuzzy_match_title("Dark Knight")
        assert len(candidates) >= 2
        titles = [c.item.title for c in candidates]
        assert "The Dark Knight" in titles

    def test_typo_title_match(self, movie_service: MovieService) -> None:
        """Typos should still match with lower score."""
        candidates = movie_service.fuzzy_match_title("Incpetion")  # Typo
        # Should find Inception with reduced score
        assert len(candidates) >= 1
        inception_candidates = [c for c in candidates if "Inception" in c.item.title]
        assert len(inception_candidates) >= 1

    def test_sorted_by_score(self, movie_service: MovieService) -> None:
        """Results should be sorted by score descending."""
        candidates = movie_service.fuzzy_match_title("Dark")
        scores = [c.score for c in candidates]
        assert scores == sorted(scores, reverse=True)

    def test_no_matches(self, movie_service: MovieService) -> None:
        """No matches returns empty list."""
        candidates = movie_service.fuzzy_match_title("Xyzabc123")
        assert len(candidates) == 0


class TestMovieServiceSearch:
    """Tests for multi-criteria search."""

    def test_search_by_title(self, movie_service: MovieService) -> None:
        """Search with title filter only."""
        candidates = movie_service.search(MovieQuery(title="Inception"))
        assert len(candidates) >= 1
        assert candidates[0].item.title == "Inception"

    def test_search_by_actor(self, movie_service: MovieService) -> None:
        """Search with actor filter only."""
        candidates = movie_service.search(MovieQuery(actor_name="DiCaprio"))
        assert len(candidates) >= 3
        titles = [c.item.title for c in candidates]
        assert "Inception" in titles

    def test_search_by_genre(self, movie_service: MovieService) -> None:
        """Search with genre filter only."""
        candidates = movie_service.search(MovieQuery(genre="Thriller"))
        assert len(candidates) >= 3

    def test_search_by_director(self, movie_service: MovieService) -> None:
        """Search with director filter."""
        candidates = movie_service.search(MovieQuery(director_name="Christopher Nolan"))
        assert len(candidates) >= 5
        directors = {c.item.director for c in candidates}
        assert all("Nolan" in d for d in directors)

    def test_search_by_year_range(self, movie_service: MovieService) -> None:
        """Search with year range filter."""
        candidates = movie_service.search(
            MovieQuery(year_from=1990, year_to=1999)
        )
        years = [c.item.year for c in candidates]
        assert all(1990 <= y <= 1999 for y in years)

    def test_search_by_min_rating(self, movie_service: MovieService) -> None:
        """Search with minimum rating filter."""
        candidates = movie_service.search(MovieQuery(min_rating=8.5))
        ratings = [c.item.rating for c in candidates]
        assert all(r >= 8.5 for r in ratings)

    def test_search_multi_criteria(self, movie_service: MovieService) -> None:
        """Search with multiple criteria (AND logic)."""
        candidates = movie_service.search(
            MovieQuery(
                genre="Drama",
                actor_name="Tom Hanks",
                year_from=1990,
                year_to=1999,
            )
        )
        # Should find Forrest Gump (1994)
        assert len(candidates) >= 1
        titles = [c.item.title for c in candidates]
        assert "Forrest Gump" in titles

    def test_search_empty_query_returns_all(
        self, movie_service: MovieService
    ) -> None:
        """Empty query returns all movies sorted by rating."""
        candidates = movie_service.search(MovieQuery())
        assert len(candidates) == 15
        # Should be sorted by rating
        ratings = [c.item.rating for c in candidates]
        assert ratings == sorted(ratings, reverse=True)

    def test_search_no_matches(self, movie_service: MovieService) -> None:
        """Search with impossible criteria returns empty."""
        candidates = movie_service.search(
            MovieQuery(
                title="Xyzqwerty12345",  # Nonsensical to avoid fuzzy matches
            )
        )
        assert len(candidates) == 0


class TestMovieServiceScenarios:
    """Realistic search scenarios from conversation flows."""

    def test_scenario_batman_search(self, movie_service: MovieService) -> None:
        """User: 'Batman movie' - should return Batman-related movies."""
        candidates = movie_service.search(MovieQuery(title="Batman"))
        # Should have Batman movies with high scores
        assert len(candidates) >= 1
        # Batman Begins should be top result (contains "Batman")
        titles = [c.item.title for c in candidates]
        assert "Batman Begins" in titles

    def test_scenario_dicaprio_filmography(
        self, movie_service: MovieService
    ) -> None:
        """User: 'Movies with DiCaprio' - list filmography."""
        candidates = movie_service.search(MovieQuery(actor_name="DiCaprio"))
        assert len(candidates) >= 3
        # Check we have his major films
        titles = [c.item.title for c in candidates]
        assert "Inception" in titles
        assert "Titanic" in titles
        assert "The Departed" in titles

    def test_scenario_90s_drama(self, movie_service: MovieService) -> None:
        """User: '90s drama' - filter by genre and decade."""
        candidates = movie_service.search(
            MovieQuery(
                genre="Drama",
                year_from=1990,
                year_to=1999,
            )
        )
        # Should include Forrest Gump, Pulp Fiction, Fight Club, Titanic
        assert len(candidates) >= 3
        for c in candidates:
            assert "Drama" in c.item.genres
            assert 1990 <= c.item.year <= 1999

    def test_scenario_nolan_scifi(self, movie_service: MovieService) -> None:
        """User: 'Christopher Nolan sci-fi' - director + genre."""
        candidates = movie_service.search(
            MovieQuery(
                director_name="Christopher Nolan",
                genre="Sci-Fi",
            )
        )
        # Should find Inception, Interstellar
        titles = [c.item.title for c in candidates]
        assert "Inception" in titles
        assert "Interstellar" in titles

    def test_scenario_top_rated_action(self, movie_service: MovieService) -> None:
        """User: 'best action movies' - genre with rating filter."""
        candidates = movie_service.search(
            MovieQuery(
                genre="Action",
                min_rating=8.0,
            )
        )
        assert len(candidates) >= 3
        # All should be high-rated action
        for c in candidates:
            assert "Action" in c.item.genres
            assert c.item.rating >= 8.0
