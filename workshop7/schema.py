from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class RequestVacationInfo(BaseModel):
    """Structured information extracted from a user's vacation request."""

    destination: Optional[str] = Field(
        default=None,
        description="The city, region or country the user wants to travel to.",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="The first day of the vacation, in YYYY-MM-DD format.",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="The last day of the vacation, in YYYY-MM-DD format.",
    )
    people_count: Optional[int] = Field(
        default=None,
        ge=1,
        description="The number of people travelling, including the user.",
    )
    budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="The total budget for the vacation, as a number without currency symbols.",
    )
    missing_info: list[str] = Field(
        default_factory=list,
        description=(
            "Names of the fields above that could not be determined from the message "
            "(e.g. 'destination', 'start_date', 'end_date', 'people_count', 'budget')."
        ),
    )
