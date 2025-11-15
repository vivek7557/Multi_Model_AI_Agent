import streamlit as st
import requests
import json
import base64
from io import BytesIO

# -------------------------------------------------------
# Streamlit UI Setup
# -------------------------------------------------------
st.set_page_config(page_title="Multi-Model AI Agent", page_icon="🎙️", layout="wide")

# -------------------------------------------------------
# Custom CSS
# -------------------------------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #081329 0%, #2b0b29 100%);
}

/* Main card */
.main-card {
    background: rgba(255,255,255,0.04);
    padding: 32px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Sub cards */
.card {
    background: rgba(255,255,255,0.03);
    padding: 22px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 12px;
}

/* Section headers */
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

/* Buttons */
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


# -------------------------------------------------------
# Sidebar API Keys
# -------------------------------------------------------
with st.sidebar:
    st.header("🔑 API Keys")

    openai_key = st.text_input("OpenAI API Key", type="password")
    anthropic_key = st.text_input("Claude API Key", type="password")
    google_key = st.text_input("Google Gemini API Key", type="password")
    hf_key = st.text_input("HuggingFace API Key", type="password")

    st.markdown("---")

    elevenlabs_key = st.text_input("ElevenLabs API Key", type="password")
    did_key = st.text_input("D-ID API Key", type="password")


# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.markdown("""
<div style='display:flex;align-items:center;gap:16px;margin-bottom:20px'>
    <div style='width:56px;height:56px;background:linear-gradient(135deg,#c7b3ff,#ffd1f0);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:32px;'>🎙️</div>
    <div>
        <h1 style='color:white;margin:0;font-size:36px;'>Multi-Model AI Agent</h1>
        <div style='color:#ccc'>Generate → Enhance → Convert to Audio/Video</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Wrap main content
st.markdown("<div class='main-card'>", unsafe_allow_html=True)


# -------------------------------------------------------
# Two-column React-like layout
# -------------------------------------------------------
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("<div class='card'><h3 class='section-title'>Step 1: Text Generation</h3>", unsafe_allow_html=True)

    llm_model = st.selectbox(
        "Select LLM",
        ["openai", "claude", "gemini", "huggingface"],
        format_func=lambda x: {
            "openai": "OpenAI GPT-4",
            "claude": "Claude 3.5 Sonnet",
            "gemini": "Google Gemini",
            "huggingface": "Llama-2 (HuggingFace)"
        }[x]
    )

    enhance_mode = st.selectbox(
        "Enhancement Type",
        ["improve", "script", "narration", "podcast", "story", "professional", "casual"]
    )

    st.markdown("</div>", unsafe_allow_html=True)


with col2:
    st.markdown("<div class='card'><h3 class='section-title'>Step 2: Audio / Video</h3>", unsafe_allow_html=True)

    tts_model = st.selectbox(
        "Target Output",
        ["openai-tts", "elevenlabs", "did"],
        format_func=lambda x: {
            "openai-tts": "OpenAI TTS",
            "elevenlabs": "ElevenLabs",
            "did": "D-ID Video"
        }[x]
    )

    voices = {
        "openai-tts": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "elevenlabs": ["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave"],
        "did": ["en-US-JennyNeural", "en-US-GuyNeural"]
    }

    voice = st.selectbox("Voice", voices[tts_model])

    st.markdown("</div>", unsafe_allow_html=True)


st.divider()


# -------------------------------------------------------
# Input text
# -------------------------------------------------------
input_text = st.text_area("Enter your text", height=150)
st.caption(f"{len(input_text)} characters")


# -------------------------------------------------------
# Prompts mapped
# -------------------------------------------------------
enhance_prompts = {
    "improve": "Improve writing and clarity.",
    "script": "Convert this into a video script.",
    "narration": "Rewrite in narrative storytelling style.",
    "podcast": "Rewrite as a podcast intro.",
    "story": "Expand into a fictional story.",
    "professional": "Rewrite formally and professionally.",
    "casual": "Rewrite casually and friendly."
}



# -------------------------------------------------------
# LLM PROCESSING FUNCTION (fixed for KeyError)
# -------------------------------------------------------
def generate_with_llm(text, model, keys, mode):

    prompt = f"{enhance_prompts[mode]}\n\nOriginal text:\n{text}"

    # -------------------- OPENAI --------------------
    if model == "openai":
        if not keys["openai"]:
            raise Exception("OpenAI API key required")

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {keys['openai']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a text enhancement AI."},
                    {"role": "user", "content": prompt},
                ],
            },
        )

        data = r.json()

        if "error" in data:
            raise Exception(f"OpenAI Error: {data['error']['message']}")

        if "choices" not in data or len(data["choices"]) == 0:
            raise Exception("OpenAI returned no output.")

        return data["choices"][0]["message"]["content"]


    # -------------------- CLAUDE --------------------
    if model == "claude":
        if not keys["anthropic"]:
            raise Exception("Claude API key required")

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": keys["anthropic"],
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        data = r.json()
        if "error" in data:
            raise Exception(data["error"]["message"])

        return data["content"][0]["text"]


    # -------------------- GEMINI --------------------
    if model == "gemini":
        if not keys["google"]:
            raise Exception("Gemini API key required")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys['google']}"

        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})

        data = r.json()

        if "error" in data:
            raise Exception(data["error"]["message"])

        return data["candidates"][0]["content"]["parts"][0]["text"]


    # -------------------- HUGGINGFACE --------------------
    if model == "huggingface":
        if not keys["huggingface"]:
            raise Exception("HuggingFace key required")

        r = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers={"Authorization": f"Bearer {keys['huggingface']}"},
            json={"inputs": prompt},
        )

        data = r.json()

        if isinstance(data, dict) and "error" in data:
            raise Exception(data["error"])

        return data[0]["generated_text"]



