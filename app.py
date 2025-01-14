from flask import Flask, render_template, request, redirect, url_for, jsonify
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import (
    ListUsers, AddUser, SetUserValues, RecommendItemsToUser, AddRating, SetViewPortion, GetItemValues 
)
from recombee_logic import (
    check_user_exists,
    recommend_songs_for_user,
    create_new_user,
    send_rating_interaction,
    send_view_portion_interaction
)

client = RecombeeClient(
    'sr-music',
    'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97', 
    region=Region.EU_WEST
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = request.form["user_id"]
        if check_user_exists(user_id):
            return redirect(url_for("recommendations", user_id=user_id))
        else:
            return render_template("create_account_prompt.html", user_id=user_id)
    return render_template("index.html")


@app.route("/recommendations/<user_id>", methods=["GET", "POST"])
def recommendations(user_id):
    songs = recommend_songs_for_user(user_id)
    return render_template("recommendations.html", user_id=user_id, songs=songs)

@app.route("/interact", methods=["POST"])
def interact():
    data = request.json
    action = data["action"]
    user_id = data["user_id"]
    song_id = data["song_id"]
    if action == "like":
        send_rating_interaction(user_id, song_id, 1)
    elif action == "dislike":
        send_rating_interaction(user_id, song_id, -1)
    return jsonify({"status": "success"})

@app.route("/set_view_portion", methods=["POST"])
def set_view_portion():
    data = request.json
    user_id = data["user_id"]
    song_id = data["song_id"]
    percent_listened = data["portion"]
    send_view_portion_interaction(user_id, song_id, percent_listened)
    
    return jsonify({"status": "success"})

# Track the currently playing song and its progress globally
current_playing_song = None
current_playing_time = 0

@app.route('/stop_song', methods=['POST'])
def stop_song():
    global current_playing_song, current_playing_time

    if current_playing_song:
        data = request.json
        user_id = data["user_id"]
        song_id = current_playing_song
        progress = data["progress"]  # A float value between 0 and 1 representing how much of the song was played

        # Send SetViewPortion to Recombee
        client.send(SetViewPortion(user_id, song_id, progress))

        # Reset playing state
        current_playing_song = None
        current_playing_time = 0

    return jsonify({"status": "stopped"})

@app.route('/play_song', methods=['POST'])
def play_song():
    global current_playing_song, current_playing_time

    data = request.json
    user_id = data["user_id"]
    song_id = data["song_id"]

    # Stop the currently playing song (if any) before starting a new one
    if current_playing_song and current_playing_song != song_id:
        progress = current_playing_time / 60  # Assuming each song is 60 seconds
        client.send(SetViewPortion(user_id, current_playing_song, progress))

    # Update the currently playing song
    current_playing_song = song_id
    current_playing_time = 0

    return jsonify({"status": "playing", "song_id": song_id})

@app.route('/create_account', methods=['POST'])
def create_account():
    print("Hello")
    data = request.json
    user_id = data["user_id"]
    print(user_id)
    name = data["name"]
    gender = data["gender"]
    birthday = data["birthday"]
    genres = data["genres"]

    # Create the user in Recombee
    client.send(AddUser(user_id))
    client.send(SetUserValues(user_id, {
        "Name": name,
        "Gender": gender,
        "Birthday": birthday,
        "Genres": genres
    }))

    # Fetch recommendations for the cold start case
    recommendations = recommend_songs_for_user(user_id)
    print(recommendations)
    return jsonify({"status": "account_created", "recommendations": recommendations})



if __name__ == "__main__":
    app.run(debug=True)
