import re


def prompt_issue_iid():
    while True:
        try:
            return int(input("Enter Issue IID: ").strip())
        except ValueError:
            print("❌ Issue IID must be a number")


def prompt_label_name():
    while True:
        name = input("Enter label name: ").strip()
        if name:
            return name
        print("❌ Label name cannot be empty")


def prompt_color():
    color = input("Enter label color (#RRGGBB) [default #428BCA]: ").strip()
    if not color:
        return "#428BCA"

    if not re.fullmatch(r"#([0-9a-fA-F]{6})", color):
        print("⚠️ Invalid color, using default")
        return "#428BCA"

    return color


def prompt_description():
    return input("Enter label description (optional): ").strip() or None
