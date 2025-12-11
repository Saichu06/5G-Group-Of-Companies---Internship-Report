import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import GITLAB_TOKEN, PROJECT_ID

GITLAB_URL = "https://git.fifthgentech.com"
BASE_URL = f"{GITLAB_URL}/api/v4"


def get_issues():
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues"
    headers = {"Private-Token": GITLAB_TOKEN}

    all_issues = []
    page = 1

    while True:
        params = {
            "per_page": 100,
            "page": page,
            "order_by": "created_at",
            "sort": "asc"
        }

        print(f"Fetching page {page}...")
        response = requests.get(url, headers=headers, params=params, verify=False)
        data = response.json()

        if not data:
            break

        all_issues.extend(data)
        page += 1

    print(f"Total issues fetched: {len(all_issues)}")
    return all_issues


def get_spend_events(issue_iid):
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues/{issue_iid}/notes"
    headers = {"Private-Token": GITLAB_TOKEN}

    response = requests.get(url, headers=headers, verify=False)
    notes = response.json()

    events = []
    for note in notes:
        if note.get("system") and "time spent" in note["body"].lower():
            events.append({
                "user": note["author"]["username"],
                "body": note["body"],
                "created_at": note["created_at"]
            })

    return events


def parse_issue(issue):
    time_stats = issue.get("time_stats", {})

    return {
        "iid": issue["iid"],
        "title": issue["title"],
        "state": issue["state"],
        "assignee": issue["assignee"][
            "username"] if issue.get("assignee") else None,
        "estimate_seconds": time_stats.get("time_estimate", 0),
        "spent_seconds": time_stats.get("total_time_spent", 0),
        "estimate_hours": round(time_stats.get("time_estimate", 0) / 3600, 2),
        "spent_hours": round(time_stats.get("total_time_spent", 0) / 3600, 2),
        "spend_events": get_spend_events(issue["iid"])
    }


def get_time_report():
    issues = get_issues()
    parsed = []

    for i, issue in enumerate(issues):
        print(f"Processing issue {issue['iid']} ({i+1}/{len(issues)})")
        parsed.append(parse_issue(issue))

    return parsed


if __name__ == "__main__":
    report = get_time_report()
    print(report)
