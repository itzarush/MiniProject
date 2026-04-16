from flask import Flask, render_template, request, redirect, url_for
import json
import uuid
import time

app = Flask(__name__)

DATA_FILE = "users.json"
TEAM_SIZE = 2

#It reads all users from the JSON file.
def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

#This function writes user data into the file.
def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

#This function calculates personality type based on answers.
def calculate_cluster(q):

    social = (q[0] + q[4] + q[5]) / 3
    energy = (q[1] + q[9]) / 2
    depth = (q[2] + q[7]) / 2

    if social >= 7:
        return "Extrovert"
    elif depth >= 7:
        return "Deep Thinker"
    else:
        return "Balanced Explorer"

#This function creates teams automatically.
def matchmaking():

    users = load_users()

    waiting = [u for u in users if not u["assigned"]]

    clusters = {}

    for user in waiting:
        cluster = user["cluster"]

        if cluster not in clusters:
            clusters[cluster] = []

        clusters[cluster].append(user)

#This actually forms the teams.
    for cluster in clusters:

        group = clusters[cluster]

        while len(group) >= TEAM_SIZE:

            team = group[:TEAM_SIZE]
            group = group[TEAM_SIZE:]

            team_id = str(uuid.uuid4())

            for member in team:
                member["assigned"] = True
                member["team"] = team_id

    save_users(users)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/submit", methods=["POST"])
def submit():

    username = request.form["username"]

    answers = [int(request.form[f"q{i}"]) for i in range(1, 11)]

    cluster = calculate_cluster(answers)

    uid = str(uuid.uuid4())

    users = load_users()

    user = {
        "id": uid,
        "username": username,
        "answers": answers,
        "cluster": cluster,
        "assigned": False,
        "team": None,
        "time": time.time()
    }

    users.append(user)

    save_users(users)

    return redirect(url_for("personality", uid=uid))

#Shows the user’s personality result.
@app.route("/personality/<uid>")
def personality(uid):

    users = load_users()

    user = next((u for u in users if u["id"] == uid), None)

    return render_template("personality.html", user=user)

#Shows the waiting page.
@app.route("/lobby/<uid>")
def lobby(uid):

    matchmaking()

    users = load_users()

    user = next((u for u in users if u["id"] == uid), None)

    if user["assigned"]:
        return redirect(url_for("team", uid=uid))

    return render_template("lobby.html", uid=uid)

#Displays the final team.
@app.route("/team/<uid>")
def team(uid):

    users = load_users()

    user = next((u for u in users if u["id"] == uid), None)

    team_members = [u for u in users if u.get("team") == user["team"]]

    return render_template("team.html", team=team_members)

#Starts the web server.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)