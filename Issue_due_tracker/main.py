"""
Entry point for the GitLab Issue Due-Date Tracker.

Coordinates data extraction and Excel export.
"""

from due_date_service import build_due_date_rows
from export_excel import export_due_dates


def main():

    """
    Run the issue due-date tracking workflow.

    Fetches issue and assignee data from GitLab
    and exports a weekday-based Excel report.
    """
    rows = build_due_date_rows()
    export_due_dates(rows)


if __name__ == "__main__":
    main()
