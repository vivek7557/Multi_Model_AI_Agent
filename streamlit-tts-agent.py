import streamlit as st
import os
import io
import tempfile
import soundfile as sf
from moviepy.editor import ImageClip, AudioFileClip

# ------------------- PAGE CONFIG -------------------
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
st.markdown("<p style='text-align:center;font-size:1.3rem;color:#666;'>Generate → Enhance → Image → Audio → Video in seconds</p>", unsafe_allow_html=True)
st.markdown("<div class='speed'>CPU + GPU • Zero errors • Instant deploy</div><br>", unsafe_allow_html=True)

# ------------------- LAZY LOAD HEAVY LIBRARIES -------------------
@st.cache_resource(show_spinner="Warming up AI models...")
def load_models():
    import torch
    from diffusers import StableDiffusionPipeline
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer, pipeline
    from groq import Groq
    from anthropic import Anthropic

    device = "cuda" if torch.cuda.is_available() else "cpu"
    st.info(f"Running on **{device.upper()}**")

    # Image model (SD-Turbo = 1-step super fast)
    pipe_img = StableDiffusionPipeline.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None,
        variant="fp16" if device == "cuda" else None
    )
    pipe_img.to(device)
    if device == "cuda":
        pipe_img.enable_attention_slicing()

    # TTS model (Parler-TTS Mini – works great on CPU too)
    tts_model = ParlerTTSForConditionalGeneration.from_pretrained(
        "parler-tts/parler-tts-mini-v1"
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
    tts = pipeline("text-to-speech", model=tts_model, tokenizer=tokenizer, device=device if device == "cuda" else -1)

    # API clients
    groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"))
    claude_client = Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

    return pipe_img, tts, groq_client, claude_client, device

# ------------------- CORE FUNCTIONS -------------------
def generate_text(prompt, groq_client):
    response = groq_client.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=[{"role": "user", "content": f"Write a short vivid scene about: {prompt}"}],
        max_tokens=250,
        temperature=0.8
    )
    return response.choices[0].message.content

def enhance_text(text, claude_client):
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=400,
        messages=[{"role": "user", "content": f"Rewrite this to be more cinematic and engaging:\n\n{text}"}]
    )
    return response.content[0].text

def text_to_image(prompt, pipe):
    image = pipe(prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
    return image

def text_to_audio(text, tts_pipe):
    output = tts_pipe(text, forward_params={"description": "A clear female voice speaking slowly and calmly"})
    return output["audio"], output["sampling_rate"]

def make_video(image_pil, audio_np, sr):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        sf.write(tmp_wav.name, audio_np.T, sr)
        audio_clip = AudioFileClip(tmp_wav.name)

    clip = ImageClip(image_pil).set_duration(audio_clip.duration).set_audio(audio_clip)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_mp4:
        clip.write_videofile(tmp_mp4.name, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        video_path = tmp_mp4.name

    audio_clip.close()
    clip.close()
    os.unlink(tmp_wav.name)
    return video_path

# ------------------- MAIN APP -------------------
prompt = st.text_area("Your idea / story", placeholder="A lone astronaut floating above a purple nebula, dramatic lighting...", height=100)

if st.button("Generate Everything (Ultra Fast)", type="primary"):
    if not prompt.strip():
        st.error("Please enter a prompt!")
        st.stop()

    # Load models once
    pipe_img, tts_pipe, groq_client, claude_client, device = load_models()

    progress = st.progress(0)
    status = st.empty()

    # 1. Text
    status.info("Generating text with Groq...")
    raw_text = generate_text(prompt, groq_client)
    enhanced_text = enhance_text(raw_text, claude_client)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Raw Text")
        st.write(raw_text)
    with c2:
        st.subheader("Enhanced (Cinematic)")
        st.write(enhanced_text)
    progress.progress(25)

    # 2. Image
    status.info("Generating image (SD-Turbo)...")
    image = text_to_image(enhanced_text, pipe_img)
    st.image(image, use_column_width=True)
    progress.progress(50)

    # 3. Audio
    status.info("Generating voice (Parler-TTS)...")
    audio_np, sr = text_to_audio(enhanced_text, tts_pipe)
    audio_bytes = io.BytesIO()
    sf.write(audio_bytes, audio_np.T, sr, format="WAV")
    audio_bytes.seek(0)
    st.audio(audio_bytes, format="audio/wav")
    progress.progress(75)

    # 4. Video
    status.info("Creating video...")
    video_path = make_video(image, audio_np, sr)
    st.video(video_path)

    with open(video_path, "rb") as f:
        st.download_button("Download Video MP4", f, "ai_video.mp4", "video/mp4")

    progress.progress(100)
    st.success("All done in seconds! Lightning")
    st.balloons()

    # Cleanup
    os.unlink(video_path)
