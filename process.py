import json
from asyncio import gather
from datetime import datetime, timedelta

import bs4
import httpx
import uvloop

url = "https://tix.blueroom.org.au/api/v1/Items/Browse"


def groupby(iterable, key):
    groups = {}
    for item in iterable:
        groups.setdefault(key(item), []).append(item)
    return groups


def make_date(date):
    start = datetime.fromisoformat(date["DateTime"])
    duration = timedelta(minutes=date["Runtime"])
    return {
        "start": start.isoformat(),
        "end": (start + duration).isoformat(),
        "venue": date["VenueName"],
        "url": "https://tix.blueroom.org.au" + date["URL"],
    }


def boop(shows, descriptions):
    for show, instances in shows.items():
        i = instances[0]
        meta = descriptions[show]
        yield {
            "item_hash": i["Hash"],
            "title": i["Name"],
            "url": "https://blueroom.org.au/" + i["URL"].rsplit("/", 1)[0],
            "html_desc": meta,
            "dates": [make_date(instance) for instance in instances],
        }


async def get_show(client, key, item_hash):
    res = (
        await client.get(
            "https://blueroom.org.au" + item_hash["URL"].rsplit("/", 1)[0].lower(),
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
        )
    ).text
    soup = bs4.BeautifulSoup(res, "html.parser")
    html_desc = soup.css.select_one(".event-desc")
    return (key, html_desc)


async def main():
    client = httpx.AsyncClient()
    data = (await client.get(url)).json()
    shows = groupby(data["Items"], lambda x: x["Name"].replace(" - Opening Night", ""))
    descriptions = dict(
        await gather(
            *[get_show(client, key, values[0]) for key, values in shows.items()]
        )
    )
    with open("out.json", "w") as f:
        json.dump(list(boop(shows, descriptions)), f, indent=2)


if __name__ == "__main__":
    uvloop.run(main())
