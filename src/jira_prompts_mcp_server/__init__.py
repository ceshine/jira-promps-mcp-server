import os
import logging
from pathlib import Path
from datetime import datetime

import typer

from .server import APP


def _main(url: str, username: str, api_token: str) -> None:
    os.environ["JIRA_URL"] = url
    os.environ["JIRA_USERNAME"] = username
    os.environ["JIRA_API_TOKEN"] = api_token
    APP.run()


def entry_point():
    logging.basicConfig(
        format="[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    # Export log to a temporary file under /tmp
    tmp_log_file = Path(f"/tmp/jira_prompts_mcp_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
    file_handler = logging.FileHandler(tmp_log_file)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s] %(message)s"))
    logging.getLogger().addHandler(file_handler)
    typer.run(_main)


if __name__ == "__main__":
    entry_point()
