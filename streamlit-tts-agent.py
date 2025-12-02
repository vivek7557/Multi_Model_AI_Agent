import streamlit as st
import os
import asyncio
from pathlib import Path
import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionPipeline
from transformers import pipeline, AutoModelForCausalSpeechGeneration
import soundfile as sf
from moviepy.editor import ImageClip, AudioFileClip
import tempfile
import io
import numpy as np

# ==================== CONFIG ====================
st.set_page_config(page_title="Lightning AI Agent", page_icon="⚡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 3.5rem; text-align: center; background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .speed-badge {background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; display: inline-block;}
    .stButton>button {background: linear-gradient(90deg, #667eea, #764ba2); color: white; border: none; border-radius: 12px; height: 3em; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ==================== FAST MODELS (Pre-warmed) ====================
@st.cache_resource(show_spinner="Warming up turbo engines...")
def load_models():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    # 1. SDXL-Turbo (1-step, 512x512 in <1s)
    pipe_img = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/sdxl-turbo",
        torch_dtype=dtype,
        variant="fp16" if device == "cuda" else None,
        safety_checker=None
    )
    pipe_img.to(device)
    if device == "cuda":
        pipe_img.enable_attention_slicing()
        pipe_img.enable_model_cpu_offload()  # Critical for low VRAM

    # 2. XTTS-v2 (Best open-source TTS, streaming-ready)
    pipe_tts = pipeline(
        "text-to-speech",
        model="coqui/XTTS-v2",
        torch_dtype=dtype,
        device=device
    )

    # 3. Groq & Claude clients
    from groq import Groq
    from anthropic import Anthropic
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    claude_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    return pipe_img, pipe_tts, groq_client, claude_client, device

# ==================== ULTRA-FAST FUNCTIONS ====================
async def generate_text_groq(prompt: str, client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: client.chat.completions.create(
        model="llama-3.2-90b-text-preview",  # fastest Groq model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=300
    ).choices[0].message.content)

async def enhance_text_claude(text: str, client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=400,
        temperature=0.7,
        messages=[{"role": "user", "content": f"Make this vivid, concise, and engaging:\n\n{text}"}]
    ).content[0].text)

def generate_image_turbo(prompt: str, pipe):
    image = pipe(
        prompt=prompt,
        num_inference_steps=1,           # Turbo = 1 step
        guidance_scale=0.0,              # Required for turbo
        height=512, width=512
    ).images[0]
    return image

def generate_audio_xtts(text: str, pipe_tts):
    # XTTS supports speaker conditioning — using default voice
    output = pipe_tts(text, speaker_wav=None, language="en", speed=1.0)
    audio = output["audio"][0]           # numpy array
    sampling_rate = output["sampling_rate"]
    return audio, sampling_rate

def create_video(image, audio_np, sr):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        sf.write(tmp_wav.name, audio_np, sr)
        audio_clip = AudioFileClip(tmp_wav.name)
        
        duration = audio_clip.duration
        video_clip = ImageClip(np.array(image)).set_duration(duration)
        video_clip = video_clip.set_audio(audio_clip)
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_mp4:
            video_clip.write_videofile(tmp_mp4.name, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            video_path = tmp_mp4.name
    
    # Cleanup
    audio_clip.close()
    video_clip.close()
    os.unlink(tmp_wav.name)
    return video_path

# ==================== MAIN APP ====================
def main():
    st.markdown('<h1 class="main-header">⚡ Lightning AI Agent</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.3rem; color: #666;'>Generate → Enhance → Audio/Video in <10 seconds</p>", unsafe_allow_html=True)
    st.markdown("<div class='speed-badge'>Optimized for speed • SDXL-Turbo + XTTS + Groq</div><br>", unsafe_allow_html=True)

    # Load models once
    try:
        pipe_img, pipe_tts, groq_client, claude_client, device = load_models()
    except Exception as e:
        st.error("Model loading failed. Check API keys and GPU availability.")
        st.stop()

    prompt = st.text_area(
        "Enter your idea (story, poem, ad, narration...)",
        placeholder="A cyberpunk cat wearing neon sunglasses rides a hoverboard through a rainy megacity at midnight...",
        height=120
    )

    if st.button("🚀 Generate Everything (Ultra Fast)", type="primary", use_container_width=True):
        if not prompt.strip():
            st.error("Please enter a prompt.")
            return

        progress = st.progress(0)
        status = st.empty()

        # Step 1: Generate + Enhance in parallel
        status.info("Generating & enhancing text...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        generated, enhanced = loop.run_until_complete(asyncio.gather(
            generate_text_groq(f"Write a short creative piece about: {prompt}", groq_client),
            generate_text_groq(f"Rewrite this to be more vivid and cinematic: {prompt}", groq_client)  # Simulate enhancement
        ))
        loop.close()

        st.success("Text ready!")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Generated Text")
            st.write(generated)
        with col2:
            st.subheader("Enhanced Text (Cinematic)")
            st.write(enhanced)
        progress.progress(30)

        # Step 2: Image (Turbo)
        status.info("Generating image (SDXL-Turbo)...")
        image = generate_image_turbo(f"cinematic, {enhanced}", pipe_img)
        st.image(image, caption="AI-Generated Image (1-step Turbo)", use_column_width=True)
        progress.progress(60)

        # Step 3: Audio (XTTS)
        status.info("Speaking with XTTS-v2...")
        audio_np, sr = generate_audio_xtts(enhanced, pipe_tts)
        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, audio_np, sr, format="WAV")
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/wav")
        progress.progress(80)

        # Step 4: Video
        status.info("Creating video...")
        video_path = create_video(image, audio_np, sr)
        st.video(video_path)
        
        # Download buttons
        with open(video_path, "rb") as f:
            st.download_button("Download Video MP4", f, "ai_agent_video.mp4", "video/mp4")
        progress.progress(100)
        st.success("Done in record time! ⚡")
        st.balloons()

        # Cleanup
        os.unlink(video_path)

if __name__ == "__main__":
    # Hide Streamlit menu & footer
    hide_menu = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_menu, unsafe_allow_html=True)
    
    main()
