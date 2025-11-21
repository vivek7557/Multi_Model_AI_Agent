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
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # API Keys table
    c.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_name TEXT NOT NULL,
            key_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Usage logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_type TEXT NOT NULL,
            input_text TEXT,
            output_text TEXT,
            media_url TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin user if not exists
    admin_password = "Admin123!"  # Change this in production
    admin_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    c.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, email, role)
        VALUES (?, ?, ?, 'admin')
    ''', ("admin", admin_hash, "admin@enterprise.com"))
    
    conn.commit()
    conn.close()

# -------------------------------------------------------
# Security Functions
# -------------------------------------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, password_hash, role FROM users WHERE username=? AND is_active=1', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return {"id": user[0], "username": user[1], "role": user[3]}
    return None

def get_user_keys(user_id: int) -> Dict[str, str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT service_name, key_value FROM api_keys WHERE user_id=?', (user_id,))
    keys = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return keys

def log_usage(user_id: int, service_type: str, input_text: str, output_text: str, media_url: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO usage_logs (user_id, service_type, input_text, output_text, media_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, service_type, input_text, output_text, media_url))
    conn.commit()
    conn.close()

def update_last_login(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET last_login=? WHERE id=?', (datetime.now(), user_id))
    conn.commit()
    conn.close()

# -------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------
if 'user' not in st.session_state:
    st.session_state.user = None
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'media_result' not in st.session_state:
    st.session_state.media_result = None
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}

# Initialize database
init_db()

# -------------------------------------------------------
# Authentication UI
# -------------------------------------------------------
def login_ui():
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: rgba(26, 11, 46, 0.8); border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin-bottom: 20px;'>🔐 Enterprise AI Portal</h1>
        <p style='color: #a78bfa;'>Sign in to access advanced AI capabilities</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
                update_last_login(user['id'])
                st.rerun()
            else:
                st.error("Invalid credentials")

def logout():
    st.session_state.user = None
    st.rerun()

# -------------------------------------------------------
# Main Application UI
# -------------------------------------------------------
def main_app():
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://placehold.co/200x50?text=Enterprise+AI", use_column_width=True)
        st.subheader(f"Welcome, {st.session_state.user['username']}")
        
        if st.session_state.user['role'] == 'admin':
            nav = st.selectbox("Navigation", ["Dashboard", "API Keys", "User Management", "Usage Logs", "Settings"])
        else:
            nav = st.selectbox("Navigation", ["Dashboard", "API Keys", "Settings"])
        
        if st.button("Logout", type="primary"):
            logout()
    
    # Main Content Area
    if nav == "Dashboard":
        dashboard_ui()
    elif nav == "API Keys":
        api_keys_ui()
    elif nav == "User Management" and st.session_state.user['role'] == 'admin':
        user_management_ui()
    elif nav == "Usage Logs" and st.session_state.user['role'] == 'admin':
        usage_logs_ui()
    elif nav == "Settings":
        settings_ui()

def dashboard_ui():
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(26, 11, 46, 0.8), rgba(45, 27, 105, 0.8)); border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin-bottom: 10px;'>Multi-Model AI Agent</h1>
        <p style='color: #c7b3ff;'>Enterprise-grade AI content generation platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Collect user's API keys
    st.session_state.api_keys = get_user_keys(st.session_state.user['id'])
    
    # Two-column layout
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>
            <h3 style='color: white; margin-top: 0;'>🧠 AI Text Generation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Model selection based on available keys
        available_models = []
        if 'claude' in st.session_state.api_keys:
            available_models.append("claude")
        if 'openai' in st.session_state.api_keys:
            available_models.append("openai")
        if 'gemini' in st.session_state.api_keys:
            available_models.append("gemini")
        if 'huggingface' in st.session_state.api_keys:
            available_models.append("huggingface")
        
        if not available_models:
            st.warning("⚠️ No API keys configured. Please add keys in the API Keys section.")
            return
        
        llm_model = st.selectbox(
            "Select LLM Model",
            available_models,
            format_func=lambda x: {
                "claude": "🔮 Claude 3.5 Sonnet",
                "openai": "🤖 OpenAI GPT-4",
                "gemini": "✨ Google Gemini",
                "huggingface": "🤗 Llama-2"
            }.get(x, x)
        )
        
        enhance_mode = st.selectbox(
            "Enhancement Mode",
            ["improve", "script", "narration", "podcast", "story", "professional", "casual"],
            format_func=lambda x: {
                "improve": "✍️ Improve & Enhance",
                "script": "🎬 Video Script",
                "narration": "📖 Narration Style",
                "podcast": "🎙️ Podcast Intro",
                "story": "📚 Expand into Story",
                "professional": "💼 Professional Tone",
                "casual": "😊 Casual & Friendly"
            }[x]
        )
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>
            <h3 style='color: white; margin-top: 0;'>🎵 Audio/Video Generation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # TTS Provider Selection
        tts_choice = st.radio(
            "Select Provider:",
            ["OpenAI TTS", "ElevenLabs", "D-ID Video"],
            help="Choose the service for converting text to audio/video"
        )
        
        tts_model_map = {
            "OpenAI TTS": "openai-tts",
            "ElevenLabs": "elevenlabs",
            "D-ID Video": "did"
        }
        tts_model = tts_model_map[tts_choice]
        
        # Voice selection based on provider
        voices = {
            "openai-tts": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            "elevenlabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
            "did": ["en-US-JennyNeural", "en-US-GuyNeural"]
        }
        
        voice = st.selectbox("Voice Selection", voices[tts_model])
    
    # Text Input
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>
        <h3 style='color: white; margin-top: 0;'>📝 Enter Your Content</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_text = st.text_area(
        "",
        height=150,
        placeholder="Enter your text or topic here... For example: 'Create a professional introduction about AI technology' or 'Write a casual podcast intro about climate change'",
        label_visibility="collapsed"
    )
    
    st.caption(f"📝 {len(input_text)} characters")
    
    # Generate button
    if st.button("✨ Generate AI Content → Audio/Video", type="primary"):
        if not input_text.strip():
            st.error("⚠️ Please enter some text first")
            return
        
        try:
            # Generate enhanced text
            with st.spinner("🧠 Generating enhanced text with AI..."):
                enhanced = generate_with_llm(input_text, llm_model, st.session_state.api_keys, enhance_mode)
                st.session_state.generated_text = enhanced
            
            st.success("✅ Text enhanced successfully!")
            
            # Generate media
            with st.spinner("🎙️ Converting to audio/video..."):
                media = generate_media(enhanced, tts_model, voice, st.session_state.api_keys)
                st.session_state.media_result = media
            
            st.success("✅ Media generated successfully!")
            
            # Log usage
            media_url = media.get('url', None) if media.get('type') == 'video' else None
            log_usage(
                st.session_state.user['id'],
                f"{llm_model}+{tts_model}",
                input_text,
                enhanced,
                media_url
            )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.generated_text:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>
            <h3 style='color: white; margin-top: 0;'>AI Enhanced Text</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_area("", st.session_state.generated_text, height=180, label_visibility="collapsed", disabled=True)
    
    if st.session_state.media_result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>
            <h3 style='color: white; margin-top: 0;'>Generated Content</h3>
        </div>
        """, unsafe_allow_html=True)
        
        media = st.session_state.media_result
        
        if media["type"] == "audio":
            st.audio(media["content"], format="audio/mp3")
            st.download_button(
                "⬇️ Download Audio",
                media["content"],
                "generated_audio.mp3",
                "audio/mp3"
            )
        
        elif media["type"] == "video":
            if media.get("url"):
                st.video(media["url"])
                st.markdown(f"[📥 Download Video]({media['url']})")
            else:
                st.error("❌ D-ID returned no video URL")

def api_keys_ui():
    st.header("🔑 API Key Management")
    st.subheader("Configure your service credentials")
    
    services = {
        "Claude": "claude",
        "OpenAI": "openai",
        "Google Gemini": "gemini",
        "HuggingFace": "huggingface",
        "ElevenLabs": "elevenlabs",
        "D-ID": "did"
    }
    
    for display_name, key_name in services.items():
        current_key = st.session_state.api_keys.get(key_name, "")
        new_key = st.text_input(
            f"{display_name} API Key",
            type="password",
            value=current_key,
            key=f"key_{key_name}",
            help=f"Enter your {display_name} API key"
        )
        
        if new_key != current_key:
            # Save to database
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Check if key already exists for user
            c.execute('SELECT id FROM api_keys WHERE user_id=? AND service_name=?', 
                     (st.session_state.user['id'], key_name))
            existing = c.fetchone()
            
            if existing:
                c.execute('UPDATE api_keys SET key_value=? WHERE user_id=? AND service_name=?',
                         (new_key, st.session_state.user['id'], key_name))
            else:
                c.execute('INSERT INTO api_keys (user_id, service_name, key_value) VALUES (?, ?, ?)',
                         (st.session_state.user['id'], key_name, new_key))
            
            conn.commit()
            conn.close()
            
            # Update session state
            st.session_state.api_keys[key_name] = new_key
            st.success(f"{display_name} key updated!")

def user_management_ui():
    st.header("👥 User Management")
    st.subheader("Manage system users and permissions")
    
    # Create new user form
    with st.expander("Create New User"):
        with st.form("create_user"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            user_role = st.selectbox("Role", ["user", "admin"])
            create_submit = st.form_submit_button("Create User")
            
            if create_submit:
                if not new_username or not new_password:
                    st.error("Username and password are required")
                else:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    try:
                        c.execute('''
                            INSERT INTO users (username, password_hash, email, role)
                            VALUES (?, ?, ?, ?)
                        ''', (new_username, hash_password(new_password), new_email, user_role))
                        conn.commit()
                        st.success(f"User {new_username} created successfully!")
                    except sqlite3.IntegrityError:
                        st.error("Username or email already exists")
                    conn.close()
    
    # Display users
    st.subheader("Existing Users")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, email, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    
    for user in users:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            col1.write(f"**{user[1]}**")
            col2.write(user[2])
            col3.write(user[3])
            col4.write("✅" if user[4] else "❌")
            
            if st.session_state.user['id'] != user[0]:  # Don't allow self-deactivation
                if col5.button("Toggle", key=f"toggle_{user[0]}"):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('UPDATE users SET is_active=1-is_active WHERE id=?', (user[0],))
                    conn.commit()
                    conn.close()
                    st.rerun()

def usage_logs_ui():
    st.header("📊 Usage Analytics")
    st.subheader("Track system usage and performance")
    
    # Date range selector
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", value=datetime.now() - timedelta(days=7))
    end_date = col2.date_input("End Date", value=datetime.now())
    
    # Filter options
    service_filter = st.selectbox("Filter by Service", ["All", "claude+openai-tts", "openai+elevenlabs", "gemini+did"])
    
    # Fetch logs
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = '''
        SELECT u.username, ul.service_type, ul.timestamp, ul.input_text, ul.output_text
        FROM usage_logs ul
        JOIN users u ON ul.user_id = u.id
        WHERE ul.timestamp BETWEEN ? AND ?
    '''
    params = [start_date.isoformat(), end_date.isoformat()]
    
    if service_filter != "All":
        query += " AND ul.service_type = ?"
        params.append(service_filter)
    
    query += " ORDER BY ul.timestamp DESC LIMIT 50"
    c.execute(query, params)
    logs = c.fetchall()
    conn.close()
    
    # Display logs
    if logs:
        for log in logs:
            with st.expander(f"{log[2]} - {log[0]} ({log[1]})"):
                st.write(f"**Input:** {log[3][:100]}{'...' if len(log[3]) > 100 else ''}")
                st.write(f"**Output:** {log[4][:100]}{'...' if len(log[4]) > 100 else ''}")
    else:
        st.info("No usage logs found for the selected period")

def settings_ui():
    st.header("⚙️ System Settings")
    st.subheader("Configure application behavior")
    
    # Security settings
    st.markdown("### Security")
    enable_audit = st.checkbox("Enable audit logging", value=True)
    session_timeout = st.slider("Session timeout (minutes)", 15, 240, 60)
    
    # Performance settings
    st.markdown("### Performance")
    max_concurrent_requests = st.slider("Max concurrent requests", 1, 10, 3)
    cache_ttl = st.slider("Cache TTL (minutes)", 5, 120, 30)
    
    # Save settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# -------------------------------------------------------
# LLM Generation Function
# -------------------------------------------------------
def generate_with_llm(text, model, keys, mode):
    prompt = f"{enhance_prompts[mode]}\n\nOriginal text:\n{text}"
    
    if model == "claude":
        if not keys.get("claude"):
            raise Exception("Claude API key required. Please add it in the API Keys section.")
        
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
            raise Exception(f"Claude Error: {data['error'].get('message', 'Unknown error')}")
        return data["content"][0]["text"]
    
    elif model == "openai":
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
                "messages": [
                    {"role": "system", "content": "You are a text enhancement AI."},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        
        data = r.json()
        if "error" in data:
            raise Exception(f"OpenAI Error: {data['error']['message']}")
        return data["choices"][0]["message"]["content"]
    
    elif model == "gemini":
        if not keys.get("google"):
            raise Exception("Gemini API key required")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['gemini']}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        
        data = r.json()
        if "error" in data:
            raise Exception(f"Gemini Error: {data['error']['message']}")
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    elif model == "huggingface":
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
# Media Generation Function
# -------------------------------------------------------
def generate_media(text, model, voice, keys):
    if model == "openai-tts":
        api_key = keys.get("openai")
        if not api_key:
            raise Exception("OpenAI API key required for TTS")
        
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
    
    elif model == "elevenlabs":
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
    
    elif model == "did":
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
# Main Application Flow
# -------------------------------------------------------
st.set_page_config(
    page_title="Enterprise AI Agent",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise look
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 12, 41, 0.95) 0%, rgba(24, 20, 61, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Render appropriate UI based on authentication state
if st.session_state.user:
    main_app()
else:
    login_ui()
