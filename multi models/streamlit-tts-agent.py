import streamlit as st
import requests
import json
import base64
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Multi-Model AI Agent",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1);
    }
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

# Title
st.title("🎙️ Multi-Model AI Agent")
st.markdown("**Generate & enhance text with AI (OpenAI, Claude, Gemini, HF) → Convert to audio/video**")

# Sidebar for API Keys
with st.sidebar:
    st.header("🔑 API Configuration")
    
    with st.expander("LLM API Keys", expanded=False):
        openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key")
        anthropic_key = st.text_input("Anthropic (Claude) API Key", type="password", key="anthropic_key")
        google_key = st.text_input("Google (Gemini) API Key", type="password", key="google_key")
        hf_key = st.text_input("Hugging Face API Key", type="password", key="hf_key")
    
    with st.expander("TTS/Video API Keys", expanded=False):
        elevenlabs_key = st.text_input("ElevenLabs API Key", type="password", key="elevenlabs_key")
        did_key = st.text_input("D-ID API Key", type="password", key="did_key")
    
    st.divider()
    
    st.markdown("""
    ### 📚 Get API Keys:
    - [OpenAI](https://platform.openai.com)
    - [Claude](https://console.anthropic.com)
    - [Gemini](https://makersuite.google.com/app/apikey)
    - [Hugging Face](https://huggingface.co/settings/tokens)
    - [ElevenLabs](https://elevenlabs.io)
    - [D-ID](https://www.d-id.com)
    """)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧠 Step 1: AI Text Generation")
    
    llm_model = st.selectbox(
        "Select LLM Model",
        ["openai", "claude", "gemini", "huggingface"],
        format_func=lambda x: {
            "openai": "OpenAI GPT-4",
            "claude": "Claude (Anthropic)",
            "gemini": "Google Gemini",
            "huggingface": "Hugging Face (Llama 2)"
        }[x]
    )
    
    enhance_mode = st.selectbox(
        "Enhancement Mode",
        ["improve", "script", "narration", "podcast", "story", "professional", "casual"],
        format_func=lambda x: {
            "improve": "Improve and enhance",
            "script": "Convert to video script",
            "narration": "Convert to narration style",
            "podcast": "Convert to podcast intro/outro",
            "story": "Expand into a story",
            "professional": "Make more professional",
            "casual": "Make more casual and friendly"
        }[x]
    )

with col2:
    st.markdown("### 🎙️ Step 2: Audio/Video Generation")
    
    tts_model = st.selectbox(
        "Select TTS/Video Model",
        ["openai-tts", "elevenlabs", "did"],
        format_func=lambda x: {
            "openai-tts": "OpenAI TTS",
            "elevenlabs": "ElevenLabs",
            "did": "D-ID (Video)"
        }[x]
    )
    
    # Voice selection based on TTS model
    voice_options = {
        "openai-tts": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "elevenlabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "did": ["en-US-JennyNeural", "en-US-GuyNeural", "en-GB-SoniaNeural"]
    }
    
    voice = st.selectbox("Select Voice", voice_options[tts_model])

st.divider()

# Text input
input_text = st.text_area(
    "Enter Your Text (will be enhanced by AI)",
    height=150,
    placeholder="Enter a topic or text... For example: 'Create an introduction for a podcast about AI technology' or 'Make a professional video script about climate change'"
)

st.caption(f"{len(input_text)} characters")

# Functions for API calls
def generate_with_llm(text, model, api_keys, mode):
    """Generate/enhance text using selected LLM"""
    
    enhance_prompts = {
        "improve": "Improve and enhance the text",
        "script": "Convert to video script format",
        "narration": "Convert to narration style",
        "podcast": "Convert to podcast intro/outro",
        "story": "Expand into a story",
        "professional": "Make more professional",
        "casual": "Make more casual and friendly"
    }
    
    prompt = f"{enhance_prompts[mode]}. Original text: \"{text}\". Provide only the enhanced text without any preamble or explanation."
    
    try:
        if model == "openai":
            if not api_keys.get('openai'):
                raise ValueError("OpenAI API key required")
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_keys['openai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that enhances text for audio/video content."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        
        elif model == "claude":
            if not api_keys.get('anthropic'):
                raise ValueError("Anthropic API key required")
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_keys['anthropic'],
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            return response.json()['content'][0]['text']
        
        elif model == "gemini":
            if not api_keys.get('google'):
                raise ValueError("Google API key required")
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_keys['google']}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                }
            )
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        
        elif model == "huggingface":
            if not api_keys.get('huggingface'):
                raise ValueError("Hugging Face API key required")
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
                headers={
                    "Authorization": f"Bearer {api_keys['huggingface']}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 500}
                }
            )
            response.raise_for_status()
            return response.json()[0]['generated_text']
    
    except Exception as e:
        raise Exception(f"LLM Generation failed: {str(e)}")

