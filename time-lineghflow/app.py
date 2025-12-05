from flask import Flask, jsonify
from github_service import fetch_issues, parse_issue

app = Flask(__name__)


@app.route("/issues")
def get_all_issues():
    """Return all issues with timeline data"""
    issues = fetch_issues()
    formatted = [parse_issue(issue) for issue in issues]
    return jsonify(formatted)


@app.route("/issues/<int:number>")
def get_single_issue(number):
    """Return timeline for one specific issue"""
    issues = fetch_issues()

    for issue in issues:
        if issue["number"] == number:
            return jsonify(parse_issue(issue))

    return jsonify({"error": "Issue not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
