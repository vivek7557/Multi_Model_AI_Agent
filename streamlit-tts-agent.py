import streamlit as st
import requests
import base64
import sqlite3
import logging
import secrets

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------
DB_PATH = "enterprise_ai_agent.db"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Database
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

def get_session_id():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = secrets.token_hex(16)
    return st.session_state.session_id

def log_usage(session_id, service_type, input_text, output_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO usage_logs (session_id, service_type, input_text, output_text, ip_address)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, service_type, input_text, output_text, "unknown"))
    conn.commit()
    conn.close()

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(page_title="AI Content Generator", layout="centered", initial_sidebar_state="collapsed")

# -------------------------------------------------------
# Clean CSS
# -------------------------------------------------------
st.markdown("""
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1a1a1a;
}

.stApp {
    background-color: #ffffff;
}

[data-testid="stMainBlockContainer"] {
    padding: 2rem 0;
}

[data-testid="stSidebar"] {
    background-color: #f5f5f5;
    border-right: 1px solid #e0e0e0;
}

/* Headings */
h1, h2, h3 {
    color: #000;
    font-weight: 600;
    margin-bottom: 1rem;
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 2rem 0;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background-color: #f8f8f8 !important;
    border: 1px solid #d0d0d0 !important;
    color: #1a1a1a !important;
    border-radius: 6px !important;
    padding: 12px !important;
    font-size: 14px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: #0066cc !important;
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
}

/* Buttons */
.stButton > button {
    background-color: #0066cc !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 12px 24px !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    cursor: pointer;
    transition: background-color 0.2s;
    width: 100%;
}

.stButton > button:hover {
    background-color: #0052a3 !important;
}

.stDownloadButton > button {
    background-color: #28a745 !important;
    color: white !important;
}

.stDownloadButton > button:hover {
    background-color: #218838 !important;
}

/* Messages */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 6px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
}

.stSuccess {
    background-color: #d4edda !important;
    color: #155724 !important;
    border: 1px solid #c3e6cb !important;
}

.stError {
    background-color: #f8d7da !important;
    color: #721c24 !important;
    border: 1px solid #f5c6cb !important;
}

.stInfo {
    background-color: #d1ecf1 !important;
    color: #0c5460 !important;
    border: 1px solid #bee5eb !important;
}

/* Audio */
audio {
    width: 100%;
    border-radius: 6px;
    margin: 1rem 0;
}

/* Caption */
.stCaption {
    color: #666 !important;
    font-size: 13px !important;
}

/* Spinner */
.stSpinner > div {
    border-color: #0066cc !important;
}

/* Cards */
.card {
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #000;
}

/* Hide streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

</style>
""", unsafe_allow_html=True)

init_db()

# Session state
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'media_result' not in st.session_state:
    st.session_state.media_result = None

session_id = get_session_id()

# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>AI Content Generator</h1>
    <p style="color: #666; font-size: 16px;">Transform text into enhanced content with audio and video</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------
with st.sidebar:
    st.markdown("### API Configuration")
    
    claude_key = st.text_input("Claude API Key", type="password", placeholder="sk-ant-...")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    google_key = st.text_input("Google Gemini", type="password", placeholder="AIza...")
    hf_key = st.text_input("HuggingFace", type="password", placeholder="hf_...")
    
    st.markdown("---")
    
    st.markdown("### Audio/Video Provider")
    tts_choice = st.radio("Select provider:", ["OpenAI TTS", "ElevenLabs", "D-ID Video"], label_visibility="collapsed")
    
    if tts_choice == "ElevenLabs":
        tts_key = st.text_input("ElevenLabs Key", type="password", key="elevenlabs_key", placeholder="Enter key")
    elif tts_choice == "D-ID Video":
        tts_key = st.text_input("D-ID Key", type="password", key="did_key", placeholder="Enter key")
    else:
        tts_key = openai_key

# -------------------------------------------------------
# Main Content
# -------------------------------------------------------

