import json
import zoneinfo
from datetime import datetime

from icalendar import Calendar, Event, Timezone


def main():
    input_filename = "out.json"

    with open(input_filename) as f:
        shows = json.load(f)

    output = process(shows)

    with open("output/dates.ical", "wb") as fh:
        fh.write(output)


def process(shows):
    cal = Calendar()

    cal.add("prodid", "-//blueroom calendar//mxm.dk//")
    cal.add("version", "2.0")

    cal.add("X-WR-CALNAME", "Blueroom Theatre Events")
    cal.add("NAME", "Blueroom Theatre Events")

    refresh_interval = "PT1H"

    cal.add("source", "https://mause.me/blueroom/dates.ical")
    cal.add("REFRESH-INTERVAL", refresh_interval, parameters={"value": "DURATION"})
    cal.add("X-PUBLISHED-TTL", refresh_interval)

    tz = zoneinfo.ZoneInfo("Australia/Perth")
    cal.add_component(Timezone.from_tzinfo(tz))
    cal.add("X-WR-TIMEZONE", "Australia/Perth")

    for show in shows:
        for date in show["dates"]:
            event = Event()
            event.add("uid", show["item_hash"] + " " + date["start"])
            event.add("summary", show["title"])
            start = datetime.fromisoformat(date["start"]).astimezone(tz)
            event.add("dtstamp", start)
            event.add("dtstart", start)
            event.add("dtend", datetime.fromisoformat(date["end"]).astimezone(tz))
            event.add("location", date["venue"])
            event.add("description", (show["url"] + "\n\n\n" + show["desc"]).strip())
            cal.add_component(event)

    return cal.to_ical()


if __name__ == "__main__":
    main()
