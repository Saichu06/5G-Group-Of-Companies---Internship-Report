import openpyxl

def export_to_excel(data, file_name="live_issues_report.xlsx"):
    wb = openpyxl.Workbook()

    # Sheet 1: Issue Summary
    ws1 = wb.active
    ws1.title = "Issues Summary"

    headers1 = [
        "Issue IID", "Title", "State", "Assignee",
        "Estimate (hrs)", "Spent (hrs)"
    ]
    ws1.append(headers1)

    for issue in data:
        ws1.append([
            issue["iid"],
            issue["title"],
            issue["state"],
            issue["assignee"],
            issue["estimate_hours"],
            issue["spent_hours"],
        ])

    # Sheet 2: Time Logs
    ws2 = wb.create_sheet("Time Logs")
    headers2 = ["Issue IID", "User", "Message", "Date"]
    ws2.append(headers2)

    for issue in data:
        for log in issue["spend_events"]:
            ws2.append([
                issue["iid"],
                log["user"],
                log["body"],
                log["created_at"]
            ])

    wb.save(file_name)
    print(f"\nExcel Export Completed → {file_name}\n")
