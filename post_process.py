import json
from datetime import datetime

from icalendar import Calendar, Event

with open("out.json") as f:
    shows = json.load(f)

cal = Calendar()
for show in shows:
    for date in show["dates"]:
        event = Event()
        event.add("summary", show["title"])
        event.add("dtstart", datetime.fromisoformat(date[0]))
        event.add("dtend", datetime.fromisoformat(date[1]))
        #        event.add('location', show['url'])
        event.add("summary", show["url"])  # + '\n\n\n' + show['desc'])
        cal.add_component(event)


with open("output/dates.ical", "wb") as fh:
    fh.write(cal.to_ical())
