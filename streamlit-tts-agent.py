# app.py — Beautiful AI Video Agent with Modern UI
import streamlit as st
import requests
import base64
from PIL import Image
import io
import time

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG & CUSTOM STYLING
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Video Creator Studio",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Content card */
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 300;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 15px;
        border: 2px solid #667eea;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Result sections */
    .result-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(17, 153, 142, 0.4);
    }
    
    /* Image styling */
    img {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Audio player */
    audio {
        width: 100%;
        border-radius: 50px;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        background: #11998e;
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <div class="main-title">🎬 AI Video Creator Studio</div>
    <div class="main-subtitle">Transform Your Words into Cinematic Experiences</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# API KEYS CHECK
# ═══════════════════════════════════════════════════════════
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY")
LEONARDO_KEY = st.secrets.get("LEONARDO_KEY")
ELEVENLABS_KEY = st.secrets.get("ELEVENLABS_KEY")

if not all([GROQ_KEY, ANTHROPIC_KEY, LEONARDO_KEY, ELEVENLABS_KEY]):
    st.markdown("""
    <div class="content-card">
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #f5576c;">🔑 API Keys Required</h2>
            <p style="font-size: 1.1rem; color: #666; margin: 1rem 0;">
                To use this AI Video Creator, you need to add your API keys in <strong>Settings → Secrets</strong>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📋 Get your FREE API keys from:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🚀 [Groq API](https://console.groq.com/keys)")
        st.markdown("🖼️ [Leonardo AI](https://app.leonardo.ai/account/api-keys)")
    with col2:
        st.markdown("🤖 [Anthropic Claude](https://console.anthropic.com/settings/keys)")
        st.markdown("🎤 [ElevenLabs](https://elevenlabs.io)")
    
    st.code("""GROQ_API_KEY = "gsk_..."
ANTHROPIC_API_KEY = "sk-ant-api03..."
LEONARDO_KEY = "your-leonardo-key"
ELEVENLABS_KEY = "your-elevenlabs-key"
""", language="toml")
    st.stop()

# ═══════════════════════════════════════════════════════════
# FEATURE SHOWCASE
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="content-card">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✍️</div>
        <div class="feature-title">AI Writing</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">Powered by Groq & Claude</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎨</div>
        <div class="feature-title">Image Gen</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">Leonardo AI</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎙️</div>
        <div class="feature-title">Voice AI</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">ElevenLabs TTS</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎬</div>
        <div class="feature-title">Video Mix</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">Instant Creation</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# AI FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_story(prompt):
    """Generate and enhance story with Groq + Claude"""
    try:
        # Groq (fast generation)
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={"model": "llama-3.2-90b-text-preview", 
                  "messages": [{"role": "user", "content": f"Write a short vivid cinematic scene (max 150 words): {prompt}"}], 
                  "max_tokens": 200})
        raw = r.json()["choices"][0]["message"]["content"]

        # Claude (enhance)
        r2 = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
            json={"model": "claude-3-5-sonnet-20241022", 
                  "max_tokens": 250, 
                  "messages": [{"role": "user", "content": f"Make this vivid, cinematic, and descriptive (max 150 words):\n\n{raw}"}]})
        enhanced = r2.json()["content"][0]["text"]
        return raw, enhanced
    except Exception as e:
        st.error(f"❌ Story generation failed: {str(e)}")
        return None, None

def generate_image(prompt):
    """Generate image with Leonardo AI"""
    try:
        r = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations",
            headers={"Authorization": f"Bearer {LEONARDO_KEY}"},
            json={"prompt": f"cinematic, detailed, high quality: {prompt}", 
                  "width": 768, 
                  "height": 512, 
                  "num_images": 1})
        job_id = r.json()["sdGenerationJob"]["generationId"]

        for i in range(25):
            time.sleep(3)
            resp = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{job_id}",
                headers={"Authorization": f"Bearer {LEONARDO_KEY}"})
            data = resp.json()
            
            if data["generations_by_pk"]["status"] == "COMPLETE":
                url = data["generations_by_pk"]["generated_images"][0]["url"]
                return requests.get(url, stream=True).content
        
        st.warning("⏱️ Image generation timed out")
        return None
    except Exception as e:
        st.error(f"❌ Image generation failed: {str(e)}")
        return None

def generate_voice(text):
    """Generate voice with ElevenLabs"""
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        r = requests.post(url, 
            headers={"xi-api-key": ELEVENLABS_KEY},
            json={"text": text, 
                  "voice_settings": {"stability": 0.75, "similarity_boost": 0.8},
                  "model_id": "eleven_monolingual_v1"})
        return r.content
    except Exception as e:
        st.error(f"❌ Voice generation failed: {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════
# MAIN INPUT SECTION
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="content-card">', unsafe_allow_html=True)

st.markdown('<h2 style="color: #667eea; text-align: center; margin-bottom: 1rem;">✨ Describe Your Scene</h2>', unsafe_allow_html=True)

# Example prompts
with st.expander("💡 Need inspiration? Try these examples"):
    examples = [
        "A cyberpunk samurai walking through neon Tokyo rain at midnight",
        "An astronaut discovering ancient alien ruins on Mars at sunset",
        "A magical forest with glowing mushrooms and fairy lights at dusk",
        "A steampunk airship soaring above Victorian London in fog",
        "A dragon perched on a mountain peak during a lightning storm"
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.prompt = ex

prompt = st.text_area(
    "Your scene description",
    height=120,
    value=st.session_state.get('prompt', ''),
    placeholder="Example: A mysterious lighthouse on a stormy cliff, waves crashing, lightning illuminating the dark sky...",
    help="Be descriptive! Include details about setting, mood, lighting, and atmosphere."
)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# GENERATE BUTTON
# ═══════════════════════════════════════════════════════════
generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
with generate_col2:
    generate_button = st.button("🎬 Create My Video", type="primary", use_container_width=True)

# ═══════════════════════════════════════════════════════════
# GENERATION PROCESS
# ═══════════════════════════════════════════════════════════
if generate_button and prompt:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    progress = st.progress(0)
    status = st.empty()
    
    # Step 1: Generate Story
    status.markdown('<div class="status-badge">📝 Writing your story...</div>', unsafe_allow_html=True)
    raw, final_text = create_story(prompt)
    
    if raw and final_text:
        progress.progress(20)
        
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📖 Your Story</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["✨ Enhanced Version", "📄 Original Draft"])
        with tab1:
            st.markdown(f"<div style='font-size: 1.1rem; line-height: 1.8; color: #333;'>{final_text}</div>", unsafe_allow_html=True)
        with tab2:
            st.markdown(f"<div style='font-size: 1rem; line-height: 1.7; color: #666;'>{raw}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 2: Generate Image
        status.markdown('<div class="status-badge">🎨 Creating your image...</div>', unsafe_allow_html=True)
        img_data = generate_image(final_text)
        
        if img_data:
            progress.progress(50)
            
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🖼️ Your Image</div>', unsafe_allow_html=True)
            st.image(img_data, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 3: Generate Voice
            status.markdown('<div class="status-badge">🎙️ Generating voice narration...</div>', unsafe_allow_html=True)
            audio_data = generate_voice(final_text)
            
            if audio_data:
                progress.progress(75)
                
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🎵 Your Audio</div>', unsafe_allow_html=True)
                st.audio(audio_data, format="audio/mp3")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Step 4: Create Video
                status.markdown('<div class="status-badge">🎬 Composing final video...</div>', unsafe_allow_html=True)
                
                img_b64 = base64.b64encode(img_data).decode()
                audio_b64 = base64.b64encode(audio_data).decode()
                
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🎥 Your Final Video</div>', unsafe_allow_html=True)
                
                video_html = f"""
                <div style="position: relative; width: 100%; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                    <img src="data:image/png;base64,{img_b64}" style="width: 100%; display: block;">
                    <audio controls autoplay style="width: 100%; position: absolute; bottom: 0; background: rgba(0,0,0,0.7);">
                        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    </audio>
                </div>
                """
                st.markdown(video_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                progress.progress(100)
                status.markdown('<div class="status-badge" style="background: #11998e;">✅ Complete!</div>', unsafe_allow_html=True)
                
                # Download Section
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">💾 Download Your Creation</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📥 Image", img_data, "ai_scene.png", "image/png", use_container_width=True)
                with col2:
                    st.download_button("📥 Audio", audio_data, "ai_voice.mp3", "audio/mp3", use_container_width=True)
                with col3:
                    st.download_button("📥 Story", final_text, "ai_story.txt", "text/plain", use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

elif generate_button:
    st.warning("⚠️ Please enter a scene description first!")

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align: center; padding: 2rem; color: white; margin-top: 2rem;">
    <p style="font-size: 0.9rem; opacity: 0.8;">
        Powered by Groq 🚀 Claude 🤖 Leonardo AI 🎨 ElevenLabs 🎙️
    </p>
    <p style="font-size: 0.8rem; opacity: 0.6;">
        Made with ❤️ using Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
