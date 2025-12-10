from gitlab_service import get_time_report
from export_excel import export_to_excel

if __name__ == "__main__":
    print("Fetching GitLab Issues...")
    report = get_time_report()

    print("Exporting to Excel...")
    export_to_excel(report)

    print("DONE.")
