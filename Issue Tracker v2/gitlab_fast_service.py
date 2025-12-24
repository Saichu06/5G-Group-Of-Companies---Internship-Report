"""
GitLab Event Time Log Service.

Extracts numeric time spent events from Issues and Merge Requests
across multiple GitLab projects.
"""
# pylint: disable=no-name-in-module
import re
import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

import requests
import urllib3
from requests.exceptions import RequestException

import config

# pylint: disable=no-name-in-module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IST = timezone(timedelta(hours=5, minutes=30))
BASE_URL = f"{config.GITLAB_URL}/api/v4"
HEADERS = {"Private-Token": config.GITLAB_TOKEN}


# ---------- HTTP ----------
def safe_get(url, params=None):
    """
    Perform GET request with retry logic.
    """
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                verify=False,
                timeout=config.TIMEOUT
            )
            response.raise_for_status()
            return response
        except RequestException:
            if attempt == config.MAX_RETRIES:
                raise
            time.sleep(config.RETRY_DELAY * attempt)

    raise RuntimeError("safe_get failed unexpectedly")


# ---------- TIME PARSER ----------
def parse_time_spent(note_body):
    """
    Convert GitLab system note text into minutes.

    Examples:
    - 'added 1h 30m of time spent' -> 90
    - 'subtracted 15m of time spent' -> -15
    """
    sign = -1 if "subtracted" in note_body.lower() else 1

    hours_match = re.search(r"(\d+)h", note_body)
    minutes_match = re.search(r"(\d+)m", note_body)

    total_minutes = 0
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    if minutes_match:
        total_minutes += int(minutes_match.group(1))

    return sign * total_minutes


# ---------- FETCH ISSUES / MRS ----------
def fetch_items(project_id, item_type, days):
    """
    Fetch issues or merge requests updated within lookback window.
    """
    updated_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    url = f"{BASE_URL}/projects/{project_id}/{item_type}"

    items = []
    page = 1

    while True:
        params = {
            "per_page": 100,
            "page": page,
            "updated_after": updated_after
        }
        response = safe_get(url, params)
        data = response.json()

        if not data:
            break

        items.extend(data)
        page += 1

    return items


# ---------- FETCH & PARSE NOTES (WITH PAGINATION) ----------
def extract_time_events(project_id, event_type, iid):
    """
    Extract numeric time spent events from issue / merge request notes.
    """
    url = f"{BASE_URL}/projects/{project_id}/{event_type}s/{iid}/notes"

    notes = []
    page = 1

    while True:
        response = safe_get(url, {"per_page": 100, "page": page})
        data = response.json()

        if not data:
            break

        notes.extend(data)
        page += 1

    events = []
    for note in notes:
        if note.get("system") and "time spent" in note["body"].lower():
            minutes = parse_time_spent(note["body"])

            utc_time = datetime.fromisoformat(
                note["created_at"].replace("Z", "+00:00")
            )

            events.append({
                "project_id": project_id,
                "event_type": event_type,
                "event_id": iid,
                "user": note["author"]["username"],
                "time_spent_minutes": minutes,
                "created_at_ist": utc_time.astimezone(IST)
                    .strftime("%Y-%m-%d %H:%M:%S")
            })

    return events


def generate_time_log_report(days):
    """
    Generate normalized time-spent events across all configured projects.

    Returns:
        list: List of time-spent event dictionaries
    """
    all_events = []

    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        futures = []

        for project_id in config.PROJECT_IDS:
            # -------- ISSUES --------
            issues = fetch_items(project_id, "issues", days)
            print(f"[DEBUG] Project {project_id} → issues fetched: {len(issues)}")

            for issue in issues:
                futures.append(
                    executor.submit(
                        extract_time_events,
                        project_id,
                        "issue",
                        issue["iid"]
                    )
                )

            # -------- MERGE REQUESTS --------
            mrs = fetch_items(project_id, "merge_requests", days)
            print(f"[DEBUG] Project {project_id} → MRs fetched: {len(mrs)}")

            for mr in mrs:
                futures.append(
                    executor.submit(
                        extract_time_events,
                        project_id,
                        "merge_request",
                        mr["iid"]
                    )
                )

        # Collect results
        for future in futures:
            result = future.result()
            if result:  # avoid extending with empty lists
                all_events.extend(result)

    # ✅ ALWAYS return a list
    return all_events
