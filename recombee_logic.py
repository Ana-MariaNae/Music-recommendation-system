from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import (
    ListUsers, AddUser, SetUserValues, RecommendItemsToUser, AddRating, SetViewPortion, GetItemValues,
    ListUserRatings, ListUserViewPortions, GetUserValues 
)

client = RecombeeClient(
    'sr-music',
    'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97', 
    region=Region.EU_WEST
)

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
    """
    Recomandă melodii utilizatorului pe baza interacțiunilor sau preferințelor de gen.
    """
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
    try:
        if not interaction_exists(user_id, song_id, "view_portion"):
            client.send(SetViewPortion(user_id, song_id, percent_listened))
            print(f"Registered view for song {song_id} by user {user_id}")
        else:
            print(f"View already registered for song {song_id} by user {user_id}")
    except Exception as e:
        print(f"Error registering view for song {song_id} by user {user_id}: {e}")
