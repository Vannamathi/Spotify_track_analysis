import re
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import mysql.connector

# Set up Client credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='40e01bc80c824e8280b3c7035220607c',
    client_secret='828c29e4037b44548c38fe4caa5f5af8'
))

# MySQL Database Connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'spotify_db'
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Read URLs from text file
file_path = 'track.txt'
with open(file_path, 'r') as file:
    track_urls = file.readlines()

# Initialize list to store track data
all_tracks_data = []

# Process each URL
for track_url in track_urls:
    track_url = track_url.strip()
    try:
        track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)
        track = sp.track(track_id)

        track_data = {
            'Track Name': track['name'],
            'Artist': track['artists'][0]['name'],
            'Album': track['album']['name'],
            'Popularity': track['popularity'],
            'Duration (minutes)': track['duration_ms'] / 60000
        }

        # Add to list for DataFrame
        all_tracks_data.append(track_data)

        # Insert into MySQL
        insert_query = """
        INSERT INTO Spotify_full_track (track_name, artist, album, popularity, duration_minutes)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            track_data['Track Name'],
            track_data['Artist'],
            track_data['Album'],
            track_data['Popularity'],
            track_data['Duration (minutes)']
        ))
        connection.commit()

        print(f"Track '{track_data['Track Name']}' by {track_data['Artist']} inserted into the database.")
    except Exception as e:
        print(f"Error Processing URL: {track_url}, Error: {e}")

# Close MySQL connection
cursor.close()
connection.close()

# Convert all collected data to DataFrame
df = pd.DataFrame(all_tracks_data)

print("\nAll Track Data as DataFrame:")
print(df)

# Save to CSV
df.to_csv('Full_Track.csv', index=False)
print('All tracks inserted and saved to CSV successfully.')
