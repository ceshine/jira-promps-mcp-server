# Jira Prompts MCP Server

This repository provides a Model Context Protocol (MCP) server that offers several commands for generating prompts or contexts from Jira content.

This repository draws heavy inspiration from [MarkItDown MCP server](https://github.com/KorigamiK/markitdown_mcp_server) and the example [Git MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/git). It also adopts some of the design and code from the [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) repository. The main differences between this repository and `mcp-atlassian` is that it uses [pycontribs/jira](https://github.com/pycontribs/jira) instead of [atlassian-api/atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) to interact with Jira API, and that it focuses on providing prompts instead of tools, which makes it useful when working with tools that only supports MCP prompts such as Zed's AI assistant.

This repository draws significant inspiration from the [MarkItDown MCP server](https://github.com/KorigamiK/markitdown_mcp_server) and the example [Git MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/git). It also incorporates design and code elements from the [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) repository. The main differences between this repository and `mcp-atlassian` are that it uses [pycontribs/jira](https://github.com/pycontribs/jira) instead of [atlassian-api/atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) to interact with the Jira API, and it focuses on providing prompts rather than tools. The latter makes it especially useful when working with tools that support only MCP prompts, such as Zed's AI assistant.

Here's another MCP server project of mine: [ceshine/git-prompts-mcp-server](https://github.com/ceshine/git-prompts-mcp-server)

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

1. `jira-issue-brief <issue-key>`: Get the core information about a Jira issue. Requires the issue key (e.g., `PROJ-123`) as an argument.


Examples:

1. `/jira-issue-brief PROJ-123`


## License

MIT License. See [LICENSE](LICENSE) for details.
