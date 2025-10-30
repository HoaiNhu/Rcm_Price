"""Quick check: Upcoming events"""
from datetime import datetime
from utils.event_detector import EventDetector

detector = EventDetector()
events = detector.get_upcoming_events(datetime.now(), 60)

print(f"Found {len(events)} events in next 60 days:")
for e in events:
    print(f"  - {e.event_type.value} ({e.event_date}) - {e.days_until_event} days")
