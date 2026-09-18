from pydantic import BaseModel, Field


class DateTimeInput(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")

    time: str = Field(description="Time in HH:MM 24-hour format")
