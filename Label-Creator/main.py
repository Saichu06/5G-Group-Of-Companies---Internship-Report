from cli import (
    prompt_issue_iid,
    prompt_label_name,
    prompt_color,
    prompt_description,
)
from controller import apply_label


def main():
    print("\n=== GitLab Manual Label Tool ===\n")

    issue_iid = prompt_issue_iid()
    label_name = prompt_label_name()
    color = prompt_color()
    description = prompt_description()

    print("\nProcessing...\n")
    apply_label(issue_iid, label_name, color, description)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
