import logging
import sys
from asyncio import gather
from datetime import datetime, timedelta
from typing import Callable, Generator, Iterable, TypedDict, cast

import bs4
import httpx
import uvloop
from rich.logging import RichHandler
from tqdm import tqdm

from models import Event, Events, Status
from post_process import tz

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])


class FerveItem(TypedDict):
    Name: str
    URL: str
    Hash: str
    DescriptionBrief: str
    Runtime: int
    DateTime: str
    VenueName: str
    Status: int


class FerveBrowse(TypedDict):
    Items: list[FerveItem]


def groupby[K, V](iterable: Iterable[V], key: Callable[[V], K]) -> dict[K, list[V]]:
    groups: dict[K, list[V]] = {}
    for item in iterable:
        groups.setdefault(key(item), []).append(item)
    return groups


def make_date(domain: str, date: FerveItem) -> Event.EventDate:
    start = datetime.fromisoformat(date["DateTime"]).replace(tzinfo=tz)
    duration = timedelta(minutes=date["Runtime"])

    return Event.EventDate.model_validate(
        {
            "start": start,
            "end": (start + duration),
            "venue": date["VenueName"],
            "status": Status(date["Status"]),
            "url": f"https://tix.{domain}" + date["URL"],
        }
    )


def get_event_url(domain: str, event: FerveItem) -> str:
    path = event["URL"]
    if path.count("/") == 3:
        path = path.rsplit("/", 1)[0]
    return f"https://{domain}{path.lower()}/"


def boop(
    domain: str, shows: dict[str, list[FerveItem]], descriptions: dict[str, str | None]
) -> Generator[Event, None, None]:
    for show, instances in shows.items():
        i = instances[0]
        meta = descriptions[show]
        yield Event.model_validate(
            {
                "item_hash": i["Hash"],
                "title": i["Name"],
                "url": get_event_url(domain, i),
                "html_desc": meta,
                "desc": i["DescriptionBrief"],
                "dates": [make_date(domain, instance) for instance in instances],
            }
        )


async def get_show(
    domain: str, client: httpx.AsyncClient, key: str, event: FerveItem
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
    data = cast(FerveBrowse, (await client.get(url)).json())
    shows: dict[str, list[FerveItem]] = groupby(
        data["Items"], lambda x: x["Name"].replace(" - Opening Night", "")
    )
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
    data = Events(
        events=list(boop(domain, shows, descriptions)), updated_at=datetime.now(tz)
    )
    with open(f"output/{domain}.json", "w") as f:
        f.write(data.model_dump_json(indent=2))


if __name__ == "__main__":
    uvloop.run(main(sys.argv[1:]))
