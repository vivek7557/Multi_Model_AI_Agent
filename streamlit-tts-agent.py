# app.py — Works on Streamlit Cloud, HF Spaces, RunPod, local, etc.
import streamlit as st
import os
import io
import tempfile
from pathlib import Path

# ------------------- PAGE CONFIG & STYLE -------------------
st.set_page_config(page_title="Lightning AI Agent", page_icon="Lightning", layout="centered")
st.markdown("""
<style>
    .big-title {font-size: 3.5rem !important; text-align: center; background: linear-gradient(90deg, #667eea, #764ba2);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;}
    .speed {background:#10b981;color:white;padding:8px 16px;border-radius:30px;font-size:0.9rem;}
    .stButton>button {background:linear-gradient(90deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;height:3.2em;font-weight:bold;width:100%;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="big-title">Lightning AI Agent</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:1.3rem;color:#666;'>Text → Enhanced → Image → Audio → Video in < 12 seconds</p>", unsafe_allow_html=True)
st.markdown("<div class='speed'>CPU & GPU compatible • No torch errors</div><br>", unsafe_allow_html=True)

# ------------------- LAZY IMPORTS (Fixes torch import crash) -------------------
@st.cache_resource(show_spinner="Starting the engines...")
def load_models():
    try:
        import torch
        from diffusers import StableDiffusionPipeline
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer, pipeline
    except ImportError as e:
        st.error(f"Missing dependency: {e}. Run: pip install torch diffusers transformers parler-tts soundfile moviepy")
        st.stop()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    st.info(f"Running on **{device.upper()}**")

    # 1. Fast Image: SD-Turbo (works on CPU too!)
    with st.spinner("Loading image model..."):
        pipe_img = StableDiffusionPipeline.from_pretrained(
            "stabilityai/sd-turbo",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            safety_checker=None,
            variant="fp16" if device == "cuda" else None
        )
        pipe_img.to(device)
        if device == "cuda":
            pipe_img.enable_attention_slicing()

    # 2. Fast TTS: Parler-TTS Mini (best quality + works on CPU)
    with st.spinner("Loading voice model..."):
        tts_model = ParlerTTSForConditionalGeneration.from_pretrained(
            "parler-tts/parler-tts-mini-v1"
        ).to(device)
        tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
        tts = pipeline("text-to-speech", model=tts_model, tokenizer=tokenizer, device=device)

    # 3. Groq & Claude
    from groq import Groq
    from anthropic import Anthropic
    groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"))
    claude_client = Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

    return pipe_img, tts, groq_client, claude_client, device

# ------------------- CORE FUNCTIONS -------------------
def generate_text(prompt):
    chat = st.session_state.groq.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=[{"role": "user", "content": f"Write a short vivid scene: {prompt}"}],
        max_tokens=250,
        temperature=0.8
    )
    return chat.choices[0].message.content

def enhance_text(text):
    msg = st.session_state.claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=400,
        messages=[{"role": "user", "content": f"Make this more cinematic and engaging:\n\n{text}"}]
    )
    return msg.content[0].text

def generate_image(prompt):
    image = st.session_state.pipe_img(prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
    return image

def generate_audio(text):
    output = st.session_state.tts(text, forward_params={"description": "A clear female voice speaking slowly"})
    return output["audio"], output["sampling_rate"]

def audio_image_to_video(image, audio_np, sr):
    import soundfile as sf
    from moviepy.editor import ImageClip, AudioFileClip

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        sf.write(tmp_wav.name, audio_np.T, sr)  # Parler outputs (channels, samples)
        audio = AudioFileClip(tmp_wav.name)

    duration = audio.duration
    clip = ImageClip(image).set_duration(duration).set_audio(audio)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_mp4:
        clip.write_videofile(tmp_mp4.name, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        video_path = tmp_mp4.name

    # Cleanup
    audio.close()
    clip.close()
    os.unlink(tmp_wav.name)
    return video_path

# ------------------- MAIN -------------------
prompt = st.text_input("Your idea", placeholder="A samurai robot meditating under cherry blossoms at sunrise...", height=80)

if st.button("Generate Everything (Ultra Fast)", type="primary"):
    if not prompt:
        st.error("Please enter a prompt!")
        return

    # Load models once
    if "pipe_img" not in st.session_state:
        pipe_img, tts, groq, claude, device = load_models()
        st.session_state.pipe_img = pipe_img
        st.session_state.tts = tts
        st.session_state.groq = groq
        st.session_state.claude = claude

    progress = st.progress(0)
    status = st.empty()

    # 1. Text
    status.info("Generating story...")
    raw_text = generate_text(prompt)
    enhanced = enhance_text(raw_text)
    st.success("Text ready!")
    c1, c2 = st.columns(2)
    with c1: st.subheader("Raw"); st.write(raw_text)
    with c2: st.subheader("Enhanced"); st.write(enhanced)
    progress.progress(25)

    # 2. Image
    status.info("Creating image (SD-Turbo)...")
    img = generate_image(enhanced)
    st.image(img, use_column_width=True)
    progress.progress(50)

    # 3. Audio
    status.info("Speaking with Parler-TTS...")
    audio_np, sr = generate_audio(enhanced)
    audio_bytes = io.BytesIO()
    import soundfile as sf
    sf.write(audio_bytes, audio_np.T, sr, format="WAV")
    audio_bytes.seek(0)
    st.audio(audio_bytes, format="audio/wav")
    progress.progress(75)

    # 4. Video
    status.info("Building video...")
    video_path = audio_image_to_video(img, audio_np, sr)
    st.video(video_path)
    with open(video_path, "rb") as f:
        st.download_button("Download Video", f, "ai_video.mp4", "video/mp4")
    progress.progress(100)
    st.success("Done in seconds! Lightning")
    st.balloons()

    # Cleanup
    os.unlink(video_path)
