from pydantic import BaseModel, Field
from typing import Literal


class DateTimeInput(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")

    time: str = Field(description="Time in HH:MM 24-hour format")


class CalendarAgentResponse(BaseModel):
    status: Literal["success", "needs_approval", "cancelled", "error"]
    message: str = Field(description="Human-readable response for the user")
    events_affected: list[str] = Field(
        default_factory=list,
        description="IDs of calendar events affected by the request",
    )
