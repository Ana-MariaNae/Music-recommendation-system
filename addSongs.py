from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddItem, SetItemValues, AddItemProperty, DeleteItem, DeleteItemProperty
import pandas as pd

# Read from csv file
df= pd.read_csv("spotify_songs.csv", nrows=1299)

# Drop the duplicates
songs = df.drop_duplicates(subset='track_id')
print(len(songs))

# Initialize Recombee client 
client = RecombeeClient(
  'sr-music',
  'ItSE2Fz5VPPfRyu8vSUT7KhgNNjpwugJI5AUwvP9HeNMbI6iO2rtdzYkgly5Ud97',
  region=Region.EU_WEST
)

# Send item id 
# for index, row in songs.iterrows():
#     client.send(AddItem(row.at["track_id"]))

print("All items were added")

# # Add items property and type
# item_properties = {
#     'track_name': 'string',
#     'track_artist': 'string',
#     'track_popularity': 'int',
#     'tempo': 'string',
#     'danceability': 'string',
#     'energy': 'string',
#     'key': 'int',
#     'mode': 'int',
#     'loudness': 'string',
#     'speechiness': 'string',
#     'acousticness': 'string',
#     'instrumentalness': 'string',
#     'liveness': 'string',
#     'valence': 'string'
# }
item_properties = {'genre': 'string'}

for prop, prop_type in item_properties.items():
    client.send(AddItemProperty(prop, prop_type))

print("Properties were set")

# Send values for the items
for index, row in songs.iterrows():
    client.send(SetItemValues(row.at['track_id'], 
            {'genre': row.at['playlist_genre']},
    # 
            # 'track_name': row.at['track_name'],
            # 'track_artist': row.at['track_artist'],
            # 'track_popularity': row.at['track_popularity'],
            # 'tempo': row.at['tempo'],
            # 'danceability': row.at['danceability'],
            # 'energy': row.at['energy'],
            # 'key': row.at['key'],
            # 'mode': row.at['mode'],
            # 'loudness': row.at['loudness'],
            # 'speechiness': row.at['speechiness'],
            # 'acousticness': row.at['acousticness'],
            # 'instrumentalness': row.at['instrumentalness'],
            # 'liveness': row.at['liveness'],
            # 'valence': row.at['valence']},
            cascade_create=True
    )
    )

print("Values for the items were added")