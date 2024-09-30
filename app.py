import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
from PIL import Image
import json


# Set up Spotify API credentials
CLIENT_ID = st.secrets["MyID"] 
CLIENT_SECRET = st.secrets["MySecret"]

import streamlit as st
import base64
import requests

# OpenAI API Key
api_key = st.secrets["OPENAI_API"]  # Replace with your actual API key

# Function to encode the image to Base64
def encode_image_to_base64(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to send image and prompt to OpenAI API
def send_to_openai_api(base64_image):

    genres = sp.recommendation_genre_seeds()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Payload with the Base64 encoded image and the query
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"Based on this image, can you generate a set of audio features similar to what Spotify uses to analyze tracks? The features should include danceability, energy, instrumentalness, loudness, liveness, speechiness, acousticness, valence,and more. You can refer to Spotify's Audio Features Documentation for the full list of features. Also, add a list of less than 5 exsiting genres that matches the image from {genres} to the json, make sure they are all lowercased. Just return a json format string"
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

    # Make a request to the OpenAI API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)


    # Return the response
    if response.status_code == 200:
        try:
            # Get the raw content
            response_json = response.json()
            # Extract the content field which contains the JSON-like string

            message_content = response_json['choices'][0]['message']['content']

            # Parse the remaining part as JSON
            print(message_content.replace('json', '', 1).strip()[3:-3])
            return json.loads(message_content.replace('json', '', 1).strip()[3:-3])
        
        except Exception as e:
            return f"Error in parsing response: {e}"
    else:
        return f"Error: {response.status_code}, {response.text}"
    
# Streamlit UI
st.title("Generate Spotify Music Features from Image")

# Authenticate with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

response = {
  'audio_features': {
    'danceability': 0.5,
    'energy': 0.7,
    'instrumentalness': 0.4,
    'loudness': -5.5,
    'tempo': 120.0,
    'speechiness': 0.03,
    'acousticness': 0.6,
    'valence': 0.4,
    'liveness': 0.15,
    'key': 5,
    'mode': 1,
    'time_signature': 4
  },
  'genres': ['ambient', 'post-rock', 'experimental', 'instrumental']
}

#respose from chat gpt
created_response = None

# Image uploader for users to upload an image
uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# If an image is uploaded
if uploaded_image:
    # Display the uploaded image
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Button to trigger the API call
    if st.button("Generate Audio Features"):
        # Encode the image to Base64
        base64_image = encode_image_to_base64(uploaded_image)
        
        # Send the image and prompt to OpenAI API
        st.session_state["generated_response"] = send_to_openai_api(base64_image)

        #st.write(st.session_state.get("generated_response"))




# Let users set their own query parameters via sliders and input fields
st.write("Adjust the Spotify query parameters:")

#audio_features = response['choices'][0]['message']['content']["audio_features"] if response else None
#genres = response['choices'][0]['message']['content']["genres"] if response else None

if not  st.session_state.get("generated_response"):
    audio_features = response["audio_features"]
    genres = response["genres"]
else:
    audio_features = st.session_state.get("generated_response")["audio_features"]
    genres = st.session_state.get("generated_response")["genres"]



# Input sliders  adjusting Spotify query parameters
danceability = st.slider("Danceability (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["danceability"])
energy = st.slider("Energy (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["energy"])
instrumentalness = st.slider("Instrumentalness (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["instrumentalness"])
loudness = st.slider("Loudness (-60.0 - 0.0)", min_value=-60.0, max_value=0.0, value= audio_features["loudness"])
tempo = st.slider("Tempo (BPM)", min_value=40, max_value=200, value=120)
speechiness = st.slider("Speechiness (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["speechiness"])
acousticness = st.slider("Acousticness (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["acousticness"])
valence = st.slider("Valence (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["valence"])
liveness = st.slider("Liveness (0.0 - 1.0)", min_value=0.0, max_value=1.0, value= audio_features["liveness"])
key = st.slider("Key (0-11)", min_value=0, max_value=11, value=5)
mode = st.selectbox("Mode (0 for minor, 1 for major)", options=[0, 1], index=1)
duration_ms = st.slider("Duration (milliseconds)", min_value=60000, max_value=600000, value=180000)
time_signature = st.slider("Time Signature", min_value=1, max_value=7, value=4)
limit = st.number_input("Number of Tracks", min_value=1, max_value=50, value=10)

# Function to generate Spotify query based on user inputs
def generate_spotify_query():
    query_params = {
        'danceability': danceability,
        'energy': energy,
        'instrumentalness': instrumentalness,
        'loudness': loudness,
        'tempo': tempo,
        'speechiness': speechiness,
        'acousticness': acousticness,
        'valence': valence,
        'liveness': liveness,
        'key': key,
        'mode': mode,
        'duration_ms': duration_ms,
        'time_signature': time_signature,
        'limit': limit
    }
    
    return query_params

# Button to trigger music generation
if st.button("Generate Music Recommendations"):

  
    # Generate the query based on user input
    query_params = generate_spotify_query()
    
    # Display the generated query parameters
    st.write("Generated Query Parameters:", query_params)
    
    # Fetch recommendations from Spotify
    #(print(st.session_state.get("generated_response")["genres"]))
    
    results = sp.recommendations(seed_genres=genres, **query_params)
    
    # Sort tracks by popularity (descending order)
    tracks = results['tracks']
    sorted_tracks = sorted(tracks, key=lambda x: x['popularity'], reverse=True)  # Sort by popularity
    
    # Display the tracks from Spotify with clickable links and popularity
    if sorted_tracks:
        st.write("### Recommended Tracks (sorted by popularity):")
        for track in sorted_tracks:
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            album_name = track['album']['name']
            spotify_url = track['external_urls']['spotify']  # Get the Spotify URL for the track
            popularity = track['popularity']  # Get the track popularity
            # Display the track with a clickable link and popularity score
            st.markdown(f"- [{track_name} by {artist_name}]({spotify_url}) (Album: {album_name}, Popularity: {popularity})")
    else:
        st.write("No tracks found for this mood.")
