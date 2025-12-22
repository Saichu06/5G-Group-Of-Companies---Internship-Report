from gitlab_service import ensure_label_exists, add_label_to_issue


def apply_label(issue_iid, label_name, color, description):
    created = ensure_label_exists(label_name, color, description)

    if created:
        print(f"✔ Label '{label_name}' created")
    else:
        print(f"✔ Label '{label_name}' already exists")

    add_label_to_issue(issue_iid, label_name)
    print(f"✔ Label '{label_name}' added to issue #{issue_iid}")
