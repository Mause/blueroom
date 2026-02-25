from datetime import datetime
from pathlib import Path

from syrupy.assertion import SnapshotAssertion

from models import Events
from post_process import process, PERTH

dt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=PERTH)


def test_post_process(snapshot: SnapshotAssertion) -> None:
    output = process([], dt, output_filename=Path("output/dates.ics")).decode()

    assert output == snapshot


def test_post_process_event(snapshot: SnapshotAssertion) -> None:
    output = process(
        Events.model_validate(
            {
                "timezone": "Australia/Perth",
                "events": [
                    {
                        "item_hash": "123",
                        "title": "Test Event",
                        "url": "https://example.com",
                        "desc": "This is a test event",
                        "html_desc": "<p>This is a test event</p>",
                        "dates": [
                            {
                                "start": "2020-01-01T14:00:00+08:00",
                                "end": "2020-01-01T16:00:00+08:00",
                                "venue": "Backrooms",
                                "status": 0,
                                "url": "https://tix/",
                            }
                        ],
                    }
                ],
                "updated_at": dt,
            }
        ).events,
        dt,
        output_filename=Path("output/dates.ics"),
    ).decode()

    assert output == snapshot


def test_unusual_dates(snapshot: SnapshotAssertion) -> None:
    output = process(
        Events.model_validate(
            {
                "timezone": "Australia/Perth",
                "events": [
                    {
                        "item_hash": "ab14eaecc5144650a99de68d3f64bbca",
                        "title": "Love Stories",
                        "url": "https://blueroom.org.au/events/love-stories/",
                        "html_desc": "",
                        "desc": "Thousands",
                        "dates": [
                            {
                                "start": "2025-07-04T18:30:00+08:00",
                                "end": "2025-07-04T19:20:00+08:00",
                                "venue": "Kaos Room",
                                "status": 6,
                                "url": "https://tix.blueroom.org.au/Events/Love-Stories/Fri-Jul-4-2025-18-30",
                            },
                            {
                                "start": "2025-07-05T14:00:00+08:00",
                                "end": "2025-07-05T14:50:00+08:00",
                                "venue": "Kaos Room",
                                "status": 4,
                                "url": "https://tix.blueroom.org.au/Events/Love-Stories/Sat-Jul-5-2025-14-00",
                            },
                        ],
                    },
                ],
                "updated_at": dt,
            }
        ).events,
        dt,
        output_filename=Path("output/unusual_dates.ics"),
    ).decode()

    assert output == snapshot
