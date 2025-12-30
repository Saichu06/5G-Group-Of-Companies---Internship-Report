"""
GitLab Issue Due-Date Service.

Fetches issues, assignees, and due dates from GitLab.
"""

import time
from datetime import datetime
import requests
from requests.exceptions import RequestException

import config


BASE_URL = f"{config.GITLAB_URL}/api/v4"
HEADERS = {"PRIVATE-TOKEN": config.GITLAB_TOKEN}


def safe_get(url, params=None):
    """HTTP GET with retry."""
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=config.TIMEOUT
            )
            response.raise_for_status()
            return response
        except RequestException:
            if attempt == config.MAX_RETRIES:
                raise
            time.sleep(config.RETRY_DELAY * attempt)
    raise RuntimeError("safe_get failed")


def fetch_issues(project_id):
    """Fetch all issues for a project (with pagination)."""
    issues = []
    page = 1

    while True:
        params = {"per_page": 100, "page": page}
        response = safe_get(
            f"{BASE_URL}/projects/{project_id}/issues",
            params
        )
        data = response.json()

        if not data:
            break

        issues.extend(data)
        page += 1

    return issues


def build_due_date_rows():
    """
    Build normalized rows:
    user, issue_id, weekday columns
    """
    rows = []

    for project_id in config.PROJECT_IDS:
        issues = fetch_issues(project_id)

        for issue in issues:
            due_date = issue.get("due_date")
            assignees = issue.get("assignees", [])

            weekday_map = {
                "Monday": "",
                "Tuesday": "",
                "Wednesday": "",
                "Thursday": "",
                "Friday": ""
            }

            if due_date:
                date_obj = datetime.strptime(due_date, "%Y-%m-%d")
                weekday = date_obj.strftime("%A")
                if weekday in weekday_map:
                    weekday_map[weekday] = due_date

            # Ensure ALL assignees are included
            if assignees:
                for assignee in assignees:
                    rows.append({
                        "user": assignee["username"],
                        "issue_id": issue["iid"],
                        **weekday_map
                    })
            else:
                # Issue with no assignees
                rows.append({
                    "user":"Not Assigned",
                    "issue_id":issue["iid"],
                    **weekday_map
                })

    return rows
