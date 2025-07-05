from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template

from post_process import fmt, tz

template = Template(
    """\
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<h1>Events</h1>
<ul>
{% for file in files %}
<li>
<a href="{{file.name}}?timestamp={{timestamp | urlencode}}">Download {{file.stem}} iCal</a>
</li>
{% endfor %}
</ul>
<br/>
Updated: {{timestamp}}
"""
)


def main() -> None:
    files = list(Path("output").glob("*.ics"))
    timestamp = datetime.fromtimestamp(
        files[0].stat().st_mtime, tz=timezone.utc
    ).astimezone(tz)

    with open("output/index.html", "w") as fh:
        fh.write(template.render(timestamp=fmt(timestamp), files=list(files)))


if __name__ == "__main__":
    main()
