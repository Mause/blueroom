import json
import sys
import zoneinfo
from datetime import datetime
from pathlib import Path

from icalendar import Calendar, Event, Timezone

tz = zoneinfo.ZoneInfo("Australia/Perth")

fmt = lambda dt: dt.strftime("%l:%M%p, %B %e, %Y")


def main():
    input_filename = Path(sys.argv[1])
    output_filename = input_filename.with_suffix(".ics")

    with open(input_filename) as f:
        shows = json.load(f)

    timestamp = datetime.now(tz)

    output = process(shows, timestamp=timestamp)

    with open(output_filename, "wb") as fh:
        fh.write(output)


def process(shows, timestamp):
    cal = Calendar()

    cal.add("prodid", "-//blueroom calendar//mxm.dk//")
    cal.add("version", "2.0")

    cal.add("X-WR-CALNAME", "Blueroom Theatre Events")
    cal.add("NAME", "Blueroom Theatre Events")
    cal.add("color", "yellow")

    refresh_interval = "PT1H"

    cal.add("source", "https://mause.me/blueroom/dates.ics")
    cal.add("REFRESH-INTERVAL", refresh_interval, parameters={"value": "DURATION"})
    cal.add("X-PUBLISHED-TTL", refresh_interval)

    cal.add_component(Timezone.from_tzinfo(tz))
    cal.add("X-WR-TIMEZONE", "Australia/Perth")

    for show in shows:
        for date in show["dates"]:
            event = Event()
            event.add("uid", show["item_hash"] + " " + date["start"])
            event.add("summary", show["title"])
            event.add("last-modified", timestamp)
            event.add("dtstamp", timestamp)
            event.add("dtstart", datetime.fromisoformat(date["start"]).astimezone(tz))
            event.add("dtend", datetime.fromisoformat(date["end"]).astimezone(tz))
            event.add("location", date["venue"])
            event.add(
                "description",
                "\n\n".join(
                    [show["url"], show["html_desc"], f"Updated: {fmt(timestamp)}"]
                ),
            )
            cal.add_component(event)

    return cal.to_ical()


if __name__ == "__main__":
    main()
