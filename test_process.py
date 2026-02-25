from datetime import datetime, timezone

import uvloop
from httpx import Response
from respx import MockRouter
from syrupy.assertion import SnapshotAssertion

from process import process_domain


def test_main(respx_mock: MockRouter, snapshot: SnapshotAssertion) -> None:
    respx_mock.get("https://blueroom.org.au/event/1").mock(
        Response(
            status_code=200,
            json={
                "Id": 1,
                "Name": "Test Event",
                "Date": "2023-10-01",
                "Location": "Test Location",
                "Description": "This is a test event.",
            },
        )
    )
    respx_mock.get("https://tix.blueroom.org.au/api/v1/Items/Browse").mock(
        Response(
            status_code=200,
            json={
                "Items": [
                    {
                        "Id": 1,
                        "Name": "Test Item 1",
                        "Price": 10.0,
                        "Hash": "abc123",
                        "DescriptionBrief": "A brief description of Test Item 1.",
                        "URL": "/Event/1/2023-10-01",
                        "Status": 0,
                        "VenueName": "Test Venue",
                        "Runtime": 120,
                        "DateTime": "2023-10-01T00:00:00",
                    }
                ]
            },
        )
    )

    data = uvloop.run(
        process_domain(
            "blueroom.org.au", datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
    )

    snapshot.assert_match(
        data.model_dump_json(indent=2),
    )
