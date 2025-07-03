import json
import sys
from asyncio import gather
from datetime import datetime, timedelta

import bs4
import httpx
import uvloop
from tqdm import tqdm


def groupby(iterable, key):
    groups = {}
    for item in iterable:
        groups.setdefault(key(item), []).append(item)
    return groups


def make_date(domain, date):
    start = datetime.fromisoformat(date["DateTime"])
    duration = timedelta(minutes=date["Runtime"])
    return {
        "start": start.isoformat(),
        "end": (start + duration).isoformat(),
        "venue": date["VenueName"],
        "url": f"https://tix.{domain}" + date["URL"],
    }


def get_event_url(domain: str, event: dict) -> str:
    path = event["URL"]
    if path.count("/") == 3:
        path = path.rsplit("/", 1)[0]
    return f"https://{domain}{path.lower()}/"


def boop(domain, shows, descriptions):
    for show, instances in shows.items():
        i = instances[0]
        meta = descriptions[show]
        yield {
            "item_hash": i["Hash"],
            "title": i["Name"],
            "url": get_event_url(domain, i),
            "html_desc": meta,
            "desc": i["DescriptionBrief"],
            "dates": [make_date(domain, instance) for instance in instances],
        }


async def get_show(
    domain: str, client: httpx.AsyncClient, key: str, event: dict
) -> tuple[str, str | None]:
    res = (
        await client.get(
            get_event_url(domain, event),
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
        )
    ).text
    soup = bs4.BeautifulSoup(res, "html.parser")
    html_desc = soup.css.select_one(".event-desc")
    return (key, str(html_desc) if html_desc else None)


async def main(argv: list[str]) -> None:
    domain = argv[0] if argv else "blueroom.org.au"
    url = f"https://tix.{domain}/api/v1/Items/Browse"
    client = httpx.AsyncClient()
    data = (await client.get(url)).json()
    shows = groupby(data["Items"], lambda x: x["Name"].replace(" - Opening Night", ""))
    descriptions = dict(
        tqdm(
            await gather(
                *[
                    get_show(domain, client, key, values[0])
                    for key, values in shows.items()
                ]
            )
        )
    )
    with open(f"output/{domain}.json", "w") as f:
        json.dump(list(boop(domain, shows, descriptions)), f, indent=2)


if __name__ == "__main__":
    uvloop.run(main(sys.argv[1:]))
