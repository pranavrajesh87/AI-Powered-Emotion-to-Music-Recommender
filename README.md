🎧 AI-Powered Mood-to-Music Recommender

An AI-based web app that detects your mood using facial emotion recognition and text sentiment analysis, then recommends matching Spotify tracks in real time. Built with DeepFace, ChatGroq (Llama-3), and Streamlit — all running locally with zero cloud dependency for mood logic.

🚀 Features

🧠 Detects emotions from live camera feed using DeepFace

💬 Understands user’s text input to interpret mood context

🎵 Fetches real-time Spotify music recommendations

🤖 Uses ChatGroq (Llama-3) for smart mood-to-genre mapping

🔒 Local AI emotion analysis — no third-party cloud calls

⚙️ How It Works

User clicks a selfie or types how they feel.

DeepFace analyzes facial expressions → detects emotion.

ChatGroq refines mood & suggests a music genre.

Spotify API fetches top matching songs.

🧩 Tech Stack

Python

DeepFace – Emotion recognition

ChatGroq (Llama-3) – NLP mood mapping

Streamlit – Frontend web app

Spotipy (Spotify API) – Song search

pip install streamlit deepface spotipy langchain_groq pillow
streamlit run aimood.py

#Before running, set your environment variables:

SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
GROQ_API_KEY=your_key
