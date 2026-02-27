import sys
import zoneinfo
from datetime import datetime
from pathlib import Path

from icalendar import Calendar, Event, Timezone

from models import Events
from sent import monitor

PERTH = zoneinfo.ZoneInfo("Australia/Perth")

fmt = lambda dt: dt.strftime("%l:%M%p, %B %e, %Y %Z")


@monitor("post_process.main", "pages")
def main() -> None:
    input_filename = Path(sys.argv[1])
    output_filename = input_filename.with_suffix(".ics")

    with open(input_filename) as f:
        data = Events.model_validate_json(f.read())

    updated_at = data.updated_at

    output = process(data, updated_at=updated_at, output_filename=output_filename)

    with open(output_filename, "wb") as fh:
        fh.write(output)


def process(data: Events, updated_at: datetime, output_filename: Path) -> bytes:
    cal = Calendar()

    name = f"{output_filename.stem} calendar".title()

    cal.add("prodid", f"-//{name}//mxm.dk//")
    cal.add("version", "2.0")

    cal.add("X-WR-CALNAME", name)
    cal.add("NAME", name)
    cal.add("color", "yellow")

    refresh_interval = "PT1H"

    cal.add("source", f"https://mause.me/blueroom/{output_filename.name}")
    cal.add("REFRESH-INTERVAL", refresh_interval, parameters={"value": "DURATION"})
    cal.add("X-PUBLISHED-TTL", refresh_interval)

    tz = zoneinfo.ZoneInfo(data.timezone)
    cal.add_component(Timezone.from_tzid(data.timezone))
    cal.add("X-WR-TIMEZONE", data.timezone)

    for show in data.events:
        for date in show.dates:
            event = Event()
            event.add("uid", f"{show.item_hash} {date.start.isoformat()}")
            event.add("summary", f"{show.title} (Tickets {date.status.name})")
            event.add("last-modified", updated_at)
            event.add("dtstamp", updated_at)
            event.add("dtstart", date.start.astimezone(tz))
            event.add("dtend", date.end.astimezone(tz))
            event.add("location", date.venue)
            event.add(
                "description",
                "\n\n".join(
                    fragment
                    for fragment in [
                        str(show.url),
                        (show.html_desc or show.desc),
                        f"Updated: {fmt(updated_at)}",
                    ]
                    if fragment
                ),
            )
            cal.add_component(event)

    return cal.to_ical()


if __name__ == "__main__":
    main()