def generate_audio_video(text, model, voice, api_keys):
    """Generate audio or video from text"""
    
    try:
        if model == "openai-tts":
            if not api_keys.get('openai'):
                raise ValueError("OpenAI API key required")
            
            response = requests.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {api_keys['openai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1-hd",
                    "input": text,
                    "voice": voice
                }
            )
            response.raise_for_status()
            return response.content, "audio"
        
        elif model == "elevenlabs":
            if not api_keys.get('elevenlabs'):
                raise ValueError("ElevenLabs API key required")
            
            voice_map = {
                'Rachel': '21m00Tcm4TlvDq8ikWAM',
                'Drew': '29vD33N1CtxCmqQRPOHJ',
                'Clyde': '2EiwWnXFnvU5JabPnv8n',
                'Paul': '5Q0t7uMcjvnagumLfvZi',
                'Domi': 'AZnzlk1XvdvUeBnXmlld',
                'Dave': 'CYw3kZ02Hs0563khs1Fj'
            }
            voice_id = voice_map.get(voice, voice_map['Rachel'])
            
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_keys['elevenlabs'],
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1"
                }
            )
            response.raise_for_status()
            return response.content, "audio"
        
        elif model == "did":
            if not api_keys.get('did'):
                raise ValueError("D-ID API key required")
            
            response = requests.post(
                "https://api.d-id.com/talks",
                headers={
                    "Authorization": f"Basic {api_keys['did']}",
                    "Content-Type": "application/json"
                },
                json={
                    "script": {
                        "type": "text",
                        "input": text,
                        "provider": {
                            "type": "microsoft",
                            "voice_id": voice
                        }
                    },
                    "source_url": "https://create-images-results.d-id.com/default-presenter.jpg"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get('result_url'), "video"
    
    except Exception as e:
        raise Exception(f"TTS/Video Generation failed: {str(e)}")

# Generate button
if st.button("✨ Generate with AI → Audio/Video ✨", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("Please enter text to convert")
    else:
        # Collect API keys
        api_keys = {
            'openai': openai_key,
            'anthropic': anthropic_key,
            'google': google_key,
            'huggingface': hf_key,
            'elevenlabs': elevenlabs_key,
            'did': did_key
        }
        
        try:
            # Step 1: Generate/Enhance text with LLM
            with st.spinner("🧠 Generating/Enhancing text with AI..."):
                enhanced_text = generate_with_llm(input_text, llm_model, api_keys, enhance_mode)
                st.session_state.generated_text = enhanced_text
            
            st.success("✅ Text enhanced successfully!")
            
            # Step 2: Generate audio/video
            with st.spinner("🎙️ Converting text to audio/video..."):
                media_data, media_type = generate_audio_video(enhanced_text, tts_model, voice, api_keys)
                st.session_state.audio_data = media_data
                st.session_state.media_type = media_type
            
            st.success("✅ Audio/Video generated successfully!")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results
if st.session_state.generated_text:
    st.divider()
    st.markdown("### 🧠 AI Enhanced Text")
    st.text_area("Generated Text", st.session_state.generated_text, height=150, disabled=True)

if st.session_state.audio_data:
    st.divider()
    st.markdown("### 🎵 Generated Content")
    
    if st.session_state.media_type == "audio":
        st.audio(st.session_state.audio_data, format="audio/mp3")
        
        # Download button
        st.download_button(
            label="⬇️ Download Audio",
            data=st.session_state.audio_data,
            file_name="generated_audio.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
    elif st.session_state.media_type == "video":
        st.video(st.session_state.audio_data)
        st.markdown(f"[Download Video]({st.session_state.audio_data})")

# Footer
st.divider()
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    1. **Enter API Keys** in the sidebar (click 'API Configuration')
    2. **Select your LLM model** (OpenAI, Claude, Gemini, or Hugging Face)
    3. **Choose enhancement mode** (how AI should process your text)
    4. **Select TTS/Video model** and voice
    5. **Enter your text** or topic
    6. **Click Generate** and wait for processing
    7. **Preview and download** your content
    
    **Example inputs:**
    - "Create an introduction for a podcast about AI technology"
    - "Make a professional video script about climate change"
    - "Write a casual story about space exploration"
    """)

with st.expander("💰 Cost Information"):
    st.markdown("""
    ### Free Tiers Available:
    - **Gemini**: Free tier with generous limits
    - **Hugging Face**: Free tier available
    
    ### Paid Services:
    - **OpenAI GPT-4**: ~$0.03 per 1K tokens
    - **OpenAI TTS**: $15 per 1M characters
    - **Claude**: Similar to OpenAI pricing
    - **ElevenLabs**: Free 10K chars/month, then $5/month
    - **D-ID**: Free trial, then $0.12-$0.30 per video
    """)
