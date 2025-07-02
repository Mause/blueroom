import sys

import requests

filename = sys.argv[1]

r = requests.post(
    "https://icalendar.org/validator.html?json=1",
    files={"jform[ical_file]": "\r\n".join(open(filename).read().splitlines())},
)

r.raise_for_status()

r = r.json()

for warning in r["warnings"]:
    print(warning)

if r["errors"]:
    print("Errors:")
    for error in r["errors"]:
        print(error)
    sys.exit(1)
