from calendar_service import CalendarService

calendar_service = CalendarService()

calendar_service.get_events(
    {"date": "2026-09-17", "time": "00:00"},
    {"date": "2026-12-31", "time": "23:59"},
    None,
)
