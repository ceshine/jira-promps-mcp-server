from typing import Iterable, Any

from jira.resources import Issue

from .client import JiraClient


class IssuesMixin(JiraClient):
    def get_issue_fields(
        self,
        issue_key: str,
        fields: str | Iterable[str] = (
            "summary",
            "description",
            "status",
            "assignee",
            "reporter",
            "labels",
            "priority",
            "created",
            "updated",
            "issuetype",
        ),
    ) -> tuple[dict[str, Any], Issue]:
        issue = self.jira.issue(issue_key)
        if isinstance(fields, str):
            fields = fields.split(",")
        results = {field: getattr(issue.fields, field) for field in fields}
        # Special rule for "description" as it requires a conversion from the Jira markup format to the markdown format
        if "description" in results:
            results["description"] = self.preprocessor.clean_jira_text(results["description"])
        return results, issue
