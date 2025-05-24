# Jira Prompts MCP Server

This repository provides a Model Context Protocol (MCP) server that offers several commands for generating prompts or contexts from Jira content.

This repository draws significant inspiration from the [MarkItDown MCP server](https://github.com/KorigamiK/markitdown_mcp_server) and the example [Git MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/git). It also incorporates design and code elements from the [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) repository. The main differences between this repository and `mcp-atlassian` are that it uses [pycontribs/jira](https://github.com/pycontribs/jira) instead of [atlassian-api/atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) to interact with the Jira API, and it focuses on providing prompts rather than tools. The latter makes it especially useful when working with tools that support only MCP prompts, such as Zed's AI assistant.

Here's another MCP server project of mine: [ceshine/git-prompts-mcp-server](https://github.com/ceshine/git-prompts-mcp-server)

## Changelog

### 0.1.0

* Migrate from the low-level [mcp package](https://github.com/modelcontextprotocol/python-sdk) to the [FastMCP](https://github.com/jlowin/fastmcp?tab=readme-ov-file) package.
* Add a CLI for testing the server.

### 0.0.1

The initial release with two prompts implemented: `jira-issue-brief` and `jira-issue-full`.

## Installation

### Manual Installation

1. Clone this repository
2. Install dependencies: `uv sync --frozen`


## Usage

### As a MCP Server for Zed Editor

Add the following to your `settings.json`:

```json
"context_servers": {
  "git_prompt_mcp": {
    "command": {
      "path": "uv",
      "args": [
        "--directory",
        "/path/to/local/jira_prompts_mcp_server",
        "run",
        "jira-prompts-mcp-server",
        "https://my-company.atlassian.net", // Jira base URL
        "your_jira_account@example.com",  // Jira username
        "your_api_key"  // Jira API token (https://id.atlassian.com/manage-profile/security/api-tokens)
      ]
    },
    "settings": {}
  }
}
```

#### Commands

The server responds to the following commands:

1. `jira-issue-brief <issue-key>`: Retrieves the core fields of a Jira issue. Requires the issue key (e.g., `PROJ-123`) as an argument.
2. `jira-issue-full <issue-key>`: Retrieves the core fields, comments, linked issues, and subtasks of a Jira issue. Requires the issue key as an argument.

Examples:

1. `/jira-issue-brief PROJ-123`
2. `/jira-issue-brief PROJ-155`

### Testing the server using the CLI

Prerequisities: configuring the required environment variables (`JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`)

You can quickly test the MCP server using the CLI. Below are some example commands:

* `uv run python -m jira_prompts_mcp_server.cli jira-brief BOOM-1234`
* `uv run python -m jira_prompts_mcp_server.cli jira-full BOOM-1234`

## License

MIT License. See [LICENSE](LICENSE) for details.
