from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import ListUsers, ListItems, SetViewPortion, AddRating
import random

# Initialize Recombee client
client = RecombeeClient(
    'sr-music',
    'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97',
    region=Region.EU_WEST
)

# Fetch all users and songs from the database
def fetch_users_and_songs():
    try:
        users = client.send(ListUsers())  # Retrieve all user IDs
        songs = client.send(ListItems())  # Retrieve all song IDs
        return users, songs
    except Exception as e:
        print(f"An error occurred while fetching users or songs: {e}")
        return [], []

# Get the list of users and songs
users, songs = fetch_users_and_songs()

# Validate we have enough users and songs
if not users or not songs:
    print("No users or songs found in the database. Exiting.")
    exit()

# Interaction settings
milestones = [0.15, 0.50, 0.75, 1.00]  # Listening milestones
ratings = [1.0, -1.0]  # Liked or disliked

# Generate 5000 random interactions
for _ in range(5000):
    user = random.choice(users)  # Random user
    song = random.choice(songs)  # Random song
    
    # Randomly choose an interaction type
    interaction_type = random.choice(["view_portion", "rating"])
    
    try:
        if interaction_type == "view_portion":
            # Log a random listening milestone
            portion = random.choice(milestones)
            client.send(SetViewPortion(user_id=user, item_id=song, portion=portion))
        elif interaction_type == "rating":
            # Log a like or dislike rating
            rating = random.choice(ratings)
            client.send(AddRating(user_id=user, item_id=song, rating=rating))
    except Exception as e:
        print(f"An error occurred while logging interaction for user {user} and song {song}: {e}")

print("Random user interactions have been successfully logged!")
