import json
from datetime import datetime

from icalendar import Calendar, Event

with open("out.json") as f:
    shows = json.load(f)

cal = Calendar()

cal.add("prodid", "-//blueroom calendar//mxm.dk//")
cal.add("version", "2.0")

cal.add("X-WR-CALNAME", "Blueroom Theatre Events")
cal.add("NAME", "Blueroom Theatre Events")

refresh_interval = "PT1H"

cal.add("REFRESH-INTERVAL", refresh_interval, parameters={"value": "DURATION"})
cal.add("X-PUBLISHED-TTL", refresh_interval)

cal.add("X-WR-TIMEZONE", "Australia/Perth")

for show in shows:
    for date in show["dates"]:
        event = Event()
        event.add("uid", show["item_hash"] + " " + date[0])
        event.add("summary", show["title"])
        start = datetime.fromisoformat(date[0])
        event.add("dtstamp", start)
        event.add("dtstart", start)
        event.add("dtend", datetime.fromisoformat(date[1]))
        #        event.add('location', show['url'])
        event.add("description", show["url"])  # + '\n\n\n' + show['desc'])
        cal.add_component(event)


with open("output/dates.ical", "wb") as fh:
    fh.write(cal.to_ical())
