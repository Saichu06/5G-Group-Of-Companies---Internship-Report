from gitlab_fast_service import generate_time_log_report
from export_excel import export_time_logs

if __name__ == "__main__":
    logs = generate_time_log_report(days=7)
    export_time_logs(logs)