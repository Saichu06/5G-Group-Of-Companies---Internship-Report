"""
Configuration settings for GitLab automation services.

Contains GitLab connection details, project IDs,
and common network retry settings.
"""

GITLAB_URL = "http://192.168.17.9:6001"
GITLAB_TOKEN = ""

PROJECT_IDS = []

TIMEOUT = 20
MAX_RETRIES = 3
RETRY_DELAY = 2
