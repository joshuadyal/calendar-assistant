from datetime import datetime
from zoneinfo import ZoneInfo
from definitions import DateTimeInput


def parse_datetime(date: str, time: str) -> datetime:
    return datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M").replace(
        tzinfo=ZoneInfo("Europe/London")
    )


def parse_datetimeinput(datetimeinput: DateTimeInput) -> datetime:
    return parse_datetime(datetimeinput.date, datetimeinput.time)
