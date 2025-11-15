import streamlit as st
import requests
import json
import base64
from io import BytesIO

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------
st.set_page_config(
    page_title="Multi-Model AI Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# Enhanced Custom CSS with Modern Design
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

# -------------------------------------------------------
# Initialize Session State
# -------------------------------------------------------
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'media_result' not in st.session_state:
    st.session_state.media_result = None

# -------------------------------------------------------
# Sidebar API Keys
# -------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>🔑 API Configuration</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='color: #a78bfa; font-size: 13px; margin-bottom: 15px;'>Enter your API keys to enable AI models</div>", unsafe_allow_html=True)
    
    st.markdown("**LLM Models**")
    openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key")
    anthropic_key = st.text_input("Claude API Key", type="password", key="anthropic_key")
    google_key = st.text_input("Google Gemini API Key", type="password", key="google_key")
    hf_key = st.text_input("HuggingFace API Key", type="password", key="hf_key")
    
    st.markdown("---")
    
    st.markdown("**Audio/Video Models**")
    elevenlabs_key = st.text_input("ElevenLabs API Key", type="password", key="elevenlabs_key")
    did_key = st.text_input("D-ID API Key", type="password", key="did_key")
    
    st.markdown("---")
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px;'>
        <div style='color: #fbbf24; font-weight: 600; margin-bottom: 8px;'>📚 Get API Keys:</div>
        <div style='font-size: 12px; color: #c7b3ff; line-height: 1.6;'>
            • <a href='https://platform.openai.com' target='_blank' style='color: #a78bfa;'>OpenAI</a><br>
            • <a href='https://console.anthropic.com' target='_blank' style='color: #a78bfa;'>Claude</a><br>
            • <a href='https://makersuite.google.com' target='_blank' style='color: #a78bfa;'>Gemini</a><br>
            • <a href='https://huggingface.co' target='_blank' style='color: #a78bfa;'>HuggingFace</a><br>
            • <a href='https://elevenlabs.io' target='_blank' style='color: #a78bfa;'>ElevenLabs</a><br>
            • <a href='https://d-id.com' target='_blank' style='color: #a78bfa;'>D-ID</a>
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
            <h1 class='main-title'>Multi-Model AI Agent</h1>
            <p class='subtitle'>Generate & Enhance Text → Convert to Audio/Video with Multiple AI Models</p>
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
    
    llm_model = st.selectbox(
        "Select LLM Model",
        ["openai", "claude", "gemini", "huggingface"],
        format_func=lambda x: {
            "openai": "🤖 OpenAI GPT-4",
            "claude": "🔮 Claude 3.5 Sonnet",
            "gemini": "✨ Google Gemini",
            "huggingface": "🤗 Llama-2 (HuggingFace)"
        }[x]
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
    
    tts_model = st.selectbox(
        "Select Output Model",
        ["openai-tts", "elevenlabs", "did"],
        format_func=lambda x: {
            "openai-tts": "🎵 OpenAI TTS",
            "elevenlabs": "🔊 ElevenLabs",
            "did": "🎥 D-ID Video"
        }[x]
    )
    
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
    
    if model == "openai":
        if not keys["openai"]:
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
        if "choices" not in data or len(data["choices"]) == 0:
            raise Exception("OpenAI returned no output.")
        return data["choices"][0]["message"]["content"]
    
    elif model == "claude":
        if not keys["anthropic"]:
            raise Exception("Claude API key required")
        
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": keys["anthropic"],
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        data = r.json()
        if "error" in data:
            raise Exception(data["error"]["message"])
        return data["content"][0]["text"]
    
    elif model == "gemini":
        if not keys["google"]:
            raise Exception("Gemini API key required")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['google']}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        
        data = r.json()
        if "error" in data:
            raise Exception(data["error"]["message"])
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    elif model == "huggingface":
        if not keys["huggingface"]:
            raise Exception("HuggingFace key required")
        
        r = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers={"Authorization": f"Bearer {keys['huggingface']}"},
            json={"inputs": prompt},
        )
        
        data = r.json()
        if isinstance(data, dict) and "error" in data:
            raise Exception(data["error"])
        return data[0]["generated_text"]

# -------------------------------------------------------
# Media Generation Function
# -------------------------------------------------------
def generate_media(text, model, voice, keys):
    if model == "openai-tts":
        if not keys["openai"]:
            raise Exception("OpenAI API key required")
        
        r = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {keys['openai']}",
                "Content-Type": "application/json"
            },
            json={"model": "tts-1-hd", "voice": voice, "input": text}
        )
        return {"type": "audio", "content": r.content}
    
    elif model == "elevenlabs":
        if not keys["elevenlabs"]:
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
        return {"type": "audio", "content": r.content}
    
    elif model == "did":
        if not keys["did"]:
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
        keys = {
            "openai": openai_key,
            "anthropic": anthropic_key,
            "google": google_key,
            "huggingface": hf_key,
            "elevenlabs": elevenlabs_key,
            "did": did_key
        }
        
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
    <div style='font-weight: 600; font-size: 16px; margin-bottom: 8px;'>🚀 Multi-Model AI Agent</div>
    <div>Built with ❤️ by Vivek YT • Powered by Multiple AI Models</div>
    <div style='margin-top: 12px; font-size: 12px; opacity: 0.7;'>
        OpenAI • Claude • Gemini • HuggingFace • ElevenLabs • D-ID
    </div>
</div>
""", unsafe_allow_html=True)
