from datetime import datetime
from enum import Enum

from pydantic import AnyUrl, BaseModel, RootModel


class Status(Enum):
    AVAILABLE = 0
    SELLING_FAST = 4
    SOLD_OUT = 6


class Event(BaseModel):
    class EventDate(BaseModel):
        start: datetime
        end: datetime
        venue: str
        status: Status
        url: AnyUrl

    item_hash: str
    title: str
    url: AnyUrl
    html_desc: str | None
    desc: str
    dates: list[EventDate]


class Events(RootModel[list[Event]]):
    pass
