"""
GitLab Event Time Log Service.

Extracts numeric time spent events from Issues and Merge Requests
across multiple GitLab projects and normalizes them using office
working hours (8h/day, 5 days/week).
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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IST = timezone(timedelta(hours=5, minutes=30))
BASE_URL = f"{config.GITLAB_URL}/api/v4"
HEADERS = {"PRIVATE-TOKEN": config.GITLAB_TOKEN}

HOURS_PER_DAY = 8
DAYS_PER_WEEK = 5
HOURS_PER_WEEK = HOURS_PER_DAY * DAYS_PER_WEEK


# ---------- HTTP ----------
def safe_get(url, params=None):
    """Perform GET request with retry logic."""
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

    Supports:
    - weeks (w) → 5 days × 8 hours
    - days (d) → 8 hours
    - hours (h)
    - minutes (m)

    Examples:
    - 'added 1w 2d of time spent' -> 2880 minutes
    - 'added 1d 1h of time spent' -> 540 minutes
    - 'removed time spent' -> 0
    - 'subtracted 2h of time spent' -> -120
    """
    body = note_body.lower()

    # Explicit reset
    if "removed time spent" in body:
        return 0

    sign = -1 if "subtracted" in body else 1

    weeks = re.search(r"(\d+)w", body)
    days = re.search(r"(\d+)d", body)
    hours = re.search(r"(\d+)h", body)
    minutes = re.search(r"(\d+)m", body)

    total_minutes = 0

    if weeks:
        total_minutes += int(weeks.group(1)) * 5 * 8 * 60
    if days:
        total_minutes += int(days.group(1)) * 8 * 60
    if hours:
        total_minutes += int(hours.group(1)) * 60
    if minutes:
        total_minutes += int(minutes.group(1))

    return sign * total_minutes


# ---------- OFFICE TIME NORMALIZATION ----------
def normalize_office_time(minutes):
    """
    Convert minutes into office time units:
    weeks, days, hours (8h/day, 5 days/week)
    """
    if minutes <= 0:
        return "0 hours"

    total_hours = minutes / 60

    weeks = int(total_hours // HOURS_PER_WEEK)
    remaining_hours = total_hours % HOURS_PER_WEEK

    days = int(remaining_hours // HOURS_PER_DAY)
    hours = round(remaining_hours % HOURS_PER_DAY, 2)

    parts = []
    if weeks:
        parts.append(f"{weeks} week{'s' if weeks > 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    return " ".join(parts)


# ---------- FETCH ISSUES / MRS ----------
def fetch_items(project_id, item_type, days):
    """Fetch issues or merge requests updated within lookback window."""
    updated_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    url = f"{BASE_URL}/projects/{project_id}/{item_type}"

    items = []
    page = 1

    while True:
        params = {
            "per_page": 100,
            "page": page,
            "updated_after": updated_after,
            "scope": "all"
        }
        response = safe_get(url, params)
        data = response.json()

        if not data:
            break

        items.extend(data)
        page += 1

    return items


# ---------- FETCH & PARSE NOTES ----------
def extract_time_events(project_id, event_type, iid):
    """Extract time spent events from issue / MR notes."""
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
            office_time = normalize_office_time(minutes)

            utc_time = datetime.fromisoformat(
                note["created_at"].replace("Z", "+00:00")
            )

            events.append({
                "project_id": project_id,
                "event_type": event_type,
                "event_id": iid,
                "user": note["author"]["username"],
                "time_spent_minutes": minutes,
                "office_time": office_time,
                "created_at_ist": utc_time.astimezone(IST)
                    .strftime("%Y-%m-%d %H:%M:%S")
            })

    return events


# ---------- CORE ----------
def generate_time_log_report(days):
    """Generate normalized time-spent events across all projects."""
    all_events = []

    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        futures = []

        for project_id in config.PROJECT_IDS:
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

        for future in futures:
            result = future.result()
            if result:
                all_events.extend(result)

    return all_events
