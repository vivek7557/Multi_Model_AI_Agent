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
# CSS - Modern Sidebar + Main Layout
# -------------------------------------------------------
st.markdown("""
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp {
    background: #ffffff;
}

[data-testid="stMainBlockContainer"] {
    padding: 0;
}

/* SIDEBAR STYLING */
[data-testid="stSidebar"] {
    background: #f8f9fb;
    border-right: 1px solid #e8eef7;
    padding: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0;
}

.sidebar-header {
    padding: 24px 20px;
    border-bottom: 1px solid #e8eef7;
}

.sidebar-header h2 {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #1a1a1a;
}

.sidebar-header p {
    margin: 4px 0 0 0;
    font-size: 12px;
    color: #999;
}

/* Sidebar Sections */
.sidebar-section {
    padding: 20px;
    border-bottom: 1px solid #f0f0f0;
}

.sidebar-section-title {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: #666;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.sidebar-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #333;
    transition: all 0.2s;
    border: 1px solid transparent;
}

.sidebar-item:hover {
    background: #f0f0f0;
    border-color: #e0e0e0;
}

.sidebar-item.active {
    background: #ede9fe;
    color: #667eea;
    border-color: #d8d3fc;
    font-weight: 600;
}

.sidebar-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

/* MAIN CONTENT */
[data-testid="stMainBlockContainer"] {
    padding: 40px 60px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fb 100%);
    min-height: 100vh;
}

.page-header {
    margin-bottom: 40px;
}

.page-title {
    font-size: 32px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.page-subtitle {
    font-size: 14px;
    color: #999;
    margin: 0;
}

/* Two Column Grid */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    margin-bottom: 32px;
}

.card-section {
    background: white;
    border: 1px solid #e8eef7;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    transition: all 0.3s;
}

.card-section:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    border-color: #d8d3fc;
}

.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-icon {
    font-size: 18px;
}

/* Input Styles */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background-color: #f8f9fb !important;
    border: 1px solid #e8eef7 !important;
    color: #1a1a1a !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: #667eea !important;
    background-color: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.08) !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 28px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer;
    width: 100%;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Messages */
.stSuccess {
    background: #f0fdf4 !important;
    color: #166534 !important;
    border: 1px solid #dcfce7 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

.stError {
    background: #fef2f2 !important;
    color: #991b1b !important;
    border: 1px solid #fee2e2 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

.stInfo {
    background: #eff6ff !important;
    color: #0c2d6b !important;
    border: 1px solid #dbeafe !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #e8eef7;
    margin: 24px 0;
}

/* Audio */
audio {
    width: 100%;
    border-radius: 8px;
    margin: 16px 0;
}

/* Text Area */
.stTextArea > div > div > textarea {
    min-height: 200px !important;
}

/* Hide Streamlit UI */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Responsive */
@media (max-width: 1024px) {
    .content-grid {
        grid-template-columns: 1fr;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 24px 30px;
    }
}

</style>
""", unsafe_allow_html=True)

init_db()

if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'media_result' not in st.session_state:
    st.session_state.media_result = None
if 'selected_llm' not in st.session_state:
    st.session_state.selected_llm = "Claude 3.5 Sonnet"
if 'selected_tts' not in st.session_state:
    st.session_state.selected_tts = "OpenAI TTS"

session_id = get_session_id()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    # Header
    st.markdown("""
    <div class="sidebar-header">
        <h2>🤖 AI Generator</h2>
        <p>Community Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    # LLM Models
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-section-title">📝 Text Generation</div>
    </div>
    """, unsafe_allow_html=True)
    
    llm_models = {
        "Free": {
            "HuggingFace (Llama-2)": {"key": "hf", "icon": "🦙"},
            "Groq (LLaMA)": {"key": "groq", "icon": "⚡"}
        },
        "Paid": {
            "Claude 3.5 Sonnet": {"key": "claude", "icon": "🔮"},
            "GPT-4o": {"key": "openai", "icon": "🤖"}
        }
    }
    
    selected_llm = ""
    for category, models in llm_models.items():
        for model_name, model_info in models.items():
            active = model_name == st.session_state.selected_llm
            css_class = "active" if active else ""
            
            st.markdown(f"""
            <div class="sidebar-item {css_class}" onclick="alert('{model_name}')">
                <span class="sidebar-icon">{model_info['icon']}</span>
                <span>{model_name}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(model_name, key=f"llm_{model_name}", use_container_width=True):
                st.session_state.selected_llm = model_name
    
    st.markdown('<div style="margin: 12px 0;"></div>', unsafe_allow_html=True)
    
    # TTS Providers
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-section-title">🎵 Audio/Video</div>
    </div>
    """, unsafe_allow_html=True)
    
    tts_models = {
        "OpenAI TTS": {"icon": "🔊"},
        "ElevenLabs": {"icon": "🎙️"},
        "D-ID Video": {"icon": "🎬"}
    }
    
    for tts_name, tts_info in tts_models.items():
        active = tts_name == st.session_state.selected_tts
        
        if st.button(tts_name, key=f"tts_{tts_name}", use_container_width=True):
            st.session_state.selected_tts = tts_name
    
    st.markdown("---")
    
    # API Keys Section
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-section-title">🔑 API Keys</div>
    </div>
    """, unsafe_allow_html=True)
    
    claude_key = st.text_input("Claude", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    openai_key = st.text_input("OpenAI", type="password", placeholder="sk-...", label_visibility="collapsed")
    hf_key = st.text_input("HuggingFace", type="password", placeholder="hf_...", label_visibility="collapsed")
    groq_key = st.text_input("Groq", type="password", placeholder="gsk_...", label_visibility="collapsed")
    tts_key = st.text_input("TTS Key", type="password", placeholder="Enter key", label_visibility="collapsed")
    
    st.markdown("---")
    
    with st.expander("📚 Help"):
        st.markdown("""
