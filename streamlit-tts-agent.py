import streamlit as st
import requests
import json
import base64
from io import BytesIO
import os
import hashlib
import time
from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager
import logging
from typing import Dict, Any, Optional
import secrets

# -------------------------------------------------------
# Configuration & Constants
# -------------------------------------------------------
DB_PATH = "enterprise_ai_agent.db"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Initialize logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Database Setup
# -------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            service_type TEXT NOT NULL,
            input_text TEXT,
            output_text TEXT,
            media_url TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# -------------------------------------------------------
# Session Management
# -------------------------------------------------------
def get_session_id():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = secrets.token_hex(16)
    return st.session_state.session_id

def log_usage(session_id: str, service_type: str, input_text: str, output_text: str, media_url: str = None, ip_address: str = "unknown"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO usage_logs (session_id, service_type, input_text, output_text, media_url, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, service_type, input_text, output_text, media_url, ip_address))
    conn.commit()
    conn.close()

# -------------------------------------------------------
# Simple CSS
# -------------------------------------------------------
st.set_page_config(page_title="AI Agent", layout="wide")

st.markdown("""
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
.main-container {
    max-width: 1200px;
    margin: 0 auto;
}
.card {
    padding: 20px;
    border-radius: 8px;
    background-color: #f8f9fa;
    margin-bottom: 20px;
    border: 1px solid #e0e0e0;
}
.card h3 {
    margin-top: 0;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Initialize session state
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'media_result' not in st.session_state:
    st.session_state.media_result = None
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}

session_id = get_session_id()

# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.title("🤖 AI Content Generator")
st.markdown("Generate AI-enhanced text and convert it to audio or video")

# -------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("API Keys")
    claude_key = st.text_input("Claude API Key", type="password", placeholder="sk-ant-...")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    google_key = st.text_input("Google Gemini Key", type="password", placeholder="AIza...")
    hf_key = st.text_input("HuggingFace Key", type="password", placeholder="hf_...")
    
    st.divider()
    
    st.subheader("TTS Provider")
    tts_choice = st.radio(
        "Select Audio/Video Provider:",
        ["OpenAI TTS", "ElevenLabs", "D-ID Video"]
    )
    
    if tts_choice == "OpenAI TTS":
        tts_key = openai_key
        st.caption("Uses OpenAI API key above")
    elif tts_choice == "ElevenLabs":
        tts_key = st.text_input("ElevenLabs API Key", type="password", key="elevenlabs_key")
    else:
        tts_key = st.text_input("D-ID API Key", type="password", key="did_key")
    
    st.divider()
    
    with st.expander("📚 How to Get Keys"):
        st.markdown("""
- **Claude**: console.anthropic.com
- **OpenAI**: platform.openai.com/api-keys
- **Gemini**: makersuite.google.com/app/apikey
- **HuggingFace**: huggingface.co/settings/tokens
- **ElevenLabs**: elevenlabs.io
- **D-ID**: d-id.com
        """)

# -------------------------------------------------------
# Main Content
# -------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Step 1: Text Generation")
    
    available_models = []
    if claude_key:
        available_models.append("Claude")
    if openai_key:
        available_models.append("OpenAI GPT-4")
    if google_key:
        available_models.append("Gemini")
    if hf_key:
        available_models.append("Llama-2")
    
    if not available_models:
        st.warning("Add at least one LLM API key in sidebar")
        available_models = ["Claude"]
    
    llm_model = st.selectbox("Select Model", available_models)
    enhance_mode = st.selectbox(
        "Enhancement Mode",
        ["improve", "script", "narration", "podcast", "story", "professional", "casual"]
    )

with col2:
    st.subheader("🎵 Step 2: Audio/Video")
    
    st.info(f"Provider: **{tts_choice}**")
    
    voices = {
        "OpenAI TTS": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "ElevenLabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "D-ID Video": ["en-US-JennyNeural", "en-US-GuyNeural"]
    }
    
    voice = st.selectbox("Voice", voices[tts_choice])

st.divider()

# -------------------------------------------------------
# Text Input
# -------------------------------------------------------
st.subheader("✏️ Your Text")
input_text = st.text_area(
    "Enter text or topic:",
    height=150,
    placeholder="e.g., Create a professional introduction about AI technology"
)

st.caption(f"{len(input_text)} characters")

# -------------------------------------------------------
# Enhancement Prompts
# -------------------------------------------------------
enhance_prompts = {
    "improve": "Improve writing and clarity.",
    "script": "Convert this into a video script.",
    "narration": "Rewrite in narrative storytelling style.",
    "podcast": "Rewrite as a podcast intro.",
    "story": "Expand into a fictional story.",
    "professional": "Rewrite formally and professionally.",
    "casual": "Rewrite casually and friendly."
}

# -------------------------------------------------------
# LLM Function
# -------------------------------------------------------
def generate_with_llm(text, model, keys, mode):
    prompt = f"{enhance_prompts[mode]}\n\nOriginal text:\n{text}"
    
    model_key = {
        "Claude": "claude",
        "OpenAI GPT-4": "openai",
        "Gemini": "google",
        "Llama-2": "huggingface"
    }[model]
    
    if model_key == "claude":
        if not keys.get("claude"):
            raise Exception("Claude API key required")
        
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": keys["claude"],
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = r.json()
        if "error" in data:
            raise Exception(f"Claude Error: {data['error'].get('message', 'Unknown')}")
        return data["content"][0]["text"]
    
    elif model_key == "openai":
        if not keys.get("openai"):
            raise Exception("OpenAI API key required")
        
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {keys['openai']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        data = r.json()
        if "error" in data:
            raise Exception(f"OpenAI Error: {data['error']['message']}")
        return data["choices"][0]["message"]["content"]
    
    elif model_key == "google":
        if not keys.get("google"):
            raise Exception("Gemini API key required")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['google']}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        data = r.json()
        if "error" in data:
            raise Exception(f"Gemini Error: {data['error']['message']}")
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    elif model_key == "huggingface":
        if not keys.get("huggingface"):
            raise Exception("HuggingFace key required")
        
        r = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers={"Authorization": f"Bearer {keys['huggingface']}"},
            json={"inputs": prompt},
        )
        data = r.json()
        if isinstance(data, dict) and "error" in data:
            raise Exception(f"HuggingFace Error: {data['error']}")
        return data[0]["generated_text"]

# -------------------------------------------------------
# Media Function
# -------------------------------------------------------
def generate_media(text, provider, voice, keys):
    if provider == "OpenAI TTS":
        api_key = keys.get("openai")
        if not api_key:
            raise Exception("OpenAI API key required")
        
        r = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={"model": "tts-1-hd", "voice": voice, "input": text}
        )
        
        if r.status_code != 200:
            raise Exception(f"OpenAI TTS Error: {r.text}")
        
        return {"type": "audio", "content": r.content}
    
    elif provider == "ElevenLabs":
        if not keys.get("elevenlabs"):
            raise Exception("ElevenLabs API key required")
        
        voices_map = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Drew": "29vD33N1CtxCmqQRPOHJ",
            "Clyde": "2EiwWnXFnvU5JabPnv8n",
            "Paul": "5Q0t7uMcjvnagumLfvZi",
            "Domi": "AZnzlk1XvdvUeBnXmlld",
            "Dave": "CYw3kZ02Hs0563khs1Fj",
        }
        
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voices_map[voice]}",
            headers={"xi-api-key": keys["elevenlabs"]},
            json={"text": text}
        )
        
        if r.status_code != 200:
            raise Exception(f"ElevenLabs Error: {r.text}")
        
        return {"type": "audio", "content": r.content}
    
    elif provider == "D-ID Video":
        if not keys.get("did"):
            raise Exception("D-ID API key required")
        
        did_auth = base64.b64encode(f"{keys['did']}:".encode()).decode()
        
        r = requests.post(
            "https://api.d-id.com/talks",
            headers={
                "Authorization": f"Basic {did_auth}",
                "Content-Type": "application/json"
            },
            json={
                "script": {
                    "type": "text",
                    "input": text,
                    "voice_id": voice,
                    "provider": {"type": "microsoft"}
                },
                "source_url": "https://create-images-results.d-id.com/default-presenter.jpg"
            }
        )
        
        if r.status_code != 201:
            raise Exception(f"D-ID Error: {r.text}")
        
        data = r.json()
        return {"type": "video", "url": data.get("result_url")}

# -------------------------------------------------------
# Generate Button
# -------------------------------------------------------
if st.button("🚀 Generate", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("Please enter some text")
    else:
        keys = {}
        if claude_key:
            keys["claude"] = claude_key
        if openai_key:
            keys["openai"] = openai_key
        if google_key:
            keys["google"] = google_key
        if hf_key:
            keys["huggingface"] = hf_key
        
        if tts_choice == "OpenAI TTS":
            keys["openai"] = openai_key
        elif tts_choice == "ElevenLabs":
            keys["elevenlabs"] = tts_key
        elif tts_choice == "D-ID Video":
            keys["did"] = tts_key
        
        try:
            with st.spinner("Generating enhanced text..."):
                enhanced = generate_with_llm(input_text, llm_model, keys, enhance_mode)
                st.session_state.generated_text = enhanced
            
            st.success("Text enhanced!")
            
            with st.spinner("Converting to audio/video..."):
                media = generate_media(enhanced, tts_choice, voice, keys)
                st.session_state.media_result = media
            
            st.success("Media generated!")
            
            log_usage(session_id, f"{llm_model}+{tts_choice}", input_text, enhanced)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.divider()

# -------------------------------------------------------
# Results
# -------------------------------------------------------
if st.session_state.generated_text:
    st.subheader("📄 Enhanced Text")
    st.text_area("", st.session_state.generated_text, height=150, disabled=True)

if st.session_state.media_result:
    st.subheader("🎵 Generated Media")
    media = st.session_state.media_result
    
    if media["type"] == "audio":
        st.audio(media["content"], format="audio/mp3")
        st.download_button("⬇️ Download Audio", media["content"], "audio.mp3", "audio/mp3")
    elif media["type"] == "video":
        if media.get("url"):
            st.video(media["url"])
        else:
            st.error("No video URL returned")
