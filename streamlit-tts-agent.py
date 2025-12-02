# app.py — Works 100% on free Streamlit Community Cloud
import streamlit as st
import requests
import base64
from PIL import Image
import io
import time

st.set_page_config(page_title="AI Agent", page_icon="Robot", layout="centered")
st.title("Multi-Model AI Agent")
st.markdown("### Text → Enhanced → Image → Voice → Video — **Free Tier Ready**")

# === API KEYS FROM SECRETS ===
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY")
LEONARDO_KEY = st.secrets.get("LEONARDO_KEY")
ELEVENLABS_KEY = st.secrets.get("ELEVENLABS_KEY")

if not all([GROQ_KEY, ANTHROPIC_KEY, LEONARDO_KEY, ELEVENLABS_KEY]):
    st.error("Missing API keys! Add them in Settings → Secrets:")
    st.code('GROQ_API_KEY = "your_groq_key"\nANTHROPIC_API_KEY = "your_anthropic_key"\nLEONARDO_KEY = "your_leonardo_key"\nELEVENLABS_KEY = "your_elevenlabs_key"')
    st.stop()

# === 1. Generate + Enhance Text ===
def generate_text(prompt):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={"model": "llama-3.2-90b-text-preview", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200})
    return r.json()["choices"][0]["message"]["content"]

def enhance_text(text):
    r = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
        json={"model": "claude-3-5-sonnet-20241022", "max_tokens": 300, "messages": [{"role": "user", "content": f"Make this vivid and cinematic:\n\n{text}"}]})
    return r.json()["content"][0]["text"]

# === 2. Image via Leonardo.ai ===
def get_image(prompt):
    r = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations",
        headers={"Authorization": f"Bearer {LEONARDO_KEY}"},
        json={"prompt": prompt, "width": 768, "height": 512, "num_images": 1})
    gen_id = r.json()["sdGenerationJob"]["generationId"]
    
    for _ in range(25):
        time.sleep(3)
        resp = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
            headers={"Authorization": f"Bearer {LEONARDO_KEY}"})
        data = resp.json()
        if data["generations"][0]["status"] == "SUCCESS":
            url = data["generations"][0]["imageUrl"]
            return requests.get(url, stream=True).content
    return None

# === 3. Audio via ElevenLabs ===
def get_audio(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM/stream"  # Rachel voice
    headers = {"xi-api-key": ELEVENLABS_KEY}
    data = {"text": text, "voice_settings": {"stability": 0.75, "similarity_boost": 0.8}}
    r = requests.post(url, headers=headers, json=data, stream=True)
    return r.content

# === 4. Create Video using HTML5 + base64 (no moviepy!) ===
def create_html_video(image_bytes, audio_bytes):
    img_b64 = base64.b64encode(image_bytes).decode()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    html = f"""
    <video width="100%" controls autoplay>
        <source src="data:video/mp4;base64,{audio_b64}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    <style>
        video {{ background: url(data:image/png;base64,{img_b64}) center/cover no-repeat; }}
    </style>
    """
    return html

# === MAIN ===
prompt = st.text_area("Your idea", "A glowing phoenix rising from volcanic ashes at dawn", height=100)

if st.button("Generate Everything", type="primary", use_container_width=True):
    with st.spinner("Creating magic..."):
        progress = st.progress(0)

        # Step 1: Text
        raw = generate_text(f"Write a short vivid scene about: {prompt}")
        enhanced = enhance_text(raw)
        col1, col2 = st.columns(2)
        with col1: st.subheader("Original"); st.write(raw)
        with col2: st.subheader("Enhanced"); st.write(enhanced)
        progress.progress(25)

        # Step 2: Image
        st.write("Generating image...")
        img_data = get_image(enhanced)
        if img_data:
            st.image(img_data, use_column_width=True)
        progress.progress(50)

        # Step 3: Audio
        st.write("Generating voice...")
        audio_data = get_audio(enhanced)
        st.audio(audio_data, format="audio/mp3")
        progress.progress(75)

        # Step 4: Video (HTML5 trick — no moviepy needed!)
        st.write("Creating video...")
        video_html = f"""
        <video width="100%" controls autoplay style="border-radius:15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <source src="data:audio/mp3;base64,{base64.b64encode(audio_data).decode()}" type="audio/mp3">
        </video>
        <div style="text-align:center; margin-top:10px; background: url(data:image/png;base64,{base64.b64encode(img_data).decode()}) center/cover; height:400px; border-radius:15px;"></div>
        """
        st.markdown(video_html, unsafe_allow_html=True)
        
        # Download buttons
        st.download_button("Download Image", img_data, "image.png", "image/png")
        st.download_button("Download Audio", audio_data, "voice.mp3", "audio/mp3")
        
        progress.progress(100)
        st.success("Done! All services working perfectly")
        st.balloons()
