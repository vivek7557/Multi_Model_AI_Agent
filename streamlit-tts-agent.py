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
st.set_page_config(page_title="AI Content Generator", layout="wide", initial_sidebar_state="expanded")

# -------------------------------------------------------
# Advanced CSS with Colors
# -------------------------------------------------------
st.markdown("""
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1a1a1a;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

[data-testid="stMainBlockContainer"] {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    border-right: 2px solid #e8eef5;
}

.stSidebar .stMarkdown h3 {
    color: #1e3a8a;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* Headings */
h1, h2, h3 {
    color: #0f172a;
    font-weight: 700;
}

h1 {
    font-size: 3rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

h2 {
    color: #1e3a8a;
    font-size: 1.8rem;
    margin-top: 1.5rem;
}

/* Cards */
.card {
    background: white;
    border-left: 4px solid #667eea;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.card-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    color: #1e3a8a;
    display: flex;
    align-items: center;
    gap: 10px;
}

.card-free {
    border-left-color: #10b981;
}

.card-free .card-title {
    color: #059669;
}

.card-paid {
    border-left-color: #f59e0b;
}

.card-paid .card-title {
    color: #b45309;
}

.model-option {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s;
}

.model-option:hover {
    border-color: #667eea;
    background: #ede9fe;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background-color: #ffffff !important;
    border: 2px solid #e2e8f0 !important;
    color: #1a1a1a !important;
    border-radius: 8px !important;
    padding: 14px !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 28px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

.stDownloadButton > button:hover {
    box-shadow: 0 6px 25px rgba(16, 185, 129, 0.6);
}

/* Messages */
.stSuccess {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
    color: #065f46 !important;
    border: 1px solid #6ee7b7 !important;
    border-radius: 8px !important;
    padding: 14px !important;
}

.stError {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
    color: #7f1d1d !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 8px !important;
    padding: 14px !important;
}

.stInfo {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
    color: #0c2d6b !important;
    border: 1px solid #93c5fd !important;
    border-radius: 8px !important;
    padding: 14px !important;
}

.stWarning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
    color: #78350f !important;
    border: 1px solid #fcd34d !important;
    border-radius: 8px !important;
    padding: 14px !important;
}

/* Audio */
audio {
    width: 100%;
    border-radius: 8px;
    margin: 16px 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    margin: 2rem 0;
}

/* Radio buttons */
.stRadio > label {
    font-weight: 600;
    color: #1e3a8a;
}

/* Hide streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Badge */
.badge-free {
    display: inline-block;
    background: #d1fae5;
    color: #065f46;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}

.badge-paid {
    display: inline-block;
    background: #fef3c7;
    color: #78350f;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}

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
<div style="text-align: center; margin-bottom: 3rem; padding: 2rem 0;">
    <h1>✨ AI Content Generator</h1>
    <p style="color: #475569; font-size: 18px; margin-top: 0.5rem;">Transform your text into engaging audio & video content</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # LLM Selection
    st.markdown("#### 🧠 Choose Your AI Model")
    
    llm_choice = st.radio(
        "Select LLM:",
        ["Free Models", "Paid Models"],
        label_visibility="collapsed"
    )
    
    if llm_choice == "Free Models":
        st.markdown('<div class="card card-free"><div class="card-title">🆓 Free LLMs</div></div>', unsafe_allow_html=True)
        
        llm_model = st.radio(
            "Free Options:",
            ["HuggingFace (Llama-2)", "Groq (LLaMA)"],
            label_visibility="collapsed",
            key="free_llm"
        )
        
        if llm_model == "HuggingFace (Llama-2)":
            hf_key = st.text_input("HuggingFace API Key", type="password", placeholder="hf_...", key="hf_key")
            claude_key = openai_key = google_key = ""
        else:  # Groq
            groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="groq_key")
            claude_key = openai_key = google_key = hf_key = ""
    
    else:  # Paid Models
        st.markdown('<div class="card card-paid"><div class="card-title">💎 Paid LLMs</div></div>', unsafe_allow_html=True)
        
        llm_model = st.radio(
            "Paid Options:",
            ["Claude 3.5 Sonnet", "GPT-4o"],
            label_visibility="collapsed",
            key="paid_llm"
        )
        
        if llm_model == "Claude 3.5 Sonnet":
            claude_key = st.text_input("Claude API Key", type="password", placeholder="sk-ant-...", key="claude_key")
            openai_key = google_key = hf_key = ""
        else:  # GPT-4o
            openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="openai_key")
            claude_key = google_key = hf_key = ""
    
    st.divider()
    
    # TTS Selection
    st.markdown("#### 🎵 Audio/Video Provider")
    tts_choice = st.radio(
        "Select provider:",
        ["OpenAI TTS", "ElevenLabs", "D-ID Video"],
        label_visibility="collapsed"
    )
    
    if tts_choice == "OpenAI TTS":
        tts_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="tts_openai")
    elif tts_choice == "ElevenLabs":
        tts_key = st.text_input("ElevenLabs API Key", type="password", placeholder="Enter key", key="elevenlabs_key")
    else:
        tts_key = st.text_input("D-ID API Key", type="password", placeholder="Enter key", key="did_key")
    
    st.divider()
    
    with st.expander("📚 Get API Keys"):
        st.markdown("""
**Free Models:**
- HuggingFace: huggingface.co/settings/tokens
- Groq: console.groq.com

**Paid Models:**
- Claude: console.anthropic.com
- OpenAI: platform.openai.com/api-keys

**Audio/Video:**
- ElevenLabs: elevenlabs.io
- D-ID: d-id.com
        """)

# -------------------------------------------------------
# Main Content
# -------------------------------------------------------

# Model & Enhancement Selection
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">🧠 Text Generation Settings</div>
    </div>
    """, unsafe_allow_html=True)
    
    enhance_mode = st.selectbox(
        "Enhancement Style",
        ["improve", "script", "narration", "podcast", "story", "professional", "casual"],
        format_func=lambda x: {
            "improve": "✍️ Improve & Enhance",
            "script": "🎬 Video Script",
            "narration": "📖 Narration",
            "podcast": "🎙️ Podcast Intro",
            "story": "📚 Story",
            "professional": "💼 Professional",
            "casual": "😊 Casual"
        }[x],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-title">🎵 Audio/Video Settings</div>
    </div>
    """, unsafe_allow_html=True)
    
    voices = {
        "OpenAI TTS": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "ElevenLabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "D-ID Video": ["en-US-JennyNeural", "en-US-GuyNeural"]
    }
    
    voice = st.selectbox("Voice Selection", voices[tts_choice], label_visibility="collapsed")

st.divider()

# Text Input
st.markdown("""
<div class="card">
    <div class="card-title">✏️ Your Content</div>
</div>
""", unsafe_allow_html=True)

input_text = st.text_area(
    "Enter text:",
    height=180,
    placeholder="Write or paste your content here...",
    label_visibility="collapsed"
)
st.caption(f"📝 {len(input_text)} characters")

st.divider()

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
    
    if "Claude" in model:
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
    
    elif "GPT-4o" in model:
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
    
    elif "HuggingFace" in model:
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
    
    elif "Groq" in model:
        if not keys.get("groq"):
            raise Exception("Groq API key required")
        
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {keys['groq']}", "Content-Type": "application/json"},
            json={"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1024}
        )
        data = r.json()
        if "error" in data:
            raise Exception(f"Groq: {data['error']['message']}")
        return data["choices"][0]["message"]["content"]

# -------------------------------------------------------
# Media Generation
# -------------------------------------------------------
def generate_media(text, provider, voice, keys):
    if provider == "OpenAI TTS":
        api_key = keys.get("openai_tts")
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
if st.button("🚀 Generate Content", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("❌ Please enter some content to generate")
    else:
        keys = {}
        if claude_key:
            keys["claude"] = claude_key
        if openai_key:
            keys["openai"] = openai_key
        if 'hf_key' in locals() and hf_key:
            keys["huggingface"] = hf_key
        if 'groq_key' in locals() and groq_key:
            keys["groq"] = groq_key
        if tts_choice == "OpenAI TTS" and openai_key:
            keys["openai_tts"] = openai_key
        elif tts_choice == "ElevenLabs":
            keys["elevenlabs"] = tts_key
        elif tts_choice == "D-ID Video":
            keys["did"] = tts_key
        
        try:
            with st.spinner("🧠 Generating enhanced text..."):
                enhanced = generate_with_llm(input_text, llm_model, keys, enhance_mode)
                st.session_state.generated_text = enhanced
            st.success("✓ Text enhanced successfully!")
            
            with st.spinner("🎵 Converting to audio/video..."):
                media = generate_media(enhanced, tts_choice, voice, keys)
                st.session_state.media_result = media
            st.success("✓ Media generated successfully!")
            
            log_usage(session_id, f"{llm_model}+{tts_choice}", input_text, enhanced)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.divider()

# -------------------------------------------------------
# Results
# -------------------------------------------------------
if st.session_state.generated_text:
    st.markdown("""
    <div class="card">
        <div class="card-title">📄 Enhanced Text</div>
    </div>
    """, unsafe_allow_html=True)
    st.text_area("", st.session_state.generated_text, height=150, disabled=True, label_visibility="collapsed")

if st.session_state.media_result:
    st.markdown("""
    <div class="card">
        <div class="card-title">🎵 Generated Media</div>
    </div>
    """, unsafe_allow_html=True)
    
    media = st.session_state.media_result
    
    if media["type"] == "audio":
        st.audio(media["content"], format="audio/mp3")
        st.download_button("⬇ Download Audio", media["content"], "audio.mp3", "audio/mp3", use_container_width=True)
    elif media["type"] == "video":
        if media.get("url"):
            st.video(media["url"])
            st.markdown(f"[📥 Open Video]({media['url']})", unsafe_allow_html=True)
        else:
            st.error("❌ No video URL returned")
