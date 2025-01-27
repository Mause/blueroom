import json
import zoneinfo
from urllib.parse import parse_qsl, urlencode, urlparse

import scrapy
from dateutil.parser import parse as dateparse
from scrapy.http import HtmlResponse

PERTH = zoneinfo.ZoneInfo("Australia/Perth")


def process_date(el):
    date = "".join(el.css(".ft_ed_dateTime *::text").extract())

    from_, to = date.split(" to ")

    from_ = dateparse(from_, tzinfos={None: PERTH})
    to = dateparse(to, default=from_)

    return {
        "start": from_.isoformat(),
        "end": to.isoformat(),
        "venue": el.css(".ft_ed_venue *::text").extract_first(),
    }


class BlueroomSpider(scrapy.Spider):
    name = "blueroom"
    allowed_domains = ["blueroom.org.au"]
    start_urls = ["https://blueroom.org.au/events"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": 543,
        },
    }

    def parse(self, response):
        """
        <a href="https://blueroom.org.au/events/amplified-souls/" title="More Info" aria-label="More Info" class="btn">
                Info
            </a>
        """

        for event in response.css("a.btn"):
            if event.xpath("@title").extract_first() == "More Info":
                yield response.follow(
                    event.xpath("@href").extract_first(), callback=self.parse_event
                )

    def parse_event(self, response):
        data = json.loads(
            response.xpath(
                '//script[@type="application/ld+json"]//text()'
            ).extract_first()
        )

        item = data["@graph"][0]["itemListElement"][-1]["item"]
        title = item["name"]

        script_el = response.css("#ft_ftapiJS")
        if not script_el:
            return
        src = script_el.attrib["src"]

        item_hash = dict(parse_qsl(urlparse(src).query))["itemHash"]

        desc = "\n".join(
            s.strip() for s in response.css(".event-desc *::text").extract()
        )

        yield response.follow(
            "https://tix.blueroom.org.au/api/v1/Items/DatesCached?"
            + urlencode({"itemHash": item_hash, "app": "false"}),
            callback=self.parse_dates,
            meta={
                "title": title,
                "item_hash": item_hash,
                "url": response.url,
                "desc": desc,
                "html_desc": str(response.css(".event-desc").get()),
            },
        )

    def parse_dates(self, response):
        messages = response.json().get("SuccessMessages", [])
        if not messages:
            return

        response = HtmlResponse(
            body=messages[0].encode(),
            url=response.url,
            request=response.request,
        )

        dates = response.css(".ft_ed_timeRow")

        meta = response.meta
        yield {
            "title": meta["title"],
            "item_hash": meta["item_hash"],
            "url": meta["url"],
            "desc": meta["desc"],
            "html_desc": meta["html_desc"],
            "dates": [process_date(d) for d in dates],
        }
