import streamlit as st
import base64
import requests
import json

# SOUNDRAW API Test Token
soundraw_api_key = "VEVTVF9UT0tFTg=="  # Test token provided

# OpenAI API Key
openai_api_key = st.secrets["OPENAI_API"]  # Replace with your actual OpenAI API key

# Function to encode the image to Base64
def encode_image_to_base64(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to send the image and prompt to the ChatGPT API
def send_to_openai_api(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    link = "https://docs.google.com/document/d/185WjC7T1Rq1-9zKlARobmeFiR3VaJcN1IT4ZwDP03Tg/edit"

    genres = [
    "Acoustic", "Hip Hop", "Beats", "Funk", "Pop", "Drum n Bass", "Trap", 
    "Tokyo night pop", "Rock", "Latin", "House", "Tropical House", "Ambient", 
    "Orchestra", "Electro & Dance", "Electronica", "Techno & Trance", 
    "Jersey Club", "Drill", "R&B", "Lofi Hip Hop", "World", "Afrobeats", "Christmas"
    ]

    themes = [
        "Ads & Trailers", "Broadcasting", "Cinematic", "Corporate", "Comedy", 
        "Cooking", "Documentary", "Drama", "Fashion & Beauty", "Gaming", 
        "Holiday Season", "Horror & Thriller", "Motivational & Inspiring", 
        "Nature", "Photography", "Sports & Action", "Technology", "Travel", 
        "Tutorials", "Vlogs", "Wedding & Romance", "Workout & Wellness"
    ]

    moods = [
        "Angry", "Busy & Frantic", "Dark", "Dreamy", "Elegant", "Epic", "Euphoric", 
        "Fear", "Funny & Weird", "Glamorous", "Happy", "Heavy & Ponderous", "Hopeful", 
        "Laid Back", "Mysterious", "Peaceful", "Restless", "Romantic", "Running", 
        "Sad", "Scary", "Sentimental", "Sexy", "Smooth", "Suspense"
    ]

    
    energy_levels = '''
"energy_levels": [
        {
            "start": 
            "end": 
            "energy": 
        },
        {
            "start": 
            "end": 
            "energy": 
        }
    ]
'''

    # Refined prompt for ChatGPT to generate the required parameters for SOUNDRAW
    prompt = f"""
    Based on this image, generate a payload for creating a music track using the SOUNDRAW API. Refer to this {link}
    The payload should include:
    - Genres: list of less than 5 exsiting genres that matches the image from {genres}
    - Moods: list of less than 5 exsiting genres that matches the image from {moods}
    - Themes: list of less than 5 exsiting genres that matches the image  from {themes}
    Make sure you choose genres from {genres} and moods from {moods} and themes fomr {themes}
    - Energy levels (a JSON structure defining energy levels at various points in the track) follow {energy_levels} this format
    Return the response in JSON format. I only need json as an output. No description.
    """

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
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

    print(response.json()['choices'][0]['message']['content'])

    if response.status_code == 200:
        try:
            response_json = response.json()
            message_content = response_json['choices'][0]['message']['content']
            return json.loads(message_content.replace('json', '', 1).strip()[3:-3])
        except Exception as e:
            return f"Error in parsing response: {e}"
    else:
        return f"Error: {response.status_code}, {response.text}"
    


# Function to send a request to the SOUNDRAW API
def create_music_with_soundraw(moods, genres, themes, length, file_format="m4a", energy_levels=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {soundraw_api_key}"
    }

    # Payload with the parameters for music creation
    payload = {
        "moods": moods,
        "genres": genres,
        "themes": themes,
        "length": length,
        "file_format": file_format,
    }

    if energy_levels:
        payload["energy_levels"] = energy_levels

    # Make a request to the SOUNDRAW API /compose endpoint
    response = requests.post("https://soundraw.io/api/v2/musics/compose", headers=headers, json=payload)

    if response.status_code == 200:
        try:
            response_json = response.json()
            return {
                "m4a_url": response_json.get("m4a_url"),
                "share_link": response_json.get("share_link"),
                "bpm": response_json.get("bpm"),
                "timestamps": response_json.get("timestamps")
            }
        except Exception as e:
            return f"Error in parsing response: {e}"
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit UI
st.title("Generate Music from Image with SOUNDRAW")

# Image uploader for users to upload an image
uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# If an image is uploaded
if uploaded_image:
    # Display the uploaded image
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Encode the image to Base64
    base64_image = encode_image_to_base64(uploaded_image)
    print("succsessfully encoded")

    # Button to trigger the ChatGPT API call
    if st.button("Generate Music Parameters from Image"):
        st.write("Generating music parameters using ChatGPT API...")

        # Send the image and prompt to OpenAI API
        openai_response = send_to_openai_api(base64_image)


        if isinstance(openai_response, dict):
            st.write("Music parameters generated from the image:")
            st.json(openai_response)
            # Store response in session state for further use
            st.session_state['moods'] = openai_response.get('moods', "")
            st.session_state['genres'] = openai_response.get('genres', [])
            st.session_state['themes'] = openai_response.get('themes', "")
            st.session_state['energy_levels'] = openai_response.get('energy_levels', {})
        else:
            st.error(openai_response)

# If parameters (moods, genres, themes, energy_levels) are already generated via ChatGPT API, use them for SOUNDRAW API request
if 'moods' in st.session_state and 'genres' in st.session_state and 'themes' in st.session_state:
    moods = st.session_state['moods']
    genres = st.session_state['genres']
    themes = st.session_state['themes']
    energy_levels = st.session_state['energy_levels']

    print(moods,genres,themes,energy_levels)

    # Generate music using SOUNDRAW API
    if st.button("Generate Music with SOUNDRAW"):
        response = create_music_with_soundraw(
            moods=moods,
            genres=genres,
            themes=themes,
            length=30,  # Default track length; you can modify
            energy_levels=None  # Pass the energy levels generated by ChatGPT
        )

        print("SOUNDRAW API response:", response)

        # Display the generated track
        if isinstance(response, dict):
            st.write("### Generated Music")
            #st.markdown(f"[Download the track here]({response['m4a_url']})")
            st.markdown(f"[View the track on SOUNDRAW's website]({response['share_link']})")
            st.write(f"BPM: {response['bpm']}")
            #st.write("Timestamps and energy levels:")
            #st.write(response["timestamps"])
        else:
            st.error(response)