# Model Selection
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card"><div class="card-title">Text Generation</div>', unsafe_allow_html=True)
    
    available_models = []
    if claude_key:
        available_models.append("Claude 3.5")
    if openai_key:
        available_models.append("GPT-4")
    if google_key:
        available_models.append("Gemini")
    if hf_key:
        available_models.append("Llama-2")
    
    if not available_models:
        st.warning("Add API key in sidebar")
        available_models = ["Claude 3.5"]
    
    llm_model = st.selectbox("Model", available_models, label_visibility="collapsed")
    enhance_mode = st.selectbox(
        "Style",
        ["improve", "script", "narration", "podcast", "story", "professional", "casual"],
        format_func=lambda x: {"improve": "Improve", "script": "Script", "narration": "Narration", "podcast": "Podcast", "story": "Story", "professional": "Professional", "casual": "Casual"}[x],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">Audio/Video Generation</div>', unsafe_allow_html=True)
    st.info(f"Provider: {tts_choice}", icon="ℹ️")
    
    voices = {
        "OpenAI TTS": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "ElevenLabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "D-ID Video": ["en-US-JennyNeural", "en-US-GuyNeural"]
    }
    
    voice = st.selectbox("Voice", voices[tts_choice], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Text Input
st.markdown("### Your Content")
input_text = st.text_area(
    "Enter text:",
    height=150,
    placeholder="Write or paste your content here...",
    label_visibility="collapsed"
)
st.caption(f"{len(input_text)} characters")

st.markdown("---")

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
# LLM Generation
# -------------------------------------------------------
def generate_with_llm(text, model, keys, mode):
    prompt = f"{enhance_prompts[mode]}\n\nOriginal text:\n{text}"
    
    model_map = {
        "Claude 3.5": "claude",
        "GPT-4": "openai",
        "Gemini": "google",
        "Llama-2": "huggingface"
    }
    
    model_key = model_map[model]
    
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
            raise Exception(f"Claude: {data['error'].get('message', 'Error')}")
        return data["content"][0]["text"]
    
    elif model_key == "openai":
        if not keys.get("openai"):
            raise Exception("OpenAI API key required")
        
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {keys['openai']}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
        )
        data = r.json()
        if "error" in data:
            raise Exception(f"OpenAI: {data['error']['message']}")
        return data["choices"][0]["message"]["content"]
    
    elif model_key == "google":
        if not keys.get("google"):
            raise Exception("Gemini API key required")
        
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['google']}",
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )
        data = r.json()
        if "error" in data:
            raise Exception(f"Gemini: {data['error']['message']}")
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    elif model_key == "huggingface":
        if not keys.get("huggingface"):
            raise Exception("HuggingFace key required")
        
        r = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers={"Authorization": f"Bearer {keys['huggingface']}"},
            json={"inputs": prompt}
        )
        data = r.json()
        if isinstance(data, dict) and "error" in data:
            raise Exception(f"HuggingFace: {data['error']}")
        return data[0]["generated_text"]

# -------------------------------------------------------
# Media Generation
# -------------------------------------------------------
def generate_media(text, provider, voice, keys):
    if provider == "OpenAI TTS":
        api_key = keys.get("openai")
        if not api_key:
            raise Exception("OpenAI API key required")
        
        r = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "tts-1-hd", "voice": voice, "input": text}
        )
        if r.status_code != 200:
            raise Exception(f"TTS Error: {r.text}")
        return {"type": "audio", "content": r.content}
    
    elif provider == "ElevenLabs":
        if not keys.get("elevenlabs"):
            raise Exception("ElevenLabs API key required")
        
        voice_ids = {"Rachel": "21m00Tcm4TlvDq8ikWAM", "Drew": "29vD33N1CtxCmqQRPOHJ", "Clyde": "2EiwWnXFnvU5JabPnv8n", "Paul": "5Q0t7uMcjvnagumLfvZi", "Domi": "AZnzlk1XvdvUeBnXmlld", "Dave": "CYw3kZ02Hs0563khs1Fj"}
        
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_ids[voice]}",
            headers={"xi-api-key": keys["elevenlabs"]},
            json={"text": text}
        )
        if r.status_code != 200:
            raise Exception(f"ElevenLabs Error: {r.text}")
        return {"type": "audio", "content": r.content}
    
    elif provider == "D-ID Video":
        if not keys.get("did"):
            raise Exception("D-ID API key required")
        
        auth = base64.b64encode(f"{keys['did']}:".encode()).decode()
        r = requests.post(
            "https://api.d-id.com/talks",
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
            json={"script": {"type": "text", "input": text, "voice_id": voice, "provider": {"type": "microsoft"}}, "source_url": "https://create-images-results.d-id.com/default-presenter.jpg"}
        )
        if r.status_code != 201:
            raise Exception(f"D-ID Error: {r.text}")
        return {"type": "video", "url": r.json().get("result_url")}

# -------------------------------------------------------
# Generate Button
# -------------------------------------------------------
if st.button("Generate Content", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("Please enter some content")
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
        if tts_choice == "ElevenLabs":
            keys["elevenlabs"] = tts_key
        elif tts_choice == "D-ID Video":
            keys["did"] = tts_key
        
        try:
            with st.spinner("Generating enhanced text..."):
                enhanced = generate_with_llm(input_text, llm_model, keys, enhance_mode)
                st.session_state.generated_text = enhanced
            st.success("✓ Text enhanced")
            
            with st.spinner("Converting to audio/video..."):
                media = generate_media(enhanced, tts_choice, voice, keys)
                st.session_state.media_result = media
            st.success("✓ Media generated")
            
            log_usage(session_id, f"{llm_model}+{tts_choice}", input_text, enhanced)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")

# -------------------------------------------------------
# Results
# -------------------------------------------------------
if st.session_state.generated_text:
    st.markdown("### Enhanced Text")
    st.text_area("", st.session_state.generated_text, height=150, disabled=True, label_visibility="collapsed")

if st.session_state.media_result:
    st.markdown("### Media Output")
    media = st.session_state.media_result
    
    if media["type"] == "audio":
        st.audio(media["content"], format="audio/mp3")
        st.download_button("⬇ Download Audio", media["content"], "audio.mp3", "audio/mp3", use_container_width=True)
    elif media["type"] == "video":
        if media.get("url"):
            st.video(media["url"])
        else:
            st.error("No video URL returned")
