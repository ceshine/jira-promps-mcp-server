"""Configuration module for Jira API interactions."""

import os
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Literal


def is_atlassian_cloud_url(url: str) -> bool:
    """Determine if a URL belongs to Atlassian Cloud or Server/Data Center.

    Args:
        url: The URL to check

    Returns:
        True if the URL is for an Atlassian Cloud instance, False for Server/Data Center
    """
    # Localhost and IP-based URLs are always Server/Data Center
    if url is None or not url:
        return False

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""

    # Check for localhost or IP address
    if (
        hostname == "localhost"
        or re.match(r"^127\.", hostname)
        or re.match(r"^192\.168\.", hostname)
        or re.match(r"^10\.", hostname)
        or re.match(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", hostname)
    ):
        return False

    # The standard check for Atlassian cloud domains
    return ".atlassian.net" in hostname or ".jira.com" in hostname or ".jira-dev.com" in hostname


@dataclass
class JiraConfig:
    """Jira API configuration.

    Handles authentication for both Jira Cloud (using username/API token)
    and Jira Server/Data Center (using personal access token).
    """

    url: str  # Base URL for Jira
    auth_type: Literal["basic", "token"]  # Authentication type
    username: str | None = None  # Email or username (Cloud)
    api_token: str | None = None  # API token (Cloud)
    personal_token: str | None = None  # Personal access token (Server/DC)
    projects_filter: str | None = None  # List of project keys to filter searches

    @property
    def is_cloud(self) -> bool:
        """Check if this is a cloud instance.

        Returns:
            True if this is a cloud instance (atlassian.net), False otherwise.
            Localhost URLs are always considered non-cloud (Server/Data Center).
        """
        return is_atlassian_cloud_url(self.url)

    @classmethod
    def from_env(cls) -> "JiraConfig":
        """Create configuration from environment variables.

        Returns:
            JiraConfig with values from environment variables

        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        url = os.getenv("JIRA_URL")
        if not url:
            error_msg = "Missing required JIRA_URL environment variable"
            raise ValueError(error_msg)

        # Determine authentication type based on available environment variables
        username = os.getenv("JIRA_USERNAME")
        api_token = os.getenv("JIRA_API_TOKEN")
        personal_token = os.getenv("JIRA_PERSONAL_TOKEN")

        # Use the shared utility function directly
        is_cloud = is_atlassian_cloud_url(url)

        if is_cloud:
            if username and api_token:
                auth_type = "basic"
            else:
                error_msg = "Cloud authentication requires JIRA_USERNAME and JIRA_API_TOKEN"
                raise ValueError(error_msg)
        else:  # Server/Data Center
            if personal_token:
                auth_type = "token"
            elif username and api_token:
                # Allow basic auth for Server/DC too
                auth_type = "basic"
            else:
                error_msg = "Server/Data Center authentication requires JIRA_PERSONAL_TOKEN"
                raise ValueError(error_msg)

        # Get the projects filter if provided
        projects_filter = os.getenv("JIRA_PROJECTS_FILTER")

        return cls(
            url=url,
            auth_type=auth_type,
            username=username,
            api_token=api_token,
            personal_token=personal_token,
            projects_filter=projects_filter,
        )
