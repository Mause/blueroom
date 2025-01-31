from datetime import datetime

from post_process import process, tz

dt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz)


def test_post_process(snapshot):
    output = process([], dt).decode()

    assert output == snapshot


def test_post_process_event(snapshot):
    output = process(
        [
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
                    }
                ],
            }
        ],
        dt,
    ).decode()

    assert output == snapshot
