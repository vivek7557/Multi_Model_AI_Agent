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
# Database Setup (for usage tracking only)
# -------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Usage logs (no user authentication needed)
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
# Enhanced Custom CSS with Modern Enterprise Design
# -------------------------------------------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Background with Gradient Animation */
    .stApp {
        background: linear-gradient(-45deg, #1a0b2e, #2d1b69, #6b2d5c, #1a0b2e);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .header-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 36px;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .main-title {
        color: #ffffff;
        font-size: 42px;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        color: #c7b3ff;
        font-size: 16px;
        margin-top: 8px;
    }
    
    /* Card Styles */
    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 28px;
        border: 1px solid rgba(255,255,255,0.18);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        border-color: rgba(255,255,255,0.3);
    }
    
    .step-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.15);
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
    }
    
    .step-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .section-title {
        color: #ffffff;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-icon {
        display: inline-block;
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 8px;
        text-align: center;
        line-height: 32px;
        font-size: 18px;
    }
    
    /* Input Styles */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        background: rgba(255,255,255,0.12) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(26, 11, 46, 0.95) 0%, rgba(45, 27, 105, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(255,255,255,0.06) !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%) !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 8px !important;
        color: #d1fae5 !important;
        backdrop-filter: blur(10px);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 8px !important;
        color: #fecaca !important;
        backdrop-filter: blur(10px);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.2) 100%) !important;
        border-left: 4px solid #fbbf24 !important;
        border-radius: 8px !important;
        color: #fef3c7 !important;
        backdrop-filter: blur(10px);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 30px 0 !important;
    }
    
    /* Audio Player */
    audio {
        width: 100%;
        border-radius: 10px;
        background: rgba(255,255,255,0.05);
    }
    
    /* Caption Text */
    .stCaption {
        color: #a78bfa !important;
        font-size: 13px !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #a78bfa;
        font-size: 14px;
        padding: 30px;
        margin-top: 50px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* Selectbox Dropdown */
    [data-baseweb="select"] {
        background: rgba(255,255,255,0.08) !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 28px;
        }
        .header-icon {
            width: 48px;
            height: 48px;
            font-size: 28px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# -------------------------------------------------------
# Initialize Session State
# -------------------------------------------------------
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'media_result' not in st.session_state:
    st.session_state.media_result = None
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}

# Get session ID for usage tracking
session_id = get_session_id()

# -------------------------------------------------------
# Sidebar API Keys - Enhanced Design
# -------------------------------------------------------
with st.sidebar:
    # Sidebar Header
    st.markdown("""
    <div style='text-align: center; padding: 20px 0 30px 0; border-bottom: 1px solid rgba(255,255,255,0.1);'>
        <div style='font-size: 40px; margin-bottom: 10px;'>🔑</div>
        <h2 style='color: white; margin: 0; font-size: 24px; font-weight: 700;'>API Configuration</h2>
        <p style='color: #a78bfa; font-size: 12px; margin-top: 8px;'>Enter only the keys you need</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Required Section - Claude
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(168, 85, 247, 0.15)); 
                padding: 16px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3); margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 12px;'>
            <span style='font-size: 20px;'>⚡</span>
            <span style='color: white; font-weight: 600; font-size: 15px;'>Required: Text Generation</span>
        </div>
        <div style='color: #c7b3ff; font-size: 11px; line-height: 1.5;'>
            Enter your Claude API key to enable AI text generation
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    claude_key = st.text_input(
        "Claude API Key (Anthropic)",
        type="password",
        key="claude_key",
        placeholder="sk-ant-api03-...",
        help="Get your key from console.anthropic.com"
    )
    
    if claude_key:
        st.markdown("""
        <div style='background: rgba(16, 185, 129, 0.15); padding: 10px; border-radius: 8px; 
                    border-left: 3px solid #10b981; margin-top: 8px;'>
            <div style='color: #6ee7b7; font-size: 12px; display: flex; align-items: center; gap: 6px;'>
                <span>✓</span> Claude API key configured
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    # Optional Models Expander
    with st.expander("🔧 Optional: Additional LLM Models", expanded=False):
        st.markdown("""
        <div style='color: #a78bfa; font-size: 11px; margin-bottom: 15px; line-height: 1.5;'>
            Add more AI models for variety. These are completely optional.
        </div>
        """, unsafe_allow_html=True)
        
        openai_key = st.text_input(
            "OpenAI GPT-4",
            type="password",
            key="openai_key",
            placeholder="sk-...",
            help="For GPT-4 text generation"
        )
        
        google_key = st.text_input(
            "Google Gemini",
            type="password",
            key="google_key",
            placeholder="AIza...",
            help="For Gemini text generation"
        )
        
        hf_key = st.text_input(
            "HuggingFace",
            type="password",
            key="hf_key",
            placeholder="hf_...",
            help="For Llama-2 text generation"
        )
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='border-top: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # Audio/Video Section
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(239, 68, 68, 0.15)); 
                padding: 16px; border-radius: 12px; border: 1px solid rgba(236, 72, 153, 0.3); margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 12px;'>
            <span style='font-size: 20px;'>🎵</span>
            <span style='color: white; font-weight: 600; font-size: 15px;'>Audio/Video Generation</span>
        </div>
        <div style='color: #fbbf24; font-size: 11px; line-height: 1.5;'>
            Choose your preferred TTS provider
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TTS Provider Selection with custom styling
    tts_choice = st.radio(
        "Select Provider:",
        ["OpenAI TTS (Recommended)", "ElevenLabs", "D-ID Video"],
        help="Choose the service for converting text to audio/video",
        label_visibility="visible"
    )
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Show appropriate key input based on selection
    if tts_choice == "OpenAI TTS (Recommended)":
        if openai_key:
            openai_tts_key = openai_key
            st.markdown("""
            <div style='background: rgba(16, 185, 129, 0.15); padding: 12px; border-radius: 8px; 
                        border-left: 3px solid #10b981; margin-bottom: 15px;'>
                <div style='color: #6ee7b7; font-size: 12px; display: flex; align-items: center; gap: 6px;'>
                    <span>✓</span> Reusing OpenAI key from above
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); padding: 10px; border-radius: 8px; 
                        margin-bottom: 12px; border-left: 3px solid #3b82f6;'>
                <div style='color: #93c5fd; font-size: 11px;'>
                    ℹ️ Need OpenAI key for TTS
                </div>
            </div>
            """, unsafe_allow_html=True)
            openai_tts_key = st.text_input(
                "OpenAI API Key",
                type="password",
                key="openai_tts_key",
                placeholder="sk-...",
                help="Same as OpenAI GPT-4 key"
            )
    
    elif tts_choice == "ElevenLabs":
        st.markdown("""
        <div style='background: rgba(59, 130, 246, 0.1); padding: 10px; border-radius: 8px; 
                    margin-bottom: 12px; border-left: 3px solid #3b82f6;'>
            <div style='color: #93c5fd; font-size: 11px;'>
                ℹ️ Professional voice synthesis
            </div>
        </div>
        """, unsafe_allow_html=True)
        elevenlabs_key = st.text_input(
            "ElevenLabs API Key",
            type="password",
            key="elevenlabs_key",
            placeholder="Enter your ElevenLabs key",
            help="Get from elevenlabs.io"
        )
    
    else:  # D-ID Video
        st.markdown("""
        <div style='background: rgba(59, 130, 246, 0.1); padding: 10px; border-radius: 8px; 
                    margin-bottom: 12px; border-left: 3px solid #3b82f6;'>
            <div style='color: #93c5fd; font-size: 11px;'>
                ℹ️ AI avatar video generation
            </div>
        </div>
        """, unsafe_allow_html=True)
        did_key = st.text_input(
            "D-ID API Key",
            type="password",
            key="did_key",
            placeholder="Enter your D-ID key",
            help="Get from d-id.com"
        )
    
    # Help Section
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    with st.expander("📚 How to Get API Keys", expanded=False):
        st.markdown("""
        <div style='font-size: 12px; color: #c7b3ff; line-height: 1.8;'>
            <div style='margin-bottom: 12px;'>
                <div style='color: #8b5cf6; font-weight: 600; margin-bottom: 6px;'>🔮 Claude (Primary)</div>
                1. Visit <a href='https://console.anthropic.com' target='_blank' style='color: #a78bfa;'>console.anthropic.com</a><br>
                2. Sign up / Log in<br>
                3. Go to API Keys section<br>
                4. Create new key
            </div>
            
            <div style='margin-bottom: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);'>
                <div style='color: #10b981; font-weight: 600; margin-bottom: 6px;'>🤖 OpenAI</div>
                Visit <a href='https://platform.openai.com/api-keys' target='_blank' style='color: #a78bfa;'>platform.openai.com</a>
            </div>
            
            <div style='margin-bottom: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);'>
                <div style='color: #f59e0b; font-weight: 600; margin-bottom: 6px;'>✨ Gemini</div>
                Visit <a href='https://makersuite.google.com/app/apikey' target='_blank' style='color: #a78bfa;'>makersuite.google.com</a>
            </div>
            
            <div style='margin-bottom: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);'>
                <div style='color: #ec4899; font-weight: 600; margin-bottom: 6px;'>🔊 ElevenLabs</div>
                Visit <a href='https://elevenlabs.io' target='_blank' style='color: #a78bfa;'>elevenlabs.io</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats/Info at bottom
    st.markdown("""
    <div style='margin-top: 30px; padding: 15px; background: rgba(255,255,255,0.03); 
                border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);'>
        <div style='color: #6ee7b7; font-size: 11px; font-weight: 600; margin-bottom: 8px;'>
            💡 Quick Tips
        </div>
        <div style='color: #a78bfa; font-size: 10px; line-height: 1.6;'>
            • Keys are stored in browser only<br>
            • Start with Claude + OpenAI TTS<br>
            • Add more models as needed<br>
            • All data is secure & private
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------
# Main Header
# -------------------------------------------------------
st.markdown("""
<div class='main-header'>
    <div style='display: flex; align-items: center; gap: 20px;'>
        <div class='header-icon'>🎙️</div>
        <div>
            <h1 class='main-title'>Enterprise AI Agent</h1>
            <p class='subtitle'>Powered by Claude AI → Convert to Audio/Video</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Two-Column Layout for Steps
# -------------------------------------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class='step-card'>
        <div class='section-title'>
            <span class='section-icon'>🧠</span>
            Step 1: AI Text Generation
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Determine available models based on API keys
    available_models = []
    if claude_key:
        available_models.append("claude")
    if openai_key:
        available_models.append("openai")
    if google_key:
        available_models.append("gemini")
    if hf_key:
        available_models.append("huggingface")
    
    # Default to claude if available
    if not available_models:
        st.warning("⚠️ Please enter at least one LLM API key in the sidebar")
        available_models = ["claude"]  # Show option even if no key
    
    llm_model = st.selectbox(
        "Select LLM Model",
        available_models,
        format_func=lambda x: {
            "claude": "🔮 Claude 3.5 Sonnet (Recommended)",
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
    <div class='step-card'>
        <div class='section-title'>
            <span class='section-icon'>🎵</span>
            Step 2: Audio/Video Generation
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Map radio choice to model name
    tts_model_map = {
        "OpenAI TTS (Recommended)": "openai-tts",
        "ElevenLabs": "elevenlabs",
        "D-ID Video": "did"
    }
    tts_model = tts_model_map[tts_choice]
    
    st.info(f"📌 Using: **{tts_choice}**")
    
    voices = {
        "openai-tts": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "elevenlabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "did": ["en-US-JennyNeural", "en-US-GuyNeural"]
    }
    
    voice = st.selectbox("Voice Selection", voices[tts_model])

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------
# Text Input Section
# -------------------------------------------------------
st.markdown("""
<div class='glass-card'>
    <div class='section-title'>
        <span class='section-icon'>✏️</span>
        Enter Your Text
    </div>
</div>
""", unsafe_allow_html=True)

input_text = st.text_area(
    "",
    height=150,
    placeholder="Enter your text or topic here... For example: 'Create a professional introduction about AI technology' or 'Write a casual podcast intro about climate change'",
    label_visibility="collapsed"
)

st.caption(f"📝 {len(input_text)} characters")

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
# LLM Generation Function
# -------------------------------------------------------
def generate_with_llm(text, model, keys, mode):
    prompt = f"{enhance_prompts[mode]}\n\nOriginal text:\n{text}"
    
    if model == "claude":
        if not keys.get("claude"):
            raise Exception("Claude API key required. Please add it in the sidebar.")
        
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
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['google']}"
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
        api_key = keys.get("openai") or keys.get("openai_tts")
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
# Generate Button
# -------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("✨ Generate AI Content → Audio/Video"):
    if not input_text.strip():
        st.error("⚠️ Please enter some text first")
    else:
        # Collect only provided API keys
        keys = {}
        if claude_key:
            keys["claude"] = claude_key
        if openai_key:
            keys["openai"] = openai_key
        if google_key:
            keys["google"] = google_key
        if hf_key:
            keys["huggingface"] = hf_key
        
        # Add TTS keys
        if tts_model == "openai-tts":
            if 'openai_tts_key' in locals():
                keys["openai_tts"] = openai_tts_key
        elif tts_model == "elevenlabs" and 'elevenlabs_key' in locals():
            keys["elevenlabs"] = elevenlabs_key
        elif tts_model == "did" and 'did_key' in locals():
            keys["did"] = did_key
        
        try:
            # Step 1: Generate Enhanced Text
            with st.spinner("🧠 Generating enhanced text with AI..."):
                enhanced = generate_with_llm(input_text, llm_model, keys, enhance_mode)
                st.session_state.generated_text = enhanced
            
            st.success("✅ Text enhanced successfully!")
            
            # Step 2: Generate Media
            with st.spinner("🎙️ Converting to audio/video..."):
                media = generate_media(enhanced, tts_model, voice, keys)
                st.session_state.media_result = media
            
            st.success("✅ Media generated successfully!")
            
            # Log usage (anonymous)
            media_url = media.get('url', None) if media.get('type') == 'video' else None
            log_usage(session_id, f"{llm_model}+{tts_model}", input_text, enhanced, media_url)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# -------------------------------------------------------
# Display Results
# -------------------------------------------------------
if st.session_state.generated_text:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card'>
        <div class='section-title'>
            <span class='section-icon'>🧠</span>
            AI Enhanced Text
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.text_area("", st.session_state.generated_text, height=180, label_visibility="collapsed", disabled=True)

if st.session_state.media_result:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card'>
        <div class='section-title'>
            <span class='section-icon'>🎵</span>
            Generated Content
        </div>
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

# -------------------------------------------------------
# Footer
# -------------------------------------------------------
st.markdown("""
<div class='footer'>
    <div style='font-weight: 600; font-size: 16px; margin-bottom: 8px;'>🚀 Enterprise AI Agent</div>
    <div>Built with ❤️ for enterprise use • Powered by Claude AI</div>
    <div style='margin-top: 12px; font-size: 12px; opacity: 0.7;'>
        Claude • OpenAI • Gemini • ElevenLabs • D-ID
    </div>
</div>
""", unsafe_allow_html=True)
