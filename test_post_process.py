from post_process import process


def test_post_process(snapshot):
    output = process([]).decode()

    assert output == snapshot


def test_post_process_event(snapshot):
    output = process(
        [
            {
                "item_hash": "123",
                "title": "Test Event",
                "url": "https://example.com",
                "desc": "This is a test event",
                "dates": [
                    {
                        "start": "2020-01-01T14:00:00+08:00",
                        "end": "2020-01-01T16:00:00+08:00",
                        "venue": "Backrooms",
                    }
                ],
            }
        ]
    ).decode()

    assert output == snapshot
