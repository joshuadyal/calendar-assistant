import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import calendar_auth
from definitions import DateTimeInput
from helpers import parse_datetimeinput


class CalendarService:
    def __init__(self):
        self.__creds = calendar_auth()
        self.__service = build("calendar", "v3", credentials=self.__creds)

    def _format_event(self, event):
        return {
            "id": event["id"],
            "title": event.get("summary", "Untitled event"),
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
        }

    def get_events(
        self,
        start: DateTimeInput | None = None,
        end: DateTimeInput | None = None,
        limit: int | None = 10,
    ):
        """Get calendar events within a given range.
        Default behaviour will get the next 10 future events.

        Args:
            start: the start datetime for the range. Default is None.
            end: the end datetime for the range. Default is None.
            limit: the maximum number of events to return, default = 10. Set to None for no limit.

        """
        try:
            # Call the Calendar API
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            start_str = parse_datetimeinput(start).isoformat()
            end_str = parse_datetimeinput(end).isoformat()
            print(f"Getting the upcoming {limit} events")
            events_result = (
                self.__service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_str,
                    timeMax=end_str,
                    maxResults=limit,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                print("No upcoming events found.")
                return

            # Prints the start and name of the next {limit} events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(event["id"], start, event["summary"])

            return [self._format_event(event) for event in events]

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_event(self, event_id):
        """Get a calendar event by its ID"""
        try:

            event = (
                self.__service.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )

            return self._format_event(event)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def create_event(
        self,
        summary: str,
        start: DateTimeInput,
        end: DateTimeInput,
        description: str = None,
        location: str = None,
        recurrence: str = None,
    ):
        """Creates an event in the calendar"""
        try:

            event = {
                "summary": summary,
                "start": {
                    "dateTime": parse_datetimeinput(start).isoformat(),
                    "timeZone": "Europe/London",
                },
                "end": {
                    "dateTime": parse_datetimeinput(end).isoformat(),
                    "timeZone": "Europe/London",
                },
            }

            if description:
                event["description"] = description

            if location:
                event["location"] = location

            if recurrence:
                event["recurrence"] = [recurrence]

            created_event = (
                self.__service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )

            return self._format_event(created_event)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def update_event(
        self,
        event_id: str,
        summary: str = None,
        start: DateTimeInput = None,
        end: DateTimeInput = None,
        description: str = None,
        location: str = None,
    ):
        try:

            body = {}

            if summary is not None:
                body["summary"] = summary

            if start is not None:
                body["start"] = {
                    "dateTime": parse_datetimeinput(start).isoformat(),
                    "timeZone": "Europe/London",
                }

            if end is not None:
                body["end"] = {
                    "dateTime": parse_datetimeinput(end).isoformat(),
                    "timeZone": "Europe/London",
                }

            if description is not None:
                body["description"] = description

            if location is not None:
                body["location"] = location

            updated_event = (
                self.__service.events()
                .patch(calendarId="primary", eventId=event_id, body=body)
                .execute()
            )

            return self._format_event(updated_event)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def delete_event(self, event_id: str):
        try:

            self.__service.events().delete(
                calendarId="primary", eventId=event_id
            ).execute()

            return True

        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def get_busy_periods(self, start: DateTimeInput, end: DateTimeInput):
        try:

            body = {
                "timeMin": parse_datetimeinput(start).isoformat(),
                "timeMax": parse_datetimeinput(end).isoformat(),
                "items": [{"id": "primary"}],
            }

            result = self.__service.freebusy().query(body=body).execute()

            return result["calendars"]["primary"]["busy"]

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def is_available(self, start: DateTimeInput, end: DateTimeInput):
        busy_periods = self.get_busy_periods(start, end)

        return len(busy_periods) == 0
