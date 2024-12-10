from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import (
    ListUserRatings,
    ListUserViewPortions,
    RecommendItemsToUser,
    ListItems,
    ListUsers,
    AddRating,
    SetUserValues,
    AddUser,
    GetItemValues, 
    GetUserValues
)
import random

# Initialize Recombee client
client = RecombeeClient(
    'sr-music',
    'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97', 
    region=Region.EU_WEST
)

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
def recommend_based_on_genres(user_id, genre_count=5):
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

        # Extract and return the recommended item IDs
        return [rec["id"] for rec in response["recomms"]]
    except Exception as e:
        print(f"Error during genre-based recommendation for user {user_id}: {e}")
        return []



# Function for recommendations based on previous interactions
def recommend_based_on_interactions(user_id, count=5):
    try:
        recommendations = client.send(RecommendItemsToUser(user_id, count))
        return [rec["id"] for rec in recommendations["recomms"]]
    except Exception as e:
        print(f"Error during interaction-based recommendations for user {user_id}: {e}")
        return []

def fetch_item_details(item_id):
    try:
        # Fetch item details for the specific item_id
        item_details = client.send(GetItemValues(item_id))
        track_name = item_details.get("track_name", "Unknown Track")
        track_artist = item_details.get("track_artist", "Unknown Artist")
        return track_name, track_artist
    except Exception as e:
        print(f"Error fetching item details for {item_id}: {e}")
        return "Unknown Track", "Unknown Artist"

# Function to display recommendations with song details
def display_recommendations(recommendations):
    print("\nRecommended Songs:")
    if not recommendations:
        print("No recommendations available.")
        return

    for item_id in recommendations:
        track_name, track_artist = fetch_item_details(item_id)
        print(f" - {track_name} by {track_artist}")

# Function to create a new user
def create_new_user():
    user_id = input("Enter a unique User ID: ")
    name = input("Enter your name: ")
    gender = input("Enter your gender (Male/Female/Other): ")
    birthday = input("Enter your birthday (YYYY-MM-DD): ")
    
    # Available genres
    possible_genres = ['pop', 'rap', 'rock', 'latin', 'r&b', 'edm']
    print("Available genres: ", possible_genres)
    
    user_genres = []
    print("Select 3 genres you like.")
    while len(user_genres) < 3:
        genre = input(f"Select genre {len(user_genres)+1}: ").strip().lower()
        if genre in possible_genres and genre not in user_genres:
            user_genres.append(genre)
        else:
            print("Invalid genre or already selected. Try again.")

    # Add the new user to the database
    try:
        client.send(AddUser(user_id))
        client.send(SetUserValues(
            user_id,
            {
                "Name": name,
                "Gender": gender,
                "Birthday": birthday,
                "Genres": user_genres
            },
            cascade_create=True
        ))
        print(f"User {user_id} has been successfully created!")
        return user_id
    except Exception as e:
        print(f"Error creating user {user_id}: {e}")
        return None

# Main script
def main():
    user_id = input("Enter the User ID: ")

    # Check if user exists in the database
    try:
        users = client.send(ListUsers())  # Returns a list of user IDs (strings)
        if user_id not in users:
            print(f"User {user_id} does not exist in the database.")
            create_account = input("Do you want to create a new account? (yes/no): ").strip().lower()
            if create_account == "yes":
                user_id = create_new_user()
                if not user_id:
                    print("Failed to create a new account. Exiting.")
                    return
            else:
                print("Exiting without creating an account.")
                return
    except Exception as e:
        print(f"An error occurred while checking user existence: {e}")
        return

    # Determine if the user has interactions
    has_interactions = user_has_interactions(user_id)

    if has_interactions:
        print("User has previous interactions. Fetching interaction-based recommendations...")
        recommendations = recommend_based_on_interactions(user_id)
    else:
        print("User has no previous interactions. Fetching genre-based recommendations...")
        recommendations = recommend_based_on_genres(user_id)

    # Display recommendations with details
    display_recommendations(recommendations)

if __name__ == "__main__":
    main()
