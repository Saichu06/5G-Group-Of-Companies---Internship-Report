# pylint: disable=no-name-in-module
import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import requests
import urllib3
from requests.exceptions import RequestException

# Local
from config import GITLAB_TOKEN, PROJECT_ID


MAX_RETRIES=3
RETRY_DELAY=2

IST = timezone(timedelta(hours=5, minutes=30))


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GITLAB_URL = "https://git.fifthgentech.com"
BASE_URL = f"{GITLAB_URL}/api/v4"

HEADERS = {"Private-Token": GITLAB_TOKEN}
TIMEOUT = 20
MAX_WORKERS = 8


#filtering last 7 days with the formula 7-now

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


#to fetch time tracking entries
def get_spend_events(issue_iid):
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues/{issue_iid}/notes"

    response = safe_get(url)
    notes = response.json()

    events = []
    for note in notes:
        if note.get("system") and "time spent" in note["body"].lower():

            utc_time = datetime.fromisoformat(
                note["created_at"].replace("Z", "+00:00")
            )
            ist_time = utc_time.astimezone(IST)

            events.append({
                "issue_iid": issue_iid,
                "user": note["author"]["username"],
                "message": note["body"],
                "created_at_ist": ist_time.strftime("%Y-%m-%d %H:%M:%S")
            })

    return events


def safe_get(url, params=None):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                verify=False,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return response

        except RequestException as exc:
            if attempt == MAX_RETRIES:
                raise  # final failure

            wait_time = RETRY_DELAY * attempt
            print(
                f"[Retry {attempt}/{MAX_RETRIES}] "
                f"Error: {exc}. Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)
    raise RuntimeError("safe_get() exited retry loop unexpectedly")




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


#generating log based on fetched issues/log
def generate_time_log_report(days=7):
    issues = get_recent_issues(days)
    print(f"Recent issues fetched: {len(issues)}")

    logs = collect_time_logs(issues)
    print(f"Total time log entries: {len(logs)}")
    return logs
