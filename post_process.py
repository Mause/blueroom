import json
import zoneinfo
from datetime import datetime, timedelta

from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from ical.parsing.property import ParsedProperty
from ical.store import EventStore


def main():
    input_filename = "out.json"

    with open(input_filename) as f:
        shows = json.load(f)

    output = process(shows)

    with open("output/dates.ical", "wb") as fh:
        fh.write(output)


def process(shows):
    cal = Calendar()
    refresh_interval = timedelta(hours=1)

    tz = zoneinfo.ZoneInfo("Australia/Perth")

    cal = Calendar(
        prodid="-//blueroom calendar//mxm.dk//",
        version="2.0",
        extras=[
            ParsedProperty("x-wr-calname", value="Blueroom Theatre Events"),
            ParsedProperty("refresh_interval", value="PT1H"),
            ParsedProperty("source", value="https://mause.me/blueroom/dates.ical"),
        ],
    )
    store = EventStore(cal)

    for show in shows:
        for date in show["dates"]:
            start = datetime.fromisoformat(date["start"]).astimezone(tz)
            store.add(
                Event(
                    uid=show["item_hash"] + " " + date["start"],
                    summary=show["title"],
                    dtstamp=start,
                    dtstart=start,
                    dtend=datetime.fromisoformat(date["end"]).astimezone(tz),
                    location=date["venue"],
                    description=(show["url"] + "\n\n\n" + show["desc"]).strip(),
                )
            )

    return IcsCalendarStream.calendar_to_ics(cal)


if __name__ == "__main__":
    main()
