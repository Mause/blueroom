import json
import zoneinfo
from datetime import datetime

from icalendar import Calendar, Event, Timezone
from jinja2 import Template

template = Template(
    """\
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<a href="dates.ics?timestamp={{timestamp | urlencode}}">Download iCal</a>
"""
)

tz = zoneinfo.ZoneInfo("Australia/Perth")


def main():
    input_filename = "out.json"

    with open(input_filename) as f:
        shows = json.load(f)

    timestamp = datetime.now(tz).isoformat()

    output = process(shows, timestamp=timestamp)

    with open("output/dates.ics", "wb") as fh:
        fh.write(output)

    with open("output/index.html", "w") as fh:
        fh.write(template.render(timestamp=timestamp))


def process(shows, timestamp):
    cal = Calendar()

    cal.add("prodid", "-//blueroom calendar//mxm.dk//")
    cal.add("version", "2.0")

    cal.add("X-WR-CALNAME", "Blueroom Theatre Events")
    cal.add("NAME", "Blueroom Theatre Events")

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
            start = datetime.fromisoformat(date["start"]).astimezone(tz)
            event.add("dtstamp", start)
            event.add("dtstart", start)
            event.add("dtend", datetime.fromisoformat(date["end"]).astimezone(tz))
            event.add("location", date["venue"])
            event.add(
                "description",
                "\n\n".join([show["url"], show["desc"], f"Updated: {timestamp}"]),
            )
            event.add(
                "x-alt-desc", show["html_desc"], parameters={"fmttype": "text/html"}
            )
            cal.add_component(event)

    return cal.to_ical()


if __name__ == "__main__":
    main()
