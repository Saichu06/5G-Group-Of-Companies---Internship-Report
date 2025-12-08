📌 GitHub Issue Timeline Dashboard

A Universal GitHub Repository Issue Analyzer

📖 Overview

The GitHub Issue Timeline Dashboard is a web application that allows users to:

🔍 View issues from any GitHub repository

🧭 Track detailed timelines for each issue

👤 See assignee activity and assignment history

🕒 Calculate time since creation, update, assignment, and time open

📊 See an Open vs Closed issue bar chart

🧹 Search, filter open/closed issues, and sort easily

This tool transforms raw GitHub issue data into an interactive, visual dashboard — perfect for developers, project managers, and interns analyzing repository activity.

🚀 Live Dashboard Flow

User pastes a GitHub repository URL
Example:

https://github.com/python/cpython


The system extracts:

OWNER → python

REPO → cpython

Backend uses your GitHub token to fetch:

/issues?state=all

/issues/{number}/events

Dashboard displays:

Issue cards

Assignment timeline

Time-based metrics

Open/Closed chart

Search + filters

✨ Features
🔹 1. Global Repository Support

Fetch issue data from any GitHub public repository.

🔹 2. Smart Timeline Metrics

Each issue includes:

Time since creation

Time since last update

Total open time

Time since last assignment

🔹 3. Assignment Tracking

Shows every event where a user was assigned.

🔹 4. Dynamic Filters & Search

Filter Open, Closed, or All issues

Search by assignee or title

🔹 5. Visual Issue Chart

A bar chart showing Open vs Closed issues.

🔹 6. Clean Modern UI

Readable issue cards with clear color coding:

Green → Open

Red → Closed



🛠 Tech Stack
Frontend

HTML5

CSS3

JavaScript

Backend

Python

Flask

APIs

GitHub REST API (Issues + Events)

📂 Project Structure
/project-root
│── app.py
│── github_service.py
│── config.py
│── requirements.txt
│
├── /templates
│     └── index.html
│
├── /static
│     └── style.css
│
└── README.md

⚙️ Installation & Setup
1️⃣ Install Python packages
pip install -r requirements.txt

2️⃣ Configure your GitHub Token

Open config.py:

GITHUB_TOKEN = "your_personal_access_token"
OWNER = "default-user"
REPO = "default-repo"

3️⃣ Run the server
python app.py

4️⃣ Open the Dashboard

Visit:

http://127.0.0.1:5000/

🧩 How to Use the Dashboard
✔ Load ANY GitHub repo

Paste:

https://github.com/username/reponame


Click Load Issues.

✔ Filter

All Issues

Open Issues

Closed Issues

✔ Search

Type any keyword — title or assignee.

✔ Analyze

Each issue shows:

Timeline metrics

Assignment history

Labels

Open/closed status

🔐 Why a GitHub Token Is Needed

Even for public repositories, GitHub API only allows 60 requests/hour without a token.

Your dashboard fetches:

All issues

Events for every issue

This quickly exceeds 60 requests.

Using a token increases your limit to:

👉 5,000 requests/hour

Your token is never exposed to users.

🛠 API Endpoints (Backend)
✔ Get all issues
GET /issues?owner=OWNER&repo=REPO

✔ Get a single issue
GET /issues/12?owner=OWNER&repo=REPO
