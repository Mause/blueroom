from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template
from yarl import URL

from post_process import fmt, tz


def generate_ical(path: str, timestamp: str) -> URL:
    return URL(f"https://mause.me/blueroom/{path}").with_query(timestamp=timestamp)


def generate_gcal(path: str, timestamp: str) -> URL:
    return URL("https://calendar.google.com/calendar/render").with_query(
        cid=str(generate_ical(path, timestamp).with_scheme("webcal")),
    )


template = Template(
    """\
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<h1>Events</h1>
<ul>
{% for file in files %}
<li>
{{file.stem}}: 
<a href="{{generate_gcal(file.name, timestamp)}}">Google Calendar</a>, <a href="{{generate_ical(file.name, timestamp)}}">iCal</a>
</li>
{% endfor %}
</ul>
<br/>
Updated: {{timestamp}}<br/>
View the code on <a href="https://github.com/Mause/blueroom">GitHub</a>.
"""
)


def main() -> None:
    files = list(Path("output").glob("*.ics"))
    timestamp = datetime.fromtimestamp(
        files[0].stat().st_mtime, tz=timezone.utc
    ).astimezone(tz)

    html = template.render(
        timestamp=fmt(timestamp),
        files=files,
        generate_ical=generate_ical,
        generate_gcal=generate_gcal,
    )
    with open("output/index.html", "w") as fh:
        fh.write(html)


if __name__ == "__main__":
    main()
