import streamlit as st
import requests
import json
import base64
from io import BytesIO

# ------------------------------------------
# Streamlit App — Pixel-Perfect React Layout
# ------------------------------------------

st.set_page_config(page_title="Multi-Model AI Agent", page_icon="🎙️", layout="wide")

# ------------------------------
# Custom Tailwind-like CSS
# ------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #081329 0%, #2b0b29 100%);
}

/* ----- Main Card ----- */
.main-card {
    background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    padding: 30px;
    border-radius: 20px;
}

/* ----- Cards ----- */
.card {
    background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    padding: 22px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 10px;
}

/* Section titles */
.section-title {
    color: #fff;
    margin: 0 0 14px 0;
    padding: 0;
    font-size: 20px;
    font-weight: 600;
}

textarea, input, select {
    background: rgba(255,255,255,0.03) !important;
    color: #efe8ff !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}

/* Button */
button[kind="primary"] {
    background: linear-gradient(90deg,#4f46e5,#9333ea,#ec4899) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: white !important;
}

/* Footer */
.footer {
    color:#c7b3ff;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Sidebar API Keys
# ------------------------------

with st.sidebar:
    st.header("🔑 API Configuration")

    openai_key = st.text_input("OpenAI API Key", type="password")
    anthropic_key = st.text_input("Anthropic (Claude) API Key", type="password")
    google_key = st.text_input("Google (Gemini) API Key", type="password")
    hf_key = st.text_input("Hugging Face API Key", type="password")

    st.markdown("---")

    elevenlabs_key = st.text_input("ElevenLabs API Key", type="password")
    did_key = st.text_input("D-ID API Key", type="password")

# ------------------------------
# Page Header
# ------------------------------

st.markdown("""
<div style='display:flex;align-items:center;gap:16px;margin-bottom:18px'>
    <div style='width:56px;height:56px;background:linear-gradient(135deg,#c7b3ff,#ffd1f0);border-radius:12px;display:flex;align-items:center;justify-content:center'>
        🎙️
    </div>
    <div>
        <h1 style='color:white;margin:0;font-size:36px;'>Multi-Model AI Agent</h1>
        <div style='color:#ddd'>Generate & enhance text with AI → Convert to audio or video</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='main-card'>", unsafe_allow_html=True)

# ------------------------------
# 2-column layout like React
# ------------------------------
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("<div class='card'><h3 class='section-title'>Step 1: AI Text Generation</h3>", unsafe_allow_html=True)

    llm_model = st.selectbox(
        "Select LLM Model",
        ["openai", "claude", "gemini", "huggingface"],
        format_func=lambda x: {
            "openai": "OpenAI GPT-4",
            "claude": "Claude (Anthropic)",
            "gemini": "Google Gemini",
            "huggingface": "Hugging Face (Llama 2)"
        }[x],
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
            "professional": "Make professional",
            "casual": "Make friendly & casual",
        }[x],
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3 class='section-title'>Step 2: Audio / Video Generation</h3>", unsafe_allow_html=True)

    tts_model = st.selectbox(
        "Select TTS/Video Model",
        ["openai-tts", "elevenlabs", "did"],
        format_func=lambda x: {
            "openai-tts": "OpenAI TTS",
            "elevenlabs": "ElevenLabs",
            "did": "D-ID (Video)",
        }[x],
    )

    voices = {
        "openai-tts": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "elevenlabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "did": ["en-US-JennyNeural", "en-US-GuyNeural", "en-GB-SoniaNeural"],
    }

    voice = st.selectbox("Select Voice", voices[tts_model])
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ------------------------------
# Text Input
# ------------------------------

input_text = st.text_area(
    "Enter your text (will be enhanced)",
    height=150,
)

st.caption(f"{len(input_text)} characters")


# ------------------------------
# PROMPTS
# ------------------------------
enhance_prompts = {
    "improve": "Improve and enhance the text",
    "script": "Convert to video script format",
    "narration": "Convert to narration style",
    "podcast": "Convert to podcast intro/outro",
    "story": "Expand into a story",
    "professional": "Make more professional",
    "casual": "Make friendly and conversational",
}

# ------------------------------
# LLM GENERATION
# ------------------------------

def generate_with_llm(text, model, keys, mode):
    prompt = f"{enhance_prompts[mode]}. Original text: \"{text}\". Provide only the final output."

    # --- OpenAI ---
    if model == "openai":
        if not keys["openai"]:
            raise Exception("Missing OpenAI API key")

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {keys['openai']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "Text enhancement assistant"},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        return r.json()["choices"][0]["message"]["content"]

    # --- Claude ---
    if model == "claude":
        if not keys["anthropic"]:
            raise Exception("Missing Claude API key")

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": keys["anthropic"],
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        return r.json()["content"][0]["text"]

    # --- Gemini ---
    if model == "gemini":
        if not keys["google"]:
            raise Exception("Missing Google Gemini API key")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['google']}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    # --- HuggingFace ---
    if model == "huggingface":
        if not keys["huggingface"]:
            raise Exception("Missing HuggingFace API key")

        r = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers={"Authorization": f"Bearer {keys['huggingface']}"},
            json={"inputs": prompt},
        )
        return r.json()[0]["generated_text"]

# ------------------------------
# TTS / VIDEO
# ------------------------------

def generate_media(text, model, voice, keys):

    # --- OpenAI TTS ---
    if model == "openai-tts":
        if not keys["openai"]:
            raise Exception("Missing OpenAI API key")

        r = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {keys['openai']}",
                "Content-Type": "application/json",
            },
            json={"model": "tts-1-hd", "input": text, "voice": voice},
        )
        return {"type": "audio", "content": r.content}

    # --- ElevenLabs ---
    if model == "elevenlabs":
        if not keys["elevenlabs"]:
            raise Exception("Missing ElevenLabs API key")

        voices_map = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Drew": "29vD33N1CtxCmqQRPOHJ",
            "Clyde": "2EiwWnXFnvU5JabPnv8n",
            "Paul": "5Q0t7uMcjvnagumLfvZi",
            "Domi": "AZnzlk1XvdvUeBnXmlld",
            "Dave": "CYw3kZ02Hs0563khs1Fj",
        }

        v = voices_map[voice]

        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{v}",
            headers={"xi-api-key": keys["elevenlabs"]},
            json={"text": text},
        )
        return {"type": "audio", "content": r.content}

    # --- D-ID VIDEO ---
    if model == "did":
        if not keys["did"]:
            raise Exception("Missing D-ID API key")

        did_auth = base64.b64encode(f"{keys['did']}:".encode()).decode()

        r = requests.post(
            "https://api.d-id.com/talks",
            headers={
                "Authorization": f"Basic {did_auth}",
                "Content-Type": "application/json",
            },
            json={
                "script": {
                    "type": "text",
                    "input": text,
                    "voice_id": voice,
                    "provider": {"type": "microsoft"},
                },
                "source_url": "https://create-images-results.d-id.com/default-presenter.jpg",
            },
        )

        return {"type": "video", "url": r.json().get("result_url")}

# ------------------------------
# Generate Button
# ------------------------------

if st.button("✨ Generate with AI → Audio/Video ✨"):
    if not input_text.strip():
        st.error("Please enter some text")
    else:
        keys = {
            "openai": openai_key,
            "anthropic": anthropic_key,
            "google": google_key,
            "huggingface": hf_key,
            "elevenlabs": elevenlabs_key,
            "did": did_key,
        }

        # --- LLM ---
        with st.spinner("🧠 Enhancing text with AI..."):
            enhanced = generate_with_llm(input_text, llm_model, keys, enhance_mode)
            st.success("Text enhanced!")

        # --- TTS/Video ---
        with st.spinner("🎙️ Converting to audio/video..."):
            media = generate_media(enhanced, tts_model, voice, keys)

        # AUDIO
        if media["type"] == "audio":
            st.audio(media["content"])
            st.download_button("⬇️ Download Audio", media["content"], "audio.mp3")

        # VIDEO
        if media["type"] == "video":
            if media["url"]:
                st.video(media["url"])
                st.markdown(f"[Download Video]({media['url']})")
            else:
                st.write(media)

# ------------------------------
# Show Enhanced Text
# ------------------------------

if "enhanced" in locals():
    st.divider()
    st.subheader("🧠 AI Enhanced Text")
    st.text_area("", enhanced, height=160)

st.markdown("<div class='footer'>Pixel-perfect UI recreated in Streamlit</div>", unsafe_allow_html=True)
