# from gitlab_service import get_time_report
# from export_excel import export_to_excel

# if __name__ == "__main__":
#     print("Fetching GitLab Issues...")
#     report = get_time_report()

#     print("Exporting to Excel...")
#     export_to_excel(report)

#     print("DONE.")


from gitlab_fast_service import generate_time_log_report
from export_excel import export_time_logs

if __name__ == "__main__":
    logs = generate_time_log_report(days=7)
    export_time_logs(logs)
