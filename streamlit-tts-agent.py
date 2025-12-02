import streamlit as st
import os
from groq import Groq
import anthropic
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from diffusers import StableDiffusionPipeline
import torch
from moviepy.editor import VideoClip, ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image
import io
import tempfile

# Page config for modern look
st.set_page_config(
    page_title="Multi-Model AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main-header { font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
    .step-box { background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .stButton > button { background-color: #1f77b4; color: white; border-radius: 5px; }
    .stProgress > div > div > div > div { background-color: #1f77b4; }
    </style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def init_clients():
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # HF TTS setup
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    
    # HF Image Gen setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    image_pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16 if device == "cuda" else torch.float32)
    image_pipe = image_pipe.to(device)
    
    return groq_client, claude_client, processor, model, vocoder, image_pipe, device

# Text Generation with Groq
def generate_text(prompt, client):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Generate creative text based on: {prompt}"}],
        model="llama-3.1-70b-versatile",
        temperature=0.7,
        max_tokens=200
    )
    return chat_completion.choices[0].message.content

# Text Enhancement with Claude
def enhance_text(text, client):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=300,
        messages=[{"role": "user", "content": f"Enhance this text by summarizing and rephrasing for clarity: {text}"}]
    )
    return message.content[0].text

# Text to Audio with HF
def text_to_audio(text, processor, model, vocoder):
    inputs = processor(text=text, return_tensors="pt")
    with torch.no_grad():
        speech = model.generate_speech(inputs["input_ids"], speaker_embeddings=None, vocoder=vocoder)
    # Save to temp file
    temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    torch.save(speech.cpu().numpy(), temp_audio.name)
    return temp_audio.name

# Text to Image with HF
def text_to_image(prompt, pipe, device):
    image = pipe(prompt).images[0]
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return Image.open(img_buffer)

# Image + Audio to Video with MoviePy
def create_video(image, audio_path, duration):
    audio_clip = AudioFileClip(audio_path)
    if duration is None:
        duration = audio_clip.duration
    img_clip = ImageClip(image, duration=duration)
    video = img_clip.set_audio(audio_clip)
    temp_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    video.write_videofile(temp_video.name, fps=24)
    video.close()
    audio_clip.close()
    img_clip.close()
    return temp_video.name

# Main App
def main():
    st.markdown('<h1 class="main-header">🤖 Multi-Model AI Agent</h1>', unsafe_allow_html=True)
    st.markdown("Generate, enhance text, and convert to audio/video using Groq, Claude, Gemini (via HF), & Hugging Face.")
    
    # Sidebar for API keys (fallback if not in secrets)
    st.sidebar.title("🔑 API Keys")
    groq_key = st.sidebar.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    anthropic_key = st.sidebar.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))
    if not groq_key or not anthropic_key:
        st.sidebar.warning("Enter API keys to proceed.")
        return
    
    os.environ["GROQ_API_KEY"] = groq_key
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    
    # Tabs for workflow steps
    tab1, tab2, tab3, tab4 = st.tabs(["1. Input", "2. Generate", "3. Enhance", "4. Convert"])
    
    with tab1:
        st.markdown('<div class="step-box">Enter your prompt to start the agent.</div>', unsafe_allow_html=True)
        user_prompt = st.text_area("Prompt", placeholder="Describe a scene, story, or idea...", height=100)
        if st.button("🚀 Run Agent", type="primary"):
            if user_prompt:
                with st.spinner("Initializing models..."):
                    groq_client, claude_client, processor, model, vocoder, image_pipe, device = init_clients()
                
                # Step 2: Generate
                with tab2:
                    st.markdown('<div class="step-box">Generated Text (Groq Llama-3.1)</div>', unsafe_allow_html=True)
                    progress_bar = st.progress(0)
                    generated_text = generate_text(user_prompt, groq_client)
                    st.write(generated_text)
                    progress_bar.progress(33)
                
                # Step 3: Enhance
                with tab3:
                    st.markdown('<div class="step-box">Enhanced Text (Claude 3.5 Sonnet)</div>', unsafe_allow_html=True)
                    enhanced_text = enhance_text(generated_text, claude_client)
                    st.write(enhanced_text)
                    progress_bar.progress(66)
                
                # Step 4: Convert
                with tab4:
                    st.markdown('<div class="step-box">Conversions (Hugging Face)</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📢 Audio")
                        audio_path = text_to_audio(enhanced_text, processor, model, vocoder)
                        st.audio(audio_path)
                        with open(audio_path, "rb") as audio_file:
                            st.download_button("Download Audio", audio_file, file_name="enhanced_audio.wav")
                    
                    with col2:
                        st.subheader("🎥 Video")
                        # Generate image from enhanced text
                        image_prompt = f"A visual representation of: {enhanced_text[:100]}"
                        with st.spinner("Generating image..."):
                            image = text_to_image(image_prompt, image_pipe, device)
                            st.image(image, caption="Generated Image")
                        
                        # Create video
                        video_path = create_video(image, audio_path, None)
                        with open(video_path, "rb") as video_file:
                            st.download_button("Download Video", video_file, file_name="enhanced_video.mp4")
                    
                    progress_bar.progress(100)
                    st.success("Agent complete! 🎉")
                
                # Cleanup temp files
                for path in [audio_path, video_path]:
                    if 'path' in locals() and os.path.exists(path):
                        os.unlink(path)
            else:
                st.error("Please enter a prompt.")

if __name__ == "__main__":
    main()
