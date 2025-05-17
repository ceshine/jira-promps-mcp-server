import asyncio

import typer
from fastmcp import Client

from .server import APP as MCP_APP

client = Client(MCP_APP)

TYPER_APP = typer.Typer()


@TYPER_APP.command()
def jira_full(issue_key: str):
    async def _internal_func():
        async with client:
            result = await client.get_prompt("jira-issue-full", arguments={"issue_key": issue_key})
            print(result.messages[0].content.text)  # type: ignore

    asyncio.run(_internal_func())


@TYPER_APP.command()
def jira_brief(issue_key: str):
    async def _internal_func():
        async with client:
            result = await client.get_prompt("jira-issue-brief", arguments={"issue_key": issue_key})
            print(result.messages[0].content.text)  # type: ignore

    asyncio.run(_internal_func())


if __name__ == "__main__":
    TYPER_APP()
