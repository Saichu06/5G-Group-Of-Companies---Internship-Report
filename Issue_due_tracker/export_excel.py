"""
Excel Export Utility for GitLab Issue Due-Date Reports.

Exports assignee-wise issue due dates into a weekday-based Excel sheet.
"""

import openpyxl

def export_due_dates(rows, file_name="issue_due_dates.xlsx"):
    """
    Export issue due-date data into an Excel file.

    Columns:
    - User
    - Issue ID
    - Monday
    - Tuesday
    - Wednesday
    - Thursday
    - Friday

    Args:
        rows (list): List of due-date row dictionaries
        file_name (str): Output Excel file name
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Issue Dues"

    headers = [
        "User",
        "Issue ID",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]
    ws.append(headers)

    for row in rows:
        ws.append([
            row["user"],
            row["issue_id"],
            row["Monday"],
            row["Tuesday"],
            row["Wednesday"],
            row["Thursday"],
            row["Friday"]
        ])

    wb.save(file_name)
    wb.close()
    print(f"Excel generated → {file_name}")
