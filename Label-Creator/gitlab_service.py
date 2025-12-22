import time
import requests
from requests.exceptions import RequestException

from config import GITLAB_TOKEN, PROJECT_ID, GITLAB_URL

BASE_URL = f"{GITLAB_URL}/api/v4"
HEADERS = {"Private-Token": GITLAB_TOKEN}
TIMEOUT = 20

MAX_RETRIES = 3
RETRY_DELAY = 2


def safe_request(method, url, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                verify=False,
                **kwargs
            )
            response.raise_for_status()
            return response

        except RequestException as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"GitLab API failed: {exc}") from exc

            wait = RETRY_DELAY * attempt
            print(f"[Retry {attempt}/{MAX_RETRIES}] {exc} → retrying in {wait}s")
            time.sleep(wait)

    raise RuntimeError("safe_request exited unexpectedly")


def ensure_label_exists(name, color="#428BCA", description=None):
    url = f"{BASE_URL}/projects/{PROJECT_ID}/labels"
    payload = {"name": name, "color": color}

    if description:
        payload["description"] = description

    response = safe_request("POST", url, json=payload)

    # GitLab returns 409 if label already exists
    if response.status_code == 409:
        return False

    return True


def add_label_to_issue(issue_iid, label_name):
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues/{issue_iid}"
    payload = {"add_labels": label_name}

    safe_request("PUT", url, json=payload)
