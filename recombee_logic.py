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

def interaction_exists(user_id, song_id, interaction_type):
    if interaction_type == "rating":
        existing_ratings = client.send(ListUserRatings(user_id))
        return any(rating["itemId"] == song_id for rating in existing_ratings)
    elif interaction_type == "view_portion":
        existing_views = client.send(ListUserViewPortions(user_id))
        return any(view["itemId"] == song_id for view in existing_views)
    return False

# Function to check if user has interactions
def user_has_interactions(user_id):
    try:
        # Fetch user ratings and view portions
        ratings = client.send(ListUserRatings(user_id))
        view_portions = client.send(ListUserViewPortions(user_id))
        return len(ratings) > 0 or len(view_portions) > 0
    except Exception as e:
        print(f"Error checking interactions for user {user_id}: {e}")
        return False

# Fetch the user's genres
def get_user_genres(user_id):
    try:
        user_data = client.send(GetUserValues(user_id))  # Fetch user details
        return user_data.get("Genres", [])  # Retrieve the Genres field
    except Exception as e:
        print(f"Error fetching genres for user {user_id}: {e}")
        return []


# Function for cold-start recommendations based on liked genres
def recommend_based_on_genres(user_id, genre_count=10):
    try:
        # Fetch user's genres
        user_genres = get_user_genres(user_id)
        if not user_genres:
            print("User does not have genre preferences set. Cannot provide recommendations.")
            return []

        # Create the filter string for genres without using backslashes
        genre_filter = "'genre' in {" + ", ".join([f'\"{genre}\"' for genre in user_genres]) + "}"
        print(genre_filter)

        # Make recommendation request
        response = client.send(RecommendItemsToUser(
            user_id=user_id,
            count=genre_count,
            filter=genre_filter
        ))
        print(response["recomms"])
        # Extract and return the recommended item IDs
        return [rec["id"] for rec in response["recomms"]]
    except Exception as e:
        print(f"Error during genre-based recommendation for user {user_id}: {e}")
        return []

# Function for recommendations based on previous interactions
def recommend_based_on_interactions(user_id, count=10):
    try:
        recommendations = client.send(RecommendItemsToUser(user_id, count))
        return [rec["id"] for rec in recommendations["recomms"]]
    except Exception as e:
        print(f"Error during interaction-based recommendations for user {user_id}: {e}")
        return []

def recommend_songs_for_user(user_id):
    # Determine if the user has interactions
    has_interactions = user_has_interactions(user_id)

    if has_interactions:
        print("User has previous interactions. Fetching interaction-based recommendations...")
        recommendations = recommend_based_on_interactions(user_id)
    else:
        print("User has no previous interactions. Fetching genre-based recommendations...")
        recommendations = recommend_based_on_genres(user_id)

    # List to store song details
    recommended_songs = []

    # Fetch song details for each recommendation
    for song_id in recommendations:
        try:
            song_details = client.send(GetItemValues(song_id))
            track_name = song_details.get('track_name', 'Unknown Track')
            track_artist = song_details.get('track_artist', 'Unknown Artist')
            recommended_songs.append({
                "id": song_id,
                "name": track_name,
                "artist": track_artist
            })
        except Exception as e:
            print(f"Error fetching details for song ID {song_id}: {e}")
            recommended_songs.append({
                "id": song_id,
                "name": "Unknown Track",
                "artist": "Unknown Artist"
            })

    return recommended_songs

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
