import logging
import os

import sentry_sdk
from rich.console import Console
from rich.logging import RichHandler
from sentry_sdk.crons import monitor

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RichHandler(
            console=Console(
                width=120,
            )
        )
    ],
)

__all__ = ["monitor"]

sentry_sdk.init(
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Enable sending logs to Sentry
    enable_logs=True,
    environment=os.getenv("GITHUB_REF_NAME", "development"),
    release=os.getenv("GITHUB_SHA", "unknown"),
)

client = sentry_sdk.get_current_scope().get_client()
print(
    "Sentry is",
    "enabled" if client.is_active() and client.transport else "disabled",
)
