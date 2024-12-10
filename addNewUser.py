from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddUser, SetUserValues, GetUserValues

# Initialize Recombee client
client = RecombeeClient(
    'sr-music',
    'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97',
    region=Region.EU_WEST
)

# Define possible genres
possible_genres = ['pop', 'rap', 'rock', 'latin', 'r&b', 'edm']

# Function to check if a user exists
def user_exists(user_id):
    try:
        client.send(GetUserValues(user_id))  # Try to fetch user details
        return True
    except Exception:
        return False

def create_new_user():
    # Input a unique user ID
    while True:
        user_id = input("Enter a unique User ID: ")
        if not user_exists(user_id):
            break
        print("User ID already exists. Please enter a different one.")

    # Input other user details
    name = input("Enter the user's name: ")
    gender = input("Enter the user's gender (Male/Female/Other): ")
    birthday = input("Enter the user's birthday (YYYY-MM-DD): ")

    # Validate genres selection
    print("\nAvailable Genres: ", possible_genres)
    print("Select 3 genres the user likes.")
    user_genres = []
    while len(user_genres) < 3:
        genre = input(f"Select genre {len(user_genres)+1}: ").strip().lower()
        if genre in possible_genres and genre not in user_genres:
            user_genres.append(genre)
        else:
            print("Invalid genre or already selected. Try again.")

    # Add the user to Recombee
    try:
        # Add the user to the database
        client.send(AddUser(user_id))
        
        # Set user values
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
        print(f"User {user_id} has been successfully added to the database!")
    except Exception as e:
        print(f"An error occurred: {e}")
