# app.py — Works 100% on Streamlit Community Cloud (free)
import streamlit as st
import os
import io
import base64
from PIL import Image
import requests
from moviepy.editor import ImageClip, AudioClip
import numpy as np
import tempfile

st.set_page_config(page_title="AI Agent", page_icon="Robot", layout="centered")
st.title("Multi-Model AI Agent")
st.markdown("### Text → Enhanced → Image → Audio → Video (Free Tier Ready)")

# === GET API KEYS FROM SECRETS (must add in Streamlit settings) ===
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY")
LEONARDO_KEY = st.secrets.get("LEONARDO_KEY")      # Free: https://app.leonardo.ai/api
ELEVENLABS_KEY = st.secrets.get("ELEVENLABS_KEY")  # Free tier available

if not all([GROQ_KEY, ANTHROPIC_KEY, LEONARDO_KEY, ELEVENLABS_KEY]):
    st.error("Please add these API keys in Secrets (Settings → Secrets):")
    st.code("""
GROQ_API_KEY = "gsk_..."
ANTHROPIC_API_KEY = "sk-ant-api03..."
LEONARDO_KEY = "your-leonardo-api-key"
ELEVENLABS_KEY = "your-elevenlabs-api-key"
    """)
    st.stop()

# === STEP 1 & 2: Text Generation + Enhancement ===
def generate_and_enhance(prompt):
    # Groq (fast generation)
    import requests
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={
            "model": "llama-3.2-90b-text-preview",
            "messages": [{"role": "user", "content": f"Write a short vivid scene: {prompt}"}],
            "max_tokens": 200
        })
    raw = r.json()["choices"][0]["message"]["content"]

    # Claude (enhancement)
    r2 = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
        json={
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": f"Make this cinematic and engaging:\n\n{raw}"}]
        })
    enhanced = r2.json()["content"][0]["text"]
    return raw, enhanced

# === STEP 3: Image via Leonardo.ai (fast & beautiful) ===
def text_to_image(prompt):
    r = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations",
        headers={"Authorization": f"Bearer {LEONARDO_KEY}"},
        json={
            "prompt": prompt,
            "width": 768,
            "height": 512,
            "num_images": 1,
            "modelId": "1e60896f-3c26-4296-8ecc-53e2afecc132"  # Alchemy model (fast)
        })
    gen_id = r.json()["sdGenerationJob"]["generationId"]
    
    # Poll until ready
    import time
    for _ in range(20):
        time.sleep(3)
        r2 = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
            headers={"Authorization": f"Bearer {LEONARDO_KEY}"})
        data = r2.json()
        if data["generations"][0]["status"] == "SUCCESS":
            url = data["generations"][0]["imageUrl"]
            img = Image.open(requests.get(url, stream=True).raw)
            return img
    st.error("Image timed out")
    return Image.new("RGB", (768, 512), "gray")

# === STEP 4: Audio via ElevenLabs (best free voice) ===
def text_to_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    headers = {"xi-api-key": ELEVENLABS_KEY}
    data = {"text": text, "voice_settings": {"stability": 0.7, "similarity_boost": 0.8}}
    r = requests.post(url, headers=headers, json=data)
    return io.BytesIO(r.content)

# === STEP 5: Combine Image + Audio → Video ===
def make_video(img, audio_bytes):
    audio_bytes.seek(0)
    from moviepy.editor import AudioFileClip
    audio = AudioFileClip(audio_bytes)
    duration = audio.duration
    
    clip = ImageClip(np.array(img)).set_duration(duration).set_audio(audio)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    clip.write_videofile(tmp.name, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    clip.close()
    return tmp.name

# === MAIN APP ===
prompt = st.text_area("Your idea", placeholder="A mystical dragon flying over ancient mountains at sunset...", height=120)

if st.button("Generate Everything", type="primary", use_container_width=True):
    with st.spinner("Working..."):
        progress = st.progress(0)

        # 1-2. Text
        raw, enhanced = generate_and_enhance(prompt)
        c1, c2 = st.columns(2)
        with c1: st.subheader("Original"); st.write(raw)
        with c2: st.subheader("Enhanced"); st.write(enhanced)
        progress.progress(30)

        # 3. Image
        st.write("Generating image...")
        img = text_to_image(enhanced)
        st.image(img, use_column_width=True)
        progress.progress(60)

        # 4. Audio
        st.write("Generating voice...")
        audio_bytes = text_to_audio(enhanced)
        st.audio(audio_bytes, format="audio/mp3")
        progress.progress(80)

        # 5. Video
        st.write("Creating video...")
        video_path = make_video(img, audio_bytes)
        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button("Download Video", f, "ai_creation.mp4", "video/mp4")
        os.unlink(video_path)

        progress.progress(100)
        st.success("All done!")
        st.balloons()
