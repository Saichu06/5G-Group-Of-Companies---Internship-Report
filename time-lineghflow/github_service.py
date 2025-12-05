import requests
from config import GITHUB_TOKEN, OWNER, REPO

from datetime import datetime, timezone

def hours_between(t1, t2=None):
    """Return hours between two timestamps"""
    if t1 is None:
        return None

    # Convert string → datetime object
    t1 = datetime.fromisoformat(t1.replace("Z", "+00:00"))

    if t2 is None:
        t2 = datetime.now(timezone.utc)

    return round((t2 - t1).total_seconds() / 3600, 2)


BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def fetch_issues():
    """Fetch all issues from the GitHub repo"""
    url = f"{BASE_URL}/issues"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def fetch_issue_events(issue_number):
    """Fetch events (assignment timeline, labels, close/open activity)"""
    url = f"{BASE_URL}/issues/{issue_number}/events"
    response = requests.get(url, headers=HEADERS)
    return response.json()



def parse_issue(issue):
    issue_number = issue["number"]
    events = fetch_issue_events(issue_number)

    created = issue.get("created_at")
    updated = issue.get("updated_at")
    closed = issue.get("closed_at")

    assignees = [a["login"] for a in issue.get("assignees", [])]

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
        "assignment_history": assignment_history,

        # NEW TIMELINE FIELDS
        "time_since_creation_hours": time_since_creation,
        "time_since_update_hours": time_since_update,
        "time_open_hours": time_open_hours,
        "time_since_assignment_hours": time_since_assignment
    }
