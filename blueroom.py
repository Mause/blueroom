from urllib.parse import parse_qsl, urlencode, urlparse

import scrapy
from dateutil.parser import parse as dateparse
from scrapy.http import HtmlResponse


def process_date(date: str):
    from_, to = date.split(" to ")

    from_ = dateparse(from_)

    to = dateparse(to, default=from_)

    return from_, to


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
        title = response.css("title::text").extract_first()

        script_el = response.css("#ft_ftapiJS")
        if not script_el:
            return
        src = script_el.attrib["src"]

        item_hash = dict(parse_qsl(urlparse(src).query))["itemHash"]

        yield response.follow(
            "https://tix.blueroom.org.au/api/v1/Items/DatesCached?"
            + urlencode({"itemHash": item_hash, "app": "false"}),
            callback=self.parse_dates,
            meta={"title": title, "item_hash": item_hash},
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

        dates = {
            "".join(date.css("::text").extract())
            for date in response.css(".ft_ed_dateTime")
        }
        if "Date" in dates:
            dates.remove("Date")

        yield {
            "title": response.meta["title"],
            "item_hash": response.meta["item_hash"],
            "dates": [process_date(d) for d in dates],
        }