**Get API Keys:**
- Claude: console.anthropic.com
- OpenAI: platform.openai.com
- HuggingFace: huggingface.co/settings/tokens
- Groq: console.groq.com
- ElevenLabs: elevenlabs.io
- D-ID: d-id.com
        """)

# -------------------------------------------------------
# MAIN CONTENT
# -------------------------------------------------------

# Header
st.markdown("""
<div class="page-header">
    <h1 class="page-title">✨ AI Content Generator</h1>
    <p class="page-subtitle">Transform text into engaging audio & video content</p>
</div>
""", unsafe_allow_html=True)

# Two Column Layout
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="card-section">
        <div class="section-title">
            <span class="section-icon">🧠</span>
            Text Generation
        </div>
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
    <div class="card-section">
        <div class="section-title">
            <span class="section-icon">🎵</span>
            Audio/Video Settings
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    voices = {
        "OpenAI TTS": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "ElevenLabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "D-ID Video": ["en-US-JennyNeural", "en-US-GuyNeural"]
    }
    
    voice = st.selectbox(
        "Voice Selection",
        voices.get(st.session_state.selected_tts, voices["OpenAI TTS"]),
        label_visibility="collapsed"
    )

st.markdown("---")

# Text Input
st.markdown("""
<div class="card-section">
    <div class="section-title">
        <span class="section-icon">✏️</span>
        Your Content
    </div>
</div>
""", unsafe_allow_html=True)

input_text = st.text_area(
    "Enter text:",
    height=200,
    placeholder="Write or paste your content here...",
    label_visibility="collapsed"
)

st.caption(f"📝 {len(input_text)} characters")

st.markdown("---")

# Enhancement Prompts
enhance_prompts = {
    "improve": "Improve writing and clarity.",
    "script": "Convert this into a video script.",
    "narration": "Rewrite in narrative storytelling style.",
    "podcast": "Rewrite as a podcast intro.",
    "story": "Expand into a fictional story.",
    "professional": "Rewrite formally and professionally.",
    "casual": "Rewrite casually and friendly."
}

# LLM Generation
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

# Media Generation
def generate_media(text, provider, voice, keys):
    if provider == "OpenAI TTS":
        api_key = keys.get("openai") or keys.get("tts_key")
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
        if not keys.get("tts_key"):
            raise Exception("ElevenLabs API key required")
        
        voice_ids = {"Rachel": "21m00Tcm4TlvDq8ikWAM", "Drew": "29vD33N1CtxCmqQRPOHJ", "Clyde": "2EiwWnXFnvU5JabPnv8n", "Paul": "5Q0t7uMcjvnagumLfvZi", "Domi": "AZnzlk1XvdvUeBnXmlld", "Dave": "CYw3kZ02Hs0563khs1Fj"}
        
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_ids[voice]}",
            headers={"xi-api-key": keys["tts_key"]},
            json={"text": text}
        )
        if r.status_code != 200:
            raise Exception(f"ElevenLabs Error: {r.text}")
        return {"type": "audio", "content": r.content}
    
    elif provider == "D-ID Video":
        if not keys.get("tts_key"):
            raise Exception("D-ID API key required")
        
        auth = base64.b64encode(f"{keys['tts_key']}:".encode()).decode()
        r = requests.post(
            "https://api.d-id.com/talks",
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
            json={"script": {"type": "text", "input": text, "voice_id": voice, "provider": {"type": "microsoft"}}, "source_url": "https://create-images-results.d-id.com/default-presenter.jpg"}
        )
        if r.status_code != 201:
            raise Exception(f"D-ID Error: {r.text}")
        return {"type": "video", "url": r.json().get("result_url")}

# Generate Button
if st.button("🚀 Generate Content", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("❌ Please enter some content")
    else:
        keys = {}
        if claude_key:
            keys["claude"] = claude_key
        if openai_key:
            keys["openai"] = openai_key
        if hf_key:
            keys["huggingface"] = hf_key
        if groq_key:
            keys["groq"] = groq_key
        if tts_key:
            keys["tts_key"] = tts_key
        
        try:
            with st.spinner("🧠 Generating enhanced text..."):
                enhanced = generate_with_llm(input_text, st.session_state.selected_llm, keys, enhance_mode)
                st.session_state.generated_text = enhanced
            st.success("✓ Text enhanced!")
            
            with st.spinner("🎵 Converting to audio/video..."):
                media = generate_media(enhanced, st.session_state.selected_tts, voice, keys)
                st.session_state.media_result = media
            st.success("✓ Media generated!")
            
            log_usage(session_id, f"{st.session_state.selected_llm}+{st.session_state.selected_tts}", input_text, enhanced)
            
        except Exception as e:
            st.error(f"❌ {str(e)}")

st.markdown("---")

# Results
if st.session_state.generated_text:
    st.markdown("""
    <div class="card-section">
        <div class="section-title">
            <span class="section-icon">📄</span>
            Enhanced Text
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.text_area("", st.session_state.generated_text, height=150, disabled=True, label_visibility="collapsed")

if st.session_state.media_result:
    st.markdown("""
    <div class="card-section">
        <div class="section-title">
            <span class="section-icon">🎵</span>
            Generated Media
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    media = st.session_state.media_result
    
    if media["type"] == "audio":
        st.audio(media["content"], format="audio/mp3")
        st.download_button("⬇ Download Audio", media["content"], "audio.mp3", "audio/mp3", use_container_width=True)
    elif media["type"] == "video":
        if media.get("url"):
            st.video(media["url"])
        else:
            st.error("❌ No video URL returned")
