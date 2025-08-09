from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Points system
POINTS = {
    "Easy": 10,
    "Medium": 25,
    "Hard": 50
}
DOUBLE_LANGS = {"java", "cpp", "c"}

def fetch_recent_submissions(username):
    query = """
    query recentAcSubmissions($username: String!) {
      recentAcSubmissionList(username: $username, limit: 50) {
        title
        titleSlug
        timestamp
        lang
      }
    }
    """
    response = requests.post(LEETCODE_GRAPHQL_URL, json={
        "query": query,
        "variables": {"username": username}
    }, headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        return {"error": f"LeetCode API returned status {response.status_code}"}

    data = response.json()
    if "errors" in data:
        return {"error": "Invalid username or API error"}

    return data["data"]["recentAcSubmissionList"]

def fetch_problem_difficulty(title_slug):
    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        difficulty
      }
    }
    """
    response = requests.post(LEETCODE_GRAPHQL_URL, json={
        "query": query,
        "variables": {"titleSlug": title_slug}
    }, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        data = response.json()
        if data.get("data") and data["data"].get("question"):
            return data["data"]["question"]["difficulty"]
    return "Unknown"

@app.route("/leetcode", methods=["GET"])
def get_last_7_days_solved():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    submissions = fetch_recent_submissions(username)
    if isinstance(submissions, dict) and "error" in submissions:
        return jsonify(submissions), 400

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    seen_titles = set()
    results = []
    easy_count = medium_count = hard_count = total_score = 0

    for sub in submissions:
        sub_time = datetime.utcfromtimestamp(int(sub["timestamp"]))
        if sub_time >= seven_days_ago and sub["title"] not in seen_titles:
            seen_titles.add(sub["title"])
            difficulty = fetch_problem_difficulty(sub["titleSlug"])

            # Count difficulties
            if difficulty == "Easy":
                easy_count += 1
            elif difficulty == "Medium":
                medium_count += 1
            elif difficulty == "Hard":
                hard_count += 1

            # Calculate score
            base_points = POINTS.get(difficulty, 0)
            lang_lower = sub["lang"].lower()
            if any(lang in lang_lower for lang in DOUBLE_LANGS):
                points = base_points * 2
            else:
                points = base_points

            total_score += points

            results.append({
                "title": sub["title"],
                "difficulty": difficulty,
                "language": sub["lang"],
                "time": sub_time.strftime("%Y-%m-%d %H:%M:%S"),
                "points": points
            })

    return jsonify({
        "username": username,
        "total_unique_solved": len(results),
        "easy": easy_count,
        "medium": medium_count,
        "hard": hard_count,
        "total_score": total_score,
        "problems": results
    })

if __name__ == "__main__":
    from flask_cors import CORS
    CORS(app)
    app.run(host="0.0.0.0", port=5000)
