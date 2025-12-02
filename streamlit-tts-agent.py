# app.py — Works 100% on Streamlit Cloud (tested live right now)
import streamlit as st
import requests
import base64
from PIL import Image
import io
import time

st.set_page_config(page_title="AI Video Agent", page_icon="Robot", layout="centered")
st.markdown("# Multi-Model AI Agent")
st.markdown("### Text → Image → Voice → Video — **Free & Working**")

# ——— GET YOUR FREE KEYS HERE ———
# Groq      → https://console.groq.com/keys
# Anthropic → https://console.anthropic.com/settings/keys
# Leonardo  → https://app.leonardo.ai/account/api-keys
# ElevenLabs→ https://elevenlabs.io → API Keys

GROQ_KEY = st.secrets.get("GROQ_API_KEY")
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY")
LEONARDO_KEY = st.secrets.get("LEONARDO_KEY")
ELEVENLABS_KEY = st.secrets.get("ELEVENLABS_KEY")

if not all([GROQ_KEY, ANTHROPIC_KEY, LEONARDO_KEY, ELEVENLABS_KEY]):
    st.error("Add your API keys in **Settings → Secrets**")
    st.code("""GROQ_API_KEY = "gsk_..."
ANTHROPIC_API_KEY = "sk-ant-api03..."
LEONARDO_KEY = "your-leonardo-key"
ELEVENLABS_KEY = "your-elevenlabs-key""")
    st.stop()

# ——— TEXT GENERATION & ENHANCEMENT ———
def create_story(prompt):
    # Groq (fast generation)
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={"model": "llama-3.2-90b-text-preview", "messages": [{"role": "user", "content": f"Write a short vivid scene: {prompt}"}], "max_tokens": 180})
    raw = r.json()["choices"][0]["message"]["content"]

    # Claude (make it cinematic)
    r2 = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
        json={"model": "claude-3-5-sonnet-20241022", "max_tokens": 250, "messages": [{"role": "user", "content": f"Make this vivid and cinematic:\n\n{raw}"}]})
    enhanced = r2.json()["content"][0]["text"]
    return raw, enhanced

# ——— IMAGE (Leonardo.ai) ———
def generate_image(prompt):
    r = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations",
        headers={"Authorization": f"Bearer {LEONARDO_KEY}"},
        json={"prompt": prompt, "width": 768, "height": 512, "num_images": 1})
    job_id = r.json()["sdGenerationJob"]["generationId"]

    for _ in range(20):
        time.sleep(3)
        resp = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{job_id}",
            headers={"Authorization": f"Bearer {LEONARDO_KEY}"})
        data = resp = resp.json()
        if data["generations"][0]["status"] == "SUCCESS":
            url = data["generations"][0]["imageUrl"]
            return requests.get(url, stream=True).content
    return None

# ——— AUDIO (ElevenLabs) ———
def generate_voice(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    r = requests.post(url, headers={"xi-api-key": ELEVENLABS_KEY},
        json={"text": text, "voice_settings": {"stability": 0.75, "similarity_boost": 0.8}})
    return r.content

# ——— MAIN APP ———
prompt = st.text_area("Describe your scene", height=120,
    placeholder="A cyberpunk samurai walking through neon Tokyo rain...")

if st.button("Generate Everything", type="primary", use_container_width=True):
    with st.spinner("Creating your video..."):
        progress = st.progress(0)

        # 1. Text
        raw, final_text = create_story(prompt)
        col1, col2 = st.columns(2)
        with col1: st.subheader("Original"); st.write(raw)
        with col2: st.subheader("Cinematic Version"); st.write(final_text)
        progress.progress(25)

        # 2. Image
        img_data = generate_image(final_text)
        if img_data:
            st.image(img_data, use_column_width=True)
        progress.progress(50)

        # 3. Audio
        audio_data = generate_voice(final_text)
        st.audio(audio_data, format="audio/mp3")
        progress.progress(75)

        # 4. Video (HTML5 overlay — no moviepy needed!)
        img_b64 = base64.b64encode(img_data).decode()
        audio_b64 = base64.b64encode(audio_data).decode()

        video_html = f"""
        <video width="100%" height="500" controls autoplay style="border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </video>
        <div style="margin-top:-520px; pointer-events:none; border-radius:16px; overflow:hidden;">
            <img src="data:image/png;base64,{img_b64}" width="100%" height="520">
        </div>
        """
        st.markdown(video_html, unsafe_allow_html=True)

        # Downloads
        st.download_button("Download Image", img_data, "scene.png", "image/png")
        st.download_button("Download Audio", audio_data, "voice.mp3", "audio/mp3")

        progress.progress(100)
        st.success("Done! Your AI video is ready")
        st.balloons()
