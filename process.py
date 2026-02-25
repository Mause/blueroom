import logging
import sys
from asyncio import gather
from datetime import datetime, timedelta
from typing import Callable, Generator, Iterable, TypedDict, cast

import bs4
import httpx
import uvloop
from httpx_retries import Retry, RetryTransport
from tqdm import tqdm

from models import Event, Events, Status
from post_process import tz
from sent import monitor

logger = logging.getLogger(__name__)


class FerveItem(TypedDict):
    Name: str
    URL: str
    Hash: str
    DescriptionBrief: str
    Runtime: int
    DateTime: str | None
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
        # chop off date segment
        path = path.rsplit("/", 1)[0]
    path = path.replace("-Streaming", "").replace("-Online", "")
    if path == "/Events/O-D-E":
        path = "/Events/ODE"
    if domain == "ourgoldenage.com.au":
        path = path.replace("/Events/", "/film/")
    return f"https://{domain}{path.lower()}"


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
                "dates": [
                    make_date(domain, instance)
                    for instance in instances
                    if instance["DateTime"]
                    or logger.warning(
                        "Event %r has no date, skipping", instance["Name"]
                    )
                ],
            }
        )


async def get_show(
    domain: str, client: httpx.AsyncClient, key: str, event: FerveItem
) -> tuple[str, str | None]:
    event_url = get_event_url(domain, event)
    res = await client.get(
        event_url,
        headers={"User-Agent": "Mozilla/5.0"},
        follow_redirects=True,
    )
    if not res.is_success:
        logger.error("Failed to fetch %s: %s %s", key, event_url, res.status_code)
        return (key, None)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    html_desc = soup.css.select_one(".event-desc")
    return (key, str(html_desc) if html_desc else None)


@monitor("process.main", "pages")
async def main(argv: list[str]) -> None:
    domain = argv[0] if argv else "blueroom.org.au"

    data = await process_domain(domain, datetime.now(tz))
    with open(f"output/{domain}.json", "w") as f:
        f.write(data.model_dump_json(indent=2))


async def process_domain(domain: str, updated_at: datetime) -> Events:
    url = f"https://tix.{domain}/api/v1/Items/Browse"
    retry = Retry(total=5, backoff_factor=0.5)
    transport = RetryTransport(retry=retry)
    client = httpx.AsyncClient(transport=transport)
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
    return Events(
        events=list(boop(domain, shows, descriptions)),
        updated_at=updated_at,
    )


if __name__ == "__main__":
    uvloop.run(main(sys.argv[1:]))
