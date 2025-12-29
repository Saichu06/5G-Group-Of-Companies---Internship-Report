"""
GitLab Label Creator (YAML based).

Reads label definitions from a YAML file (Mindshare export)
and creates or updates labels across multiple GitLab projects.
"""

import time
import requests
import yaml
from requests.exceptions import RequestException

import config


BASE_URL = f"{config.GITLAB_URL}/api/v4"
HEADERS = {
    "PRIVATE-TOKEN": config.GITLAB_TOKEN
}


# ---------- HTTP WITH RETRIES ----------
def safe_request(method, url, **kwargs):
    """
    Perform an HTTP request with retry logic.
    """
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=HEADERS,
                timeout=config.TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response
        except RequestException as exc:
            if attempt == config.MAX_RETRIES:
                raise
            wait = config.RETRY_DELAY * attempt
            print(f"[Retry {attempt}] {exc} → retrying in {wait}s")
            time.sleep(wait)

    raise RuntimeError("Request failed unexpectedly")


# ---------- LOAD YAML ----------
def load_labels_from_yaml(file_path):
    """
    Load label definitions from YAML file.

    Args:
        file_path (str): Path to YAML file

    Returns:
        list: List of label dictionaries
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data.get("labels", [])


# ---------- FETCH EXISTING LABELS ----------
def fetch_existing_labels(project_id):
    """
    Fetch existing labels for a project.
    """
    url = f"{BASE_URL}/projects/{project_id}/labels"
    labels = {}
    page = 1

    while True:
        params = {"per_page": 100, "page": page}
        response = safe_request("GET", url, params=params)
        data = response.json()

        if not data:
            break

        for label in data:
            labels[label["name"]] = label

        page += 1

    return labels


# ---------- CREATE LABEL ----------
def create_label(project_id, label):
    """
    Create a label in GitLab project.
    """
    url = f"{BASE_URL}/projects/{project_id}/labels"
    payload = {
        "name": label["name"],
        "color": label["color"],
        "description": label.get("description", "")
    }
    safe_request("POST", url, data=payload)
    print(f"✅ [{project_id}] Created label: {label['name']}")


# ---------- UPDATE LABEL ----------
def update_label(project_id, label):
    """
    Update an existing label in GitLab project.
    """
    url = f"{BASE_URL}/projects/{project_id}/labels"
    payload = {
        "name": label["name"],
        "color": label["color"],
        "description": label.get("description", "")
    }
    safe_request("PUT", url, data=payload)
    print(f"🔄 [{project_id}] Updated label: {label['name']}")


# ---------- PROCESS LABELS ----------
def sync_labels(yaml_file):
    """
    Sync YAML labels to all configured GitLab projects.
    """
    labels = load_labels_from_yaml(yaml_file)

    if not labels:
        print("⚠️ No labels found in YAML file.")
        return

    for project_id in config.PROJECT_IDS:
        print(f"\n📦 Processing project: {project_id}")

        existing_labels = fetch_existing_labels(project_id)
        print(f"Existing labels: {len(existing_labels)}")

        for label in labels:
            name = label.get("name")
            color = label.get("color")

            if not name or not color:
                print(f"⚠️ Invalid label definition: {label}")
                continue

            if name in existing_labels:
                update_label(project_id, label)
            else:
                create_label(project_id, label)


# ---------- ENTRY POINT ----------
def main():
    """
    Entry point for YAML-based label creator.
    """
    yaml_file = "labels.yaml"
    print("Starting GitLab Label Creator (YAML-based)...")
    sync_labels(yaml_file)
    print("\nLabel sync completed successfully.")


if __name__ == "__main__":
    main()
