import os
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import mcp.types as types
from mcp.server import Server, models, NotificationOptions
from mcp.server.stdio import stdio_server

from .jira_utils import JiraFetcher
from .version import __version__

LOGGER = logging.getLogger("jira_prompts")

PROMPTS = {
    "jira-issue-brief": types.Prompt(
        name="jira-issue-brief",
        description="Get the core information about a Jira issue",
        arguments=[
            # Note: Zed only supports one prompt argument
            # Reference: https://github.com/zed-industries/zed/issues/21944
            types.PromptArgument(
                name="issue-key",
                description="The key/ID of the issue",
                required=True,
            ),
        ],
    ),
    "jira-issue-full": types.Prompt(
        name="jira-issue-full",
        description="Get core fields, comments, and linked issues for a Jira issue",
        arguments=[
            # Note: Zed only supports one prompt argument
            # Reference: https://github.com/zed-industries/zed/issues/21944
            types.PromptArgument(
                name="issue-key",
                description="The key/ID of the issue",
                required=True,
            ),
        ],
    ),
}


class StrFallbackEncoder(json.JSONEncoder):
    """A custom JSON encoder to get around restrictions on unserializable objects

    A custom JSON encoder that falls back to an object's __str__ representation
    if the object is not directly serializable by the default JSON encoder.
    """

    def default(self, o):
        """
        Overrides the default method of JSONEncoder.

        If the object `obj` is not serializable by the standard encoder,
        this method is called. It returns the string representation (obj.__str__())
        of the object.

        Args:
            obj: The object to encode.

        Returns:
            A serializable representation of obj (its string form in this case).

        Raises:
            TypeError: If the default encoder itself encounters an issue after
                       this method returns (though unlikely if str() succeeds).
                       It primarily handles cases where the standard encoder fails.
        """
        try:
            # Let the base class default method try first (handles dates, etc.)
            # Although often the check happens *before* calling default,
            # this is more robust if the base class had more complex logic.
            # However, for this specific requirement (call str() on failure),
            # we can directly attempt the fallback.
            #
            # If json.JSONEncoder already raises TypeError for obj,
            # this 'default' method will be called.
            return str(o)
        except TypeError:
            # If str(obj) itself fails (less common), let the base class
            # raise the final TypeError.
            # This line is technically only reached if str(obj) itself fails,
            # which is rare. The primary path is just `return str(obj)`.
            return json.JSONEncoder.default(self, o)


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[JiraFetcher]:
    """Initialize and clean up application resources."""
    jira_url = os.getenv("JIRA_URL")
    if jira_url is None:
        raise ValueError("JIRA_URL environment variable is not set")

    try:
        jira = JiraFetcher()

        # Log the startup information
        LOGGER.info("Starting Jira Prompts MCP server")
        os.system("notify-send 'Jira Prompts MCP server is starting'")

        jira_url = jira.config.url
        LOGGER.info(f"Jira URL: {jira_url}")

        # Provide context to the application
        yield jira
    finally:
        # Cleanup resources if needed
        pass


APP = Server("jira-prompts-mcp", lifespan=server_lifespan)


@APP.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return list(PROMPTS.values())


def _postprocessing_for_issue_fields_(field_to_value):
    for name_field in ("status", "priority", "issuetype"):
        field_to_value[name_field] = field_to_value[name_field].name
    for user_field in ("assignee", "reporter"):
        field_to_value[user_field] = field_to_value[user_field].displayName
    field_to_value["parent"] = {
        "key": field_to_value["parent"].key,
        "summary": field_to_value["parent"].fields.summary,
        "status": field_to_value["parent"].fields.status.name,
    }


def get_issue_and_core_fields(jira_fetcher: JiraFetcher, arguments: dict[str, str] | None):
    if not arguments:
        raise ValueError("Argument `issue-keu` is required")
    issue_key = arguments.get("issue-key", "")
    assert issue_key
    field_to_value, issue = jira_fetcher.get_issue_and_core_fields(issue_key)
    field_to_value["issue_key"] = issue_key
    _postprocessing_for_issue_fields_(field_to_value)
    return field_to_value, issue


@APP.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")
    jira_fetcher = APP.request_context.lifespan_context
    if name.startswith("jira-issue"):
        field_to_value, issue = get_issue_and_core_fields(jira_fetcher, arguments)
        if name == "jira-issue-full":
            field_to_value["links"] = jira_fetcher.collect_links(issue)
            field_to_value["subtasks"] = jira_fetcher.collect_subtasks(issue)
            field_to_value["comments"] = jira_fetcher.collect_comments(issue)
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=json.dumps(field_to_value, cls=StrFallbackEncoder, indent=4),
                    ),
                )
            ]
        )
    else:
        raise RuntimeError("Should not reach this line.")


async def run_server() -> None:
    """Run the MCP server with the specified transport."""

    async with stdio_server() as (read_stream, write_stream):
        await APP.run(
            read_stream,
            write_stream,
            models.InitializationOptions(
                server_name="jira_prompts_mcp_server",
                server_version=__version__,
                capabilities=APP.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
