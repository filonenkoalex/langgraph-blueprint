"""Movie domain models for film and actor entities.

Provides models for movies, actors, search queries,
and recommendations used in conversational interactions.
"""

from pydantic import BaseModel, Field


class Actor(BaseModel):
    """A film actor with biographical information.

    Attributes:
        id: Unique identifier.
        name: Full name of the actor.
        birth_year: Year of birth.
        nationality: Country of origin.
    """

    id: str = Field(description="Unique identifier.")
    name: str = Field(description="Full name of the actor.")
    birth_year: int | None = Field(default=None, description="Year of birth.")
    nationality: str | None = Field(default=None, description="Country of origin.")


class Movie(BaseModel):
    """A film with full metadata and cast information.

    Attributes:
        id: Unique identifier.
        title: Movie title.
        year: Release year.
        director: Director's name.
        genres: List of genre tags.
        cast: List of actors in the film.
        rating: Rating out of 10.
        runtime_minutes: Duration in minutes.
    """

    id: str = Field(description="Unique identifier.")
    title: str = Field(description="Movie title.")
    year: int = Field(description="Release year.")
    director: str = Field(description="Director's name.")
    genres: list[str] = Field(default_factory=list, description="List of genre tags.")
    cast: list[Actor] = Field(default_factory=list, description="List of actors.")
    rating: float = Field(ge=0.0, le=10.0, description="Rating out of 10.")
    runtime_minutes: int | None = Field(
        default=None, description="Duration in minutes."
    )


class MovieQuery(BaseModel):
    """Search parameters for finding movies.

    All fields are optional to support partial queries.
    Multiple fields create an AND filter.

    Attributes:
        title: Partial or full title to match.
        actor_name: Actor name to search for.
        director_name: Director name to filter by.
        genre: Genre to filter by.
        year_from: Minimum release year (inclusive).
        year_to: Maximum release year (inclusive).
        min_rating: Minimum rating threshold.
    """

    title: str | None = Field(
        default=None, description="Partial or full title to match."
    )
    actor_name: str | None = Field(
        default=None, description="Actor name to search for."
    )
    director_name: str | None = Field(
        default=None, description="Director name to filter by."
    )
    genre: str | None = Field(default=None, description="Genre to filter by.")
    year_from: int | None = Field(
        default=None, description="Minimum release year (inclusive)."
    )
    year_to: int | None = Field(
        default=None, description="Maximum release year (inclusive)."
    )
    min_rating: float | None = Field(
        default=None, ge=0.0, le=10.0, description="Minimum rating."
    )

    def is_empty(self) -> bool:
        """Check if the query has no filters set."""
        return all(
            v is None
            for v in [
                self.title,
                self.actor_name,
                self.director_name,
                self.genre,
                self.year_from,
                self.year_to,
                self.min_rating,
            ]
        )


class MovieRecommendation(BaseModel):
    """A movie recommendation with reasoning.

    Attributes:
        movie: The recommended movie.
        reason: Explanation for the recommendation.
        similar_titles: Related movies the user might also like.
    """

    movie: Movie = Field(description="The recommended movie.")
    reason: str = Field(description="Explanation for the recommendation.")
    similar_titles: list[str] = Field(
        default_factory=list,
        description="Related movies the user might also like.",
    )
