import sys

import requests

r = requests.post(
    "https://icalendar.org/validator.html?json=1",
    files={"jform[ical_file]": open("output/dates.ical")},
)

r.raise_for_status()

r = r.json()
print(r.keys())


if r["errors"]:
    print("Errors:")
    for error in r["errors"]:
        print(error)
    sys.exit(1)
