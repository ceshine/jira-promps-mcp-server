from typing import Iterable, Any

from jira.resources import Issue

from .client import JiraClient


class IssuesMixin(JiraClient):
    def collect_comments(
        self,
        issue: Issue,
        limit: int = -1,  # Set limit to -1 to collect all comments
    ) -> list[dict[str, Any]]:
        comments = sorted(issue.fields.comment.comments, key=lambda x: x.created, reverse=True)
        if limit > 0:
            comments = comments[:limit]
        return [
            {
                "id": entry.id,
                "author": entry.author,
                "created": entry.created,
                "updated": entry.updated,
                "body": self.preprocessor.clean_jira_text(entry.body),
            }
            for entry in comments
        ]

    @staticmethod
    def collect_links_and_subtasks(issue: Issue):
        links = issue.fields.issuelinks
        results = []
        for entry in links:
            try:
                results.append(
                    {
                        "relationship": entry.type.inward,
                        "key": entry.inwardIssue.key,
                        "summary": entry.inwardIssue.fields.summary,
                        "status": entry.inwardIssue.fields.status.name,
                        "type": entry.inwardIssue.fields.issuetype.name,
                    }
                )
            except AttributeError:
                results.append(
                    {
                        "relationship": entry.type.outward,
                        "key": entry.outwardIssue.key,
                        "summary": entry.outwardIssue.fields.summary,
                        "status": entry.outwardIssue.fields.status.name,
                        "type": entry.outwardIssue.fields.issuetype.name,
                    }
                )
        subtasks = issue.fields.subtasks
        for entry in subtasks:
            results.append(
                {
                    "relationship": "subtask",
                    "key": entry.key,
                    "summary": entry.fields.summary,
                    "status": entry.fields.status.name,
                    "type": entry.fields.issuetype.name,
                }
            )
        return results

    def get_issue_and_core_fields(
        self,
        issue_key: str,
        fields: str | Iterable[str] = (
            "summary",
            "description",
            "status",
            "assignee",
            "parent",
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
