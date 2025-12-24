from gitlab_fast_service import generate_time_log_report
from export_excel import export_time_logs
import config


def main():
    logs = generate_time_log_report(days=config.LOOKBACK_DAYS)

    if not logs:
        print("No time log events found for the given period.")
        return

    export_time_logs(logs)
    print(f"Export completed. Total events: {len(logs)}")


if __name__ == "__main__":
    main()