# -------------------------------------------------------
# TTS + VIDEO FUNCTION
# -------------------------------------------------------
def generate_media(text, model, voice, keys):

    # -------------------------------------------------------
    # OpenAI TTS
    # -------------------------------------------------------
    if model == "openai-tts":
        if not keys["openai"]:
            raise Exception("OpenAI API key required")

        r = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {keys['openai']}",
                "Content-Type": "application/json"
            },
            json={"model": "tts-1-hd", "voice": voice, "input": text}
        )

        return {"type": "audio", "content": r.content}

    # -------------------------------------------------------
    # ElevenLabs
    # -------------------------------------------------------
    if model == "elevenlabs":
        if not keys["elevenlabs"]:
            raise Exception("ElevenLabs API key required")

        voices_map = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Drew": "29vD33N1CtxCmqQRPOHJ",
            "Clyde": "2EiwWnXFnvU5JabPnv8n",
            "Paul": "5Q0t7uMcjvnagumLfvZi",
            "Domi": "AZnzlk1XvdvUeBnXmlld",
            "Dave": "CYw3kZ02Hs0563khs1Fj",
        }

        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voices_map[voice]}",
            headers={"xi-api-key": keys["elevenlabs"]},
            json={"text": text}
        )

        return {"type": "audio", "content": r.content}

    # -------------------------------------------------------
    # D-ID VIDEO
    # -------------------------------------------------------
    if model == "did":
        if not keys["did"]:
            raise Exception("D-ID API key required")

        did_auth = base64.b64encode(f"{keys['did']}:".encode()).decode()

        r = requests.post(
            "https://api.d-id.com/talks",
            headers={
                "Authorization": f"Basic {did_auth}",
                "Content-Type": "application/json"
            },
            json={
                "script": {
                    "type": "text",
                    "input": text,
                    "voice_id": voice,
                    "provider": {"type": "microsoft"}
                },
                "source_url": "https://create-images-results.d-id.com/default-presenter.jpg"
            }
        )

        data = r.json()

        return {"type": "video", "url": data.get("result_url")}



# -------------------------------------------------------
# MAIN BUTTON
# -------------------------------------------------------
if st.button("✨ Generate → Audio / Video"):

    if not input_text.strip():
        st.error("Enter some text first")
    else:
        keys = {
            "openai": openai_key,
            "anthropic": anthropic_key,
            "google": google_key,
            "huggingface": hf_key,
            "elevenlabs": elevenlabs_key,
            "did": did_key
        }

        # LLM Generation
        with st.spinner("🧠 Generating text..."):
            enhanced = generate_with_llm(input_text, llm_model, keys, enhance_mode)

        st.success("Text enhanced!")

        # Audio / Video Output
        with st.spinner("🎙️ Converting..."):
            media = generate_media(enhanced, tts_model, voice, keys)

        # Audio output
        if media["type"] == "audio":
            st.audio(media["content"])
            st.download_button("⬇️ Download Audio", media["content"], "audio.mp3")

        # Video output
        if media["type"] == "video":
            if media["url"]:
                st.video(media["url"])
                st.markdown(f"[Download Video]({media['url']})")
            else:
                st.error("D-ID returned no video URL.")


# Show enhanced text
if "enhanced" in locals():
    st.divider()
    st.subheader("🧠 Enhanced Text")
    st.text_area("", enhanced, height=160)

st.markdown("<div class='footer'>Built by Vivek YT • Multi-Model AI Agent</div>", unsafe_allow_html=True)
