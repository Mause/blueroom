from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template
from yarl import URL

from post_process import fmt, tz


def generate_url(path: str, timestamp: str) -> str:
    return URL("https://calendar.google.com/calendar/render").with_query(
        cid=str(
            URL(f"http://mause.me/blueroom/{path}").with_query(timestamp=timestamp)
        ),
    )


template = Template(
    """\
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<h1>Events</h1>
<ul>
{% for file in files %}
<li>
<a href="{{generate_url(file.name, timestamp)}}">Add {{file.stem}} to Google Calendar</a>
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
        timestamp=fmt(timestamp), files=list(files), generate_url=generate_url
    )
    with open("output/index.html", "w") as fh:
        fh.write(html)


if __name__ == "__main__":
    main()
