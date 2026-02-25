import zoneinfo
from enum import Enum
from typing import Any

from pydantic import AnyUrl, AwareDatetime, BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema


class Status(Enum):
    AVAILABLE = 0
    SELLING_FAST = 4
    SOLD_OUT = 6


class Event(BaseModel):
    class EventDate(BaseModel):
        start: AwareDatetime
        end: AwareDatetime
        venue: str
        status: Status
        url: AnyUrl

    item_hash: str
    title: str
    url: AnyUrl
    html_desc: str | None
    desc: str
    dates: list[EventDate]


class Timezone:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if cls is source:
            # used directly as a type
            schema = core_schema.str_schema()
        else:
            schema = handler(source)
        schema["enum"] = list(zoneinfo.available_timezones())
        return schema


class Events(BaseModel):
    timezone: Timezone
    updated_at: AwareDatetime
    events: list[Event]
