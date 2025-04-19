"""Base client module for Jira API interactions."""

import logging

from jira import JIRA

from .config import JiraConfig
from .preprocessing import JiraPreprocessor

# Configure logging
LOGGER = logging.getLogger("jira_prompts.client")


class JiraClient:
    """Base client for Jira API interactions."""

    def __init__(self, config: JiraConfig | None = None) -> None:
        """Initialize the Jira client with configuration options.

        Args:
            config: Optional configuration object (will use env vars if not provided)

        Raises:
            ValueError: If configuration is invalid or required credentials are missing
        """
        # Load configuration from environment variables if not provided
        self.config = config or JiraConfig.from_env()

        # Initialize the Jira client based on auth type
        if self.config.auth_type == "token":
            raise NotImplementedError("Token authentication is not supported yet")
        else:  # basic auth
            assert self.config.username and self.config.api_token, "Username and API token are required for basic auth"
            self.jira = JIRA(
                self.config.url,
                basic_auth=(self.config.username, self.config.api_token),
            )

        self.preprocessor = JiraPreprocessor(base_url=self.config.url)

        # Cache for frequently used data
        self._field_ids: dict[str, str] | None = None
        self._current_user_account_id: str | None = None
