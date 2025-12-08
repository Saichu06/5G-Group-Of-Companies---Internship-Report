import requests
from datetime import datetime, timezone
from config import GITHUB_TOKEN, OWNER, REPO


def hours_between(t1, t2=None):
    """Return hours between two timestamps"""
    if t1 is None:
        return None

    # Convert string → datetime
    t1 = datetime.fromisoformat(t1.replace("Z", "+00:00"))

    if t2:
        t2 = datetime.fromisoformat(t2.replace("Z", "+00:00"))
    else:
        t2 = datetime.now(timezone.utc)

    return round((t2 - t1).total_seconds() / 3600, 2)


def fetch_issues(owner=None, repo=None):
    """Fetch ALL issues including closed ones from any repo"""
    owner = owner or OWNER
    repo = repo or REPO

    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    response = requests.get(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    })

    return response.json()


def fetch_issue_events(issue_number, owner=None, repo=None):
    """Fetch assignment and activity events"""
    owner = owner or OWNER
    repo = repo or REPO

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/events"
    response = requests.get(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    })

    return response.json()


def parse_issue(issue, owner=None, repo=None):
    issue_number = issue["number"]
    events = fetch_issue_events(issue_number, owner, repo)

    created = issue.get("created_at")
    updated = issue.get("updated_at")
    closed = issue.get("closed_at")

    assignees = [a["login"] for a in issue.get("assignees", [])]
    labels = [label["name"] for label in issue.get("labels", [])]

    assignment_history = []
    last_assignment_time = None

    for event in events:
        if event["event"] == "assigned":
            assigned_at = event["created_at"]
            assignment_history.append({
                "user": event["assignee"]["login"],
                "assigned_at": assigned_at
            })
            last_assignment_time = assigned_at

    # Timeline calculations
    time_since_creation = hours_between(created)
    time_since_update = hours_between(updated)
    time_open_hours = hours_between(created, closed) if closed else hours_between(created)
    time_since_assignment = hours_between(last_assignment_time) if last_assignment_time else None

    return {
        "number": issue_number,
        "title": issue["title"],
        "created_at": created,
        "updated_at": updated,
        "closed_at": closed,
        "assignees": assignees,
        "labels": labels,
        "assignment_history": assignment_history,

        "time_since_creation_hours": time_since_creation,
        "time_since_update_hours": time_since_update,
        "time_open_hours": time_open_hours,
        "time_since_assignment_hours": time_since_assignment
    }
