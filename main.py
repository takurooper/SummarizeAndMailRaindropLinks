from __future__ import annotations

import logging
import sys

from summarizeandmailraindroplinks import config
from summarizeandmailraindroplinks.orchestrator import run


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    try:
        settings = config.Settings.from_env()
    except ValueError as exc:
        logging.error("Missing configuration: %s", exc)
        sys.exit(1)

    try:
        run(settings)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Batch run failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
