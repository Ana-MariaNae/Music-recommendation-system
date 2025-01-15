from flask import Flask, render_template, request, session, redirect
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import (
    ListUsers, AddUser, SetUserValues, RecommendItemsToUser, AddRating, SetViewPortion, GetItemValues,
    ListUserRatings, ListUserViewPortions, GetUserValues, AddUserProperty
)

client = RecombeeClient(
    'sr-music',
    'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97',
    region=Region.EU_WEST
)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        if authenticate_user(user_id, password):
            session['user_id'] = user_id
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid user ID or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        name = request.form['name']
        gender = request.form['gender']
        birthday = request.form['birthday']
        genres = request.form['genres'].split(',')
        success, message = create_new_user_with_password(user_id, password, name, gender, birthday, genres)
        if success:
            session['user_id'] = user_id
            return redirect('/dashboard')
        else:
            return render_template('register.html', error=message)
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    recommended_songs = recommend_songs_for_user(user_id)
    return render_template('dashboard.html', songs=recommended_songs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/like', methods=['POST'])
def like():
    data = request.json
    user_id = session.get('user_id')  # Verificăm utilizatorul autentificat
    song_id = data.get('song_id')

    if not user_id or not song_id:
        return {"error": "Invalid request"}, 400

    try:
        like_song(user_id, song_id)
        return {"message": "Song liked successfully!"}, 200
    except Exception as e:
        print(f"Error liking song {song_id} for user {user_id}: {e}")
        return {"error": "Failed to like the song"}, 500
    
    
@app.route('/play', methods=['POST'])
def play():
    data = request.json
    user_id = session.get('user_id')  # Verificăm utilizatorul autentificat
    song_id = data.get('song_id')

    if not user_id or not song_id:
        return {"error": "Invalid request"}, 400

    try:
        send_view_portion_interaction(user_id, song_id, 1.0)  # Înregistrăm că utilizatorul a ascultat 100% din melodie
        return {"message": "Song play registered successfully!"}, 200
    except Exception as e:
        print(f"Error registering play for song {song_id} by user {user_id}: {e}")
        return {"error": "Failed to register play"}, 500




def ensure_password_property():
    try:
        client.send(AddUserProperty('password', 'string'))
        print("Property 'password' added successfully.")
    except Exception as e:
        print(f"Error adding 'password' property: {e}")

ensure_password_property()

def check_user_exists(user_id):
    users = client.send(ListUsers())
    return user_id in users

def authenticate_user(user_id, password):
    try:
        if not check_user_exists(user_id):
            return False
        user_data = client.send(GetUserValues(user_id))
        return user_data.get("password") == password
    except Exception as e:
        print(f"Error authenticating user {user_id}: {e}")
        return False

def create_new_user_with_password(user_id, password, name, gender, birthday, genres):
    try:
        if check_user_exists(user_id):
            return False, "User already exists."
        client.send(AddUser(user_id))
        client.send(SetUserValues(user_id, {
            "password": password,
            "Name": name,
            "Gender": gender,
            "Birthday": birthday,
            "Genres": genres
        }, cascade_create=True))
        return True, "User registered successfully."
    except Exception as e:
        print(f"Error creating new user {user_id}: {e}")
        return False, "Error creating user."

def interaction_exists(user_id, song_id, interaction_type):
    if interaction_type == "rating":
        existing_ratings = client.send(ListUserRatings(user_id))
        return any(rating["itemId"] == song_id for rating in existing_ratings)
    elif interaction_type == "view_portion":
        existing_views = client.send(ListUserViewPortions(user_id))
        return any(view["itemId"] == song_id for view in existing_views)
    return False

def user_has_interactions(user_id):
    try:
        ratings = client.send(ListUserRatings(user_id))
        view_portions = client.send(ListUserViewPortions(user_id))
        return len(ratings) > 0 or len(view_portions) > 0
    except Exception as e:
        print(f"Error checking interactions for user {user_id}: {e}")
        return False

def get_user_genres(user_id):
    try:
        user_data = client.send(GetUserValues(user_id))
        return user_data.get("Genres", [])
    except Exception as e:
        print(f"Error fetching genres for user {user_id}: {e}")
        return []

def recommend_based_on_genres(user_id, genre_count=10):
    try:
        user_genres = get_user_genres(user_id)
        if not user_genres:
            print("User does not have genre preferences set. Cannot provide recommendations.")
            return []

        genre_filter = "'genre' in {" + ", ".join([f'\"{genre}\"' for genre in user_genres]) + "}"
        print(genre_filter)

        response = client.send(RecommendItemsToUser(
            user_id=user_id,
            count=genre_count,
            filter=genre_filter
        ))
        print(response["recomms"])
        return [rec["id"] for rec in response["recomms"]]
    except Exception as e:
        print(f"Error during genre-based recommendation for user {user_id}: {e}")
        return []

def recommend_based_on_interactions(user_id, count=10):
    try:
        recommendations = client.send(RecommendItemsToUser(user_id, count))
        return [rec["id"] for rec in recommendations["recomms"]]
    except Exception as e:
        print(f"Error during interaction-based recommendations for user {user_id}: {e}")
        return []

def recommend_songs_for_user(user_id):
    try:
        has_interactions = user_has_interactions(user_id)

        if has_interactions:
            print("User has previous interactions. Fetching interaction-based recommendations...")
            recommendations = client.send(RecommendItemsToUser(
                user_id=user_id,
                count=10,
                booster="'track_popularity' * 1.2",  
                diversity=0.3
            ))
        else:
            print("User has no previous interactions. Fetching genre-based recommendations...")
            recommendations = client.send(RecommendItemsToUser(
                user_id=user_id,
                count=10,
                filter="'track_popularity' < 500",
                booster="'track_popularity' * 0.5",  
                diversity=0.8
            ))

        print(f"Raw recommendations for user {user_id}: {recommendations}")

        recommended_songs = []

        for rec in recommendations["recomms"]:
            try:
                song_details = client.send(GetItemValues(rec["id"]))
                recommended_songs.append({
                    "id": rec["id"],
                    "name": song_details.get('track_name', 'Unknown Track'),
                    "artist": song_details.get('track_artist', 'Unknown Artist')
                })
            except Exception as e:
                print(f"Error fetching details for song ID {rec['id']}: {e}")
                recommended_songs.append({
                    "id": rec["id"],
                    "name": "Unknown Track",
                    "artist": "Unknown Artist"
                })

        return recommended_songs

    except Exception as e:
        print(f"Error fetching recommendations for user {user_id}: {e}")
        return []

def like_song(user_id, song_id):
    try:
        if not interaction_exists(user_id, song_id, "rating"):
            client.send(AddRating(user_id, song_id, 1.0))
            print(f"User {user_id} liked song {song_id}")
    except Exception as e:
        print(f"Error liking song {song_id} for user {user_id}: {e}")

def create_new_user(user_id, name, gender, birthday, genres):
    client.send(AddUser(user_id))
    client.send(SetUserValues(user_id, {
        "Name": name,
        "Gender": gender,
        "Birthday": birthday,
        "Genres": genres
    }, cascade_create=True))

def send_rating_interaction(user_id, song_id, rating):
    if not interaction_exists(user_id, song_id, "rating"):
        client.send(AddRating(user_id, song_id, rating))

def send_view_portion_interaction(user_id, song_id, percent_listened):
    if not interaction_exists(user_id, song_id, "view_portion"):
        client.send(SetViewPortion(user_id, song_id, percent_listened))
        

if __name__ == '__main__':
    app.run(debug=True)
