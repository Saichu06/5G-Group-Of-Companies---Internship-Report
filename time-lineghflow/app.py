from flask import Flask, jsonify, render_template, request
from github_service import fetch_issues, parse_issue

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/issues")
def get_all_issues():
    """
    Fetch issues from ANY GitHub repo.
    Example: /issues?owner=python&repo=cpython
    """
    owner = request.args.get("owner")
    repo = request.args.get("repo")

    issues = fetch_issues(owner, repo)
    
    if "message" in issues:  # GitHub error (bad token, repo not found, etc.)
        return jsonify(issues), 400

    formatted = [parse_issue(issue, owner, repo) for issue in issues]
    return jsonify(formatted)

@app.route("/issues/<int:number>")
def get_single_issue(number):
    """Return timeline for one specific issue"""
    owner = request.args.get("owner")
    repo = request.args.get("repo")

    issues = fetch_issues(owner, repo)

    for issue in issues:
        if issue["number"] == number:
            return jsonify(parse_issue(issue, owner, repo))

    return jsonify({"error": "Issue not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
