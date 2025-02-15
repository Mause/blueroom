import json
from asyncio import gather
from datetime import datetime, timedelta

import httpx
import uvloop
from rich import print

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
    res = await client.get(
        "https://tix.blueroom.org.au/api/v1/Events",
        params=({"itemHash": item_hash, "hash": "new"}),
    )
    # .json()
    print(res.text)
    res = json.loads(res["SuccessMessages"][0])
    print(res)
    return (key, res)


async def main():
    client = httpx.AsyncClient()
    data = (await client.get(url)).json()
    shows = groupby(data["Items"], lambda x: x["Name"].replace(" - Opening Night", ""))
    descriptions = await gather(
        *[get_show(client, key, values[0]["Hash"]) for key, values in shows.items()]
    )
    print({name: len(instances) for name, instances in shows.items()})
    print(data["Items"][0])

    with open("out.json", "w") as f:
        json.dump(list(boop(shows, descriptions)), f, indent=2)


if __name__ == "__main__":
    uvloop.run(main())
