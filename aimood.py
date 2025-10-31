import os
import numpy as np
import streamlit as st
from deepface import DeepFace
from PIL import Image
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from langchain_groq import ChatGroq

# -------------------------------
# Load API keys from environment
# -------------------------------
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -------------------------------
# Setup clients
# -------------------------------
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0.3)

# -------------------------------
# Helper Functions
# -------------------------------
def detect_emotion_from_image(img):
    arr = np.array(img)
    result = DeepFace.analyze(arr, actions=['emotion'], enforce_detection=False)
    dominant = result[0]['dominant_emotion'].lower()
    scores = result[0]['emotion']
    confidence = scores[dominant]
    return dominant, confidence

def get_genre_from_llm(emotion, user_text):
    prompt = f"""
You are a music mood mapper. Based on the detected emotion and user context,
respond in JSON only with keys: mood_label, genre_query, reason.

Detected emotion: {emotion}
User text/context: "{user_text or 'None'}"
"""
    try:
        response = llm.invoke(prompt)
        if "{" in response.content:
            return eval(response.content)  # simple safe parse for this format
        else:
            return {"mood_label": emotion, "genre_query": emotion, "reason": "Fallback"}
    except Exception as e:
        st.warning(f"LLM error: {e}")
        return {"mood_label": emotion, "genre_query": emotion, "reason": "LLM failed"}

def fetch_spotify_tracks(query, limit=5):
    results = sp.search(q=query, type='track', limit=limit)
    tracks = []
    for t in results['tracks']['items']:
        tracks.append({
            "name": t['name'],
            "artist": t['artists'][0]['name'],
            "url": t['external_urls']['spotify'],
            "preview": t.get('preview_url')
        })
    return tracks

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🎧 AI-Powered Emotion-to-Music Recommender")
st.write("Capture your face or describe how you feel — AI will pick songs for your mood.")

user_text = st.text_input("Optional: Describe your mood or what you want to listen to 🎵")

img_buffer = st.camera_input("Take a selfie")

dominant_emotion = None

if img_buffer is not None:
    img = Image.open(img_buffer)
    st.image(img, caption="Captured Image", use_column_width=True)

    with st.spinner("Analyzing mood..."):
        try:
            dominant_emotion, conf = detect_emotion_from_image(img)
            st.success(f"Detected Emotion: {dominant_emotion.capitalize()} ({conf:.2f} confidence)")
        # Visualize emotion confidence scores
            try:
                result = DeepFace.analyze(np.array(img), actions=['emotion'], enforce_detection=False)
                emotion_scores = result[0]['emotion']
                st.subheader("🧠 Emotion Confidence Breakdown")
                st.bar_chart(emotion_scores)
            except Exception as e:
                st.warning(f"Could not plot emotion chart: {e}")
    
            if conf < 0.55:
                st.warning("Low confidence — considering text input as well.")

            genre_info = get_genre_from_llm(dominant_emotion, user_text)
            st.info(f"**AI Mood:** {genre_info['mood_label'].capitalize()}  \n"
                    f"**Genre:** {genre_info['genre_query']}  \n"
                    f"**Reason:** {genre_info['reason']}")

            tracks = fetch_spotify_tracks(genre_info['genre_query'])
            if tracks:
                st.subheader("🎶 Recommended Tracks")
                for t in tracks:
                    st.write(f"- **{t['name']}** by *{t['artist']}* 👉 [Play on Spotify]({t['url']})")
                    if t["preview"]:
                        st.audio(t["preview"], format="audio/mp3")
            else:
                st.warning("No tracks found — try again.")

        except Exception as e:
            st.error(f"Emotion detection failed: {e}")

# Optional: Use only text if no image provided
elif user_text:
    genre_info = get_genre_from_llm("neutral", user_text)
    st.info(f"**AI Mood:** {genre_info['mood_label'].capitalize()}  \n"
            f"**Genre:** {genre_info['genre_query']}  \n"
            f"**Reason:** {genre_info['reason']}")

    tracks = fetch_spotify_tracks(genre_info['genre_query'])
    if tracks:
        st.subheader("🎶 Recommended Tracks")
        for t in tracks:
            st.write(f"- **{t['name']}** by *{t['artist']}* 👉 [Play on Spotify]({t['url']})")
            if t["preview"]:
                st.audio(t["preview"], format="audio/mp3")
    else:
        st.warning("No tracks found — try again.")
