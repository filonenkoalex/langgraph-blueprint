"""Extraction payload for entity extraction from user input.

Provides a generic container for extraction results with
success/failure semantics and missing field tracking.
"""

from pydantic import BaseModel, Field, model_validator


class ExtractionPayload[ExtractedT: BaseModel](BaseModel):
    """Generic wrapper for entity extraction results.

    Encapsulates the outcome of extracting structured data from
    unstructured user input. Tracks success state, extracted data,
    and any fields that could not be determined.

    Type Parameters:
        ExtractedT: The specific entity type being extracted.

    Attributes:
        is_success: True if required information was successfully extracted.
        data: The extracted entity if successful, None otherwise.
        missing_fields: List of field names that could not be extracted.
        error_message: Specific error if extraction failed due to ambiguity.

    Example:
        ```python
        class FundQuery(BaseModel):
            ticker: str
            name: str | None = None

        # Successful extraction
        result = ExtractionPayload[FundQuery](
            is_success=True,
            data=FundQuery(ticker="VTI", name="Vanguard Total Stock"),
        )

        # Failed extraction
        result = ExtractionPayload[FundQuery](
            is_success=False,
            missing_fields=["ticker"],
            error_message="Could not determine which fund was referenced",
        )
        ```
    """

    is_success: bool = Field(
        description="True if the required information was found in the text.",
    )
    data: ExtractedT | None = Field(
        default=None,
        description="The extracted object if successful, otherwise null.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="List of field names that could not be extracted/found.",
    )
    error_message: str | None = Field(
        default=None,
        description="Specific error if extraction failed due to ambiguity.",
    )

    @model_validator(mode="after")
    def check_data_consistency(self) -> "ExtractionPayload[ExtractedT]":
        """Ensure data is present when extraction is successful."""
        if self.is_success and self.data is None:
            msg = "Data cannot be null if is_success is True"
            raise ValueError(msg)
        return self
