from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddUser, AddUserProperty, SetUserValues, DeleteUser
import pandas as pd
import random

# Read from csv file
db = pd.read_csv("SocialMediaUsersDataset.csv", nrows=50)

# Initialize Recombee client 
client = RecombeeClient(
  'sr-music',
  'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97',
  region=Region.EU_WEST
)

# # User properties
# client.send(AddUserProperty("Name", "string")) 
# client.send(AddUserProperty("Gender", "string"))      
# client.send(AddUserProperty("Birthday", "timestamp")) 
# client.send(AddUserProperty("Genres", "set"))         

# Define possible genres
possible_genres = ['pop', 'rap', 'rock', 'latin', 'r&b', 'edm']

# Add users with random genres
for index, row in db.iterrows():
    # Generate 3 random genres for each user
    user_genres = random.sample(possible_genres, 3)
    
    # Add user and their properties to Recombee
    client.send(AddUser(row.at["UserID"]))
    client.send(SetUserValues(
        row.at["UserID"],  # Using SP ID as the unique user ID
        {
            "Name": row.at["Name"],
            "Gender": row.at["Gender"],
            "Birthday": row.at["DOB"],
            "Genres": user_genres
        },
        cascade_create=True
    ))
