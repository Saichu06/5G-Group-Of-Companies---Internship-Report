"""
Excel Export Utility for GitLab Time Logs.

Exports ALL GitLab time-spent events (Issues + Merge Requests)
into a SINGLE Excel sheet with full event details.
"""

import openpyxl


def minutes_to_hours(minutes):
    """
    Convert time from minutes to hours.

    Args:
        minutes (int): Time in minutes

    Returns:
        float: Time in hours (rounded to 2 decimals)
    """
    return round(minutes / 60, 2)


def export_time_logs(events, file_name="gitlab_time_logs.xlsx"):
    """
    Export GitLab time log events into one Excel sheet.

    Columns:
    - Project ID
    - Event Type (issue / merge_request)
    - Event ID
    - User
    - Time Spent (Hours)
    - Date (IST)

    Args:
        events (list): Normalized event list
        file_name (str): Output Excel file
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Time Logs"

    headers = [
        "Project ID",
        "Event Type",
        "Event ID",
        "User",
        "Time Spent (Hours)",
        "Date (IST)"
    ]
    ws.append(headers)

    for event in events:
        ws.append([
            event["project_id"],
            event["event_type"],
            event["event_id"],
            event["user"],
            minutes_to_hours(event["time_spent_minutes"]),
            event["created_at_ist"]
        ])

    wb.save(file_name)
    print(f"Excel generated successfully → {file_name}")
    wb.close()
