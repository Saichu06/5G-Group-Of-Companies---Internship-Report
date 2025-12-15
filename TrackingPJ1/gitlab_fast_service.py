# pylint: disable=no-name-in-module

from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import requests
import urllib3

from config import GITLAB_TOKEN, PROJECT_ID



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GITLAB_URL = "https://git.fifthgentech.com"
BASE_URL = f"{GITLAB_URL}/api/v4"

HEADERS = {"Private-Token": GITLAB_TOKEN}
TIMEOUT = 20
MAX_WORKERS = 8


def get_recent_issues(days=7):
    updated_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues"

    all_issues = []
    page = 1

    while True:
        params = {
            "per_page": 100,
            "page": page,
            "updated_after": updated_after
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            verify=False,
            timeout=TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

        if not data:
            break

        all_issues.extend(data)
        page += 1

    return all_issues


def get_spend_events(issue_iid):
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues/{issue_iid}/notes"

    response = requests.get(
        url,
        headers=HEADERS,
        verify=False,
        timeout=TIMEOUT
    )

    response.raise_for_status()
    notes = response.json()

    events = []
    for note in notes:
        if note.get("system") and "time spent" in note["body"].lower():
            events.append({
                "issue_iid": issue_iid,
                "user": note["author"]["username"],
                "message": note["body"],
                "created_at": note["created_at"]
            })

    return events


def collect_time_logs(issues):
    all_logs = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(
            lambda issue: get_spend_events(issue["iid"]),
            issues
        )

    for logs in results:
        all_logs.extend(logs)

    return all_logs



def generate_time_log_report(days=7):
    issues = get_recent_issues(days)
    print(f"Recent issues fetched: {len(issues)}")

    logs = collect_time_logs(issues)
    print(f"Total time log entries: {len(logs)}")
    return logs
