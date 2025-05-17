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


@TYPER_APP.command()
def jira_epic(issue_key_list: list[str]):
    async def _internal_func():
        async with client:
            result = await client.call_tool("epics_of_jira_issues", arguments={"issue_key_list": issue_key_list})
            print(result)

    asyncio.run(_internal_func())


if __name__ == "__main__":
    TYPER_APP()
