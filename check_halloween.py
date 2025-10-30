from domain.entities.event_promotion import EventType

print("All EventType values:")
for e in EventType:
    print(f"  - {e.name}: {e.value}")

print("\nChecking Halloween...")
halloween_exists = any(e.name == "HALLOWEEN" for e in EventType)
print(f"Halloween exists: {halloween_exists}")

if halloween_exists:
    halloween = EventType.HALLOWEEN
    print(f"Halloween value: {halloween.value}")
