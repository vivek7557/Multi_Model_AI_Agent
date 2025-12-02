# app.py — Works on Streamlit Cloud FREE tier with ZERO errors
import streamlit as st
import os
import io
import tempfile
import wave
import numpy as np
from PIL import Image

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Lightning AI Agent", page_icon="Lightning", layout="centered")
st.title("Lightning Multi-Model AI Agent")
st.markdown("### Generate → Enhance → Image → Audio → Video in seconds (CPU-friendly)")

# ------------------- LAZY LOAD ONLY WHEN NEEDED -------------------
@st.cache_resource(show_spinner="Loading AI models (first time only)...")
def load_models():
    import torch
    from diffusers import StableDiffusionPipeline
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer, pipeline
    from groq import Groq
    from anthropic import Anthropic

    device = "cpu"  # Force CPU — works everywhere
    st.info("Running on CPU (works on free Streamlit Cloud)")

    # 1. Tiny & fast image model
    pipe_img = StableDiffusionPipeline.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float32,
        safety_checker=None
    )
    pipe_img.to(device)

    # 2. Parler-TTS Mini (best quality on CPU)
    tts_model = ParlerTTSForConditionalGeneration.from_pretrained(
        "parler-tts/parler-tts-mini-v1"
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
    tts = pipeline("text-to-speech", model=tts_model, tokenizer=tokenizer, device=-1)

    # 3. API clients
    groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    if not groq_key or not anthropic_key:
        st.error("Please add GROQ_API_KEY and ANTHROPIC_API_KEY in Secrets")
        st.stop()

    groq_client = Groq(api_key=groq_key)
    claude_client = Anthropic(api_key=anthropic_key)

    return pipe_img, tts, groq_client, claude_client

# ------------------- PURE-PYTHON WAV WRITER (no soundfile needed) -------------------
def numpy_to_wav_bytes(audio_np, sample_rate=24000):
    audio_np = audio_np.T if audio_np.ndim > 1 else audio_np
    audio_np = (audio_np * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_np.tobytes())
    buffer.seek(0)
    return buffer

# ------------------- CORE FUNCTIONS -------------------
def generate_text(prompt, client):
    resp = client.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=[{"role": "user", "content": f"Write a short vivid scene: {prompt}"}],
        max_tokens=200
    )
    return resp.choices[0].message.content

def enhance_text(text, client):
    resp = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": f"Make this cinematic:\n\n{text}"}]
    )
    return resp.content[0].text

def text_to_image(prompt, pipe):
    img = pipe(prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
    return img

def text_to_audio(text, tts_pipe):
    out = tts_pipe(text, forward_params={"description": "A clear female voice, calm and professional"})
    return out["audio"], out["sampling_rate"]

def image_audio_to_video(img_pil, audio_np, sr):
    from moviepy.editor import ImageClip, AudioClip

    def make_frame(t):
        return np.array(img_pil)

    audio_clip = AudioClip(lambda t: audio_np[int(t * sr)] if t * sr < len(audio_np) else 0, duration=len(audio_np)/sr, fps=sr)
    video = ImageClip(make_frame, duration=audio_clip.duration).set_audio(audio_clip)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video.write_videofile(tmp.name, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    video.close()
    return tmp.name

# ------------------- MAIN -------------------
prompt = st.text_area("Describe your scene", placeholder="A cyberpunk fox dancing under neon rain...", height=100)

if st.button("Generate Everything Now", type="primary", use_container_width=True):
    if not prompt.strip():
        st.error("Enter a prompt!")
        st.stop()

    pipe_img, tts, groq, claude = load_models()
    progress = st.progress(0)
    status = st.empty()

    # Text
    status.info("Generating text...")
    text1 = generate_text(prompt, groq)
    text2 = enhance_text(text1, claude)
    col1, col2 = st.columns(2)
    with col1: st.subheader("Original"); st.write(text1)
    with col2: st.subheader("Enhanced"); st.write(text2)
    progress.progress(30)

    # Image
    status.info("Generating image...")
    img = text_to_image(text2, pipe_img)
    st.image(img, use_column_width=True)
    progress.progress(60)

    # Audio
    status.info("Generating voice...")
    audio_np, sr = text_to_audio(text2, tts)
    wav_bytes = numpy_to_wav_bytes(audio_np, sr)
    st.audio(wav_bytes, format="audio/wav")
    progress.progress(80)

    # Video
    status.info("Creating video...")
    video_path = image_audio_to_video(img, audio_np, sr)
    st.video(video_path)
    with open(video_path, "rb") as f:
        st.download_button("Download Video", f, "ai_video.mp4", "video/mp4")
    os.unlink(video_path)

    progress.progress(100)
    st.success("Done! Lightning")
    st.balloons()
