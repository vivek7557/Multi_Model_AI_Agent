import streamlit as st
import requests
import json
import base64
from io import BytesIO

# -------------------------
# Streamlit App: Multi-Model AI Agent
# Converted from provided React TSX (pixel-preserving layout via HTML/CSS)
# -------------------------

st.set_page_config(page_title="Multi-Model AI Agent", page_icon="🎙️", layout="wide")

# --- Custom CSS to mimic Tailwind look from React version ---
st.markdown('''
<style>
:root{--bg1:#0f172a;--card-bg:rgba(255,255,255,0.06);--muted:#9f7aea;--accent1:#667eea;--accent2:#764ba2}
body{background:linear-gradient(135deg, #081329 0%, #2b0b29 100%);}
.main-card{background:linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));border:1px solid rgba(255,255,255,0.08);padding:28px;border-radius:20px}
.btn{background:linear-gradient(90deg,#4f46e5,#9333ea,#ec4899);color:white;padding:14px;border-radius:12px;border:none;font-weight:600}
.small-btn{background:rgba(255,255,255,0.06);color:white;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.08)}
.card{background:linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));padding:18px;border-radius:12px;border:1px solid rgba(255,255,255,0.04)}
.h1{font-size:38px;color:#fff;margin:0}
.h2{color:#ddd}
textarea, input, select{background:rgba(255,255,255,0.03);color:#efe8ff;border:1px solid rgba(255,255,255,0.06);padding:10px;border-radius:8px}
.progress{padding:12px;border-radius:10px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.04)}
.bad{background:rgba(220,38,38,0.12);border:1px solid rgba(220,38,38,0.18);color:#ffdddd;padding:12px;border-radius:10px}
.good{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.14);color:#ddffef;padding:12px;border-radius:10px}
.icon{vertical-align:middle}
.footer{color:#c7b3ff;font-size:13px}
</style>
''', unsafe_allow_html=True)

# --- Helper functions ---

def require_key(key, name):
    if not key:
        raise ValueError(f"{name} API key required for selected model")


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"error": "invalid json response"}

# --- Sidebar: API keys and instructions ---
with st.sidebar:
    st.header("🔑 API Configuration")
    st.markdown("---")
    openai_key = st.text_input("OpenAI API Key", type="password")
    anthropic_key = st.text_input("Anthropic (Claude) API Key", type="password")
    google_key = st.text_input("Google (Gemini) API Key", type="password")
    hf_key = st.text_input("Hugging Face API Key", type="password")
    st.markdown("---")
    elevenlabs_key = st.text_input("ElevenLabs API Key", type="password")
    did_key = st.text_input("D-ID API Key", type="password")

    st.markdown("\n---\nExamples of keys and links:\n- OpenAI: platform.openai.com\n- Claude: console.anthropic.com\n- Gemini: makersuite.google.com\n- Hugging Face: huggingface.co/settings/tokens\n- ElevenLabs: elevenlabs.io\n- D-ID: d-id.com")

# --- Page header (matches React layout) ---
st.markdown("<div style='display:flex;align-items:center;gap:16px;margin-bottom:18px'>"
            "<div style='width:56px;height:56px;background:linear-gradient(135deg,#c7b3ff,#ffd1f0);border-radius:12px;display:flex;align-items:center;justify-content:center'>🎙️</div>"
            f"<div><h1 class='h1'>Multi-Model AI Agent</h1><div class='h2'>Generate & enhance text with AI (OpenAI, Claude, Gemini, HF) → Convert to audio/video</div></div></div>", unsafe_allow_html=True)

# --- Main card container ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)

# Layout columns to mimic React grid
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#fff;margin-top:0'>Step 1: AI Text Generation/Enhancement</h3>")
    llm_model = st.selectbox("Select LLM Model", ("openai","claude","gemini","huggingface"), format_func=lambda x: {"openai":"OpenAI GPT-4","claude":"Claude (Anthropic)","gemini":"Google Gemini","huggingface":"Hugging Face (Llama 2)"}[x])
    enhance_mode = st.selectbox("Enhancement Mode", ("improve","script","narration","podcast","story","professional","casual"), format_func=lambda x: {"improve":"Improve and enhance","script":"Convert to video script","narration":"Convert to narration style","podcast":"Convert to podcast intro/outro","story":"Expand into a story","professional":"Make more professional","casual":"Make more casual and friendly"}[x])
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#fff;margin-top:0'>Step 2: Audio/Video Generation</h3>")
    tts_model = st.selectbox("Select TTS/Video Model", ("openai-tts","elevenlabs","did"), format_func=lambda x: {"openai-tts":"OpenAI TTS","elevenlabs":"ElevenLabs","did":"D-ID (Video)"}[x])
    voice_map = {
        'openai-tts': ["alloy","echo","fable","onyx","nova","shimmer"],
        'elevenlabs': ["Rachel","Drew","Clyde","Paul","Domi","Dave"],
        'did': ["en-US-JennyNeural","en-US-GuyNeural","en-GB-SoniaNeural"]
    }
    # Set default voice based on model
    default_voices = voice_map.get(tts_model)
    voice = st.selectbox("Select Voice", default_voices)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Text area
input_text = st.text_area("Enter Your Text (will be enhanced by AI)", height=160, placeholder="For example: 'Create an introduction for a podcast about AI technology'")
st.caption(f"{len(input_text)} characters")

# Helpers for API calls (adapted and hardened)

enhance_prompts = {
    "improve": "Improve and enhance the text",
    "script": "Convert to video script format",
    "narration": "Convert to narration style",
    "podcast": "Convert to podcast intro/outro",
    "story": "Expand into a story",
    "professional": "Make more professional",
    "casual": "Make more casual and friendly"
}

# encapsulated LLM generation function with safe checks

def generate_with_llm(text, model, keys, mode):
    prompt = f"{enhance_prompts[mode]}. Original text: \"{text}\". Provide only the enhanced text without any preamble or explanation."

    if model == "openai":
        require_key(keys.get('openai'), 'OpenAI')
        resp = requests.post("https://api.openai.com/v1/chat/completions",
                             headers={"Authorization":f"Bearer {keys.get('openai')}","Content-Type":"application/json"},
                             json={"model":"gpt-4","messages":[{"role":"system","content":"You are a helpful assistant that enhances text for audio/video content."},{"role":"user","content":prompt}],"max_tokens":500}, timeout=60)
        if resp.status_code != 200:
            raise Exception(safe_json(resp).get('error', resp.text))
        data = resp.json()
        return data['choices'][0]['message']['content']

    elif model == 'claude':
        require_key(keys.get('anthropic'), 'Claude (Anthropic)')
        resp = requests.post("https://api.anthropic.com/v1/messages",
                             headers={"x-api-key":keys.get('anthropic'),"anthropic-version":"2023-06-01","Content-Type":"application/json"},
                             json={"model":"claude-3-5-sonnet-20241022","max_tokens":500,"messages":[{"role":"user","content":prompt}]}, timeout=60)
        if resp.status_code != 200:
            raise Exception(safe_json(resp).get('error', resp.text))
        j = resp.json()
        # Claude returns different shapes; try common fields
        if isinstance(j.get('content'), list):
            return j['content'][0].get('text')
        return j.get('completion') or json.dumps(j)

    elif model == 'gemini':
        require_key(keys.get('google'), 'Google Gemini')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={keys.get('google')}"
        resp = requests.post(url, headers={"Content-Type":"application/json"}, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=60)
        if resp.status_code != 200:
            raise Exception(safe_json(resp).get('error', resp.text))
        j = resp.json()
        return j['candidates'][0]['content']['parts'][0]['text']

    elif model == 'huggingface':
        require_key(keys.get('huggingface'), 'Hugging Face')
        resp = requests.post("https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
                             headers={"Authorization":f"Bearer {keys.get('huggingface')}","Content-Type":"application/json"},
                             json={"inputs":prompt,"parameters":{"max_new_tokens":500}}, timeout=120)
        if resp.status_code != 200:
            raise Exception(safe_json(resp).get('error', resp.text))
        j = resp.json()
        # Many HF endpoints return text directly or as dict
        if isinstance(j, list) and 'generated_text' in j[0]:
            return j[0]['generated_text']
        if isinstance(j, dict) and 'generated_text' in j:
            return j['generated_text']
        return json.dumps(j)

    else:
        raise ValueError('Unsupported LLM')


# Audio/Video generation

def generate_audio_video(text, model, voice, keys):
    if model == 'openai-tts':
        require_key(keys.get('openai'), 'OpenAI')
        resp = requests.post("https://api.openai.com/v1/audio/speech",
                             headers={"Authorization":f"Bearer {keys.get('openai')}","Content-Type":"application/json"},
                             json={"model":"tts-1-hd","input":text,"voice":voice}, timeout=120)
        if resp.status_code != 200:
            data = safe_json(resp)
            raise Exception(data.get('error', data))
        return {'type':'audio','content':resp.content}

    elif model == 'elevenlabs':
        require_key(keys.get('elevenlabs'), 'ElevenLabs')
        # map voice id
        voice_map = {'Rachel':'21m00Tcm4TlvDq8ikWAM','Drew':'29vD33N1CtxCmqQRPOHJ','Clyde':'2EiwWnXFnvU5JabPnv8n','Paul':'5Q0t7uMcjvnagumLfvZi','Domi':'AZnzlk1XvdvUeBnXmlld','Dave':'CYw3kZ02Hs0563khs1Fj'}
        vid = voice_map.get(voice, list(voice_map.values())[0])
        resp = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}", headers={"xi-api-key":keys.get('elevenlabs'),"Content-Type":"application/json"}, json={"text":text,"model_id":"eleven_monolingual_v1"}, timeout=120)
        if resp.status_code != 200:
            raise Exception(safe_json(resp))
        return {'type':'audio','content':resp.content}

    elif model == 'did':
        require_key(keys.get('did'), 'D-ID')
        # D-ID wants Basic base64 auth: encode key with a trailing colon
        did_auth = base64.b64encode(f"{keys.get('did')}:".encode()).decode()
        resp = requests.post("https://api.d-id.com/talks",
                             headers={"Authorization":f"Basic {did_auth}","Content-Type":"application/json"},
                             json={"script":{"type":"text","input":text,"provider":{"type":"microsoft","voice_id":voice}},"source_url":"https://create-images-results.d-id.com/default-presenter.jpg"}, timeout=120)
        if resp.status_code not in (200,201):
            raise Exception(safe_json(resp))
        j = resp.json()
        # D-ID may return a result URL or an id you poll; we'll return whatever useful
        return {'type':'video','url':j.get('result_url') or j.get('id') or j}

    else:
        raise ValueError('Unsupported TTS/Video model')


# --- Generate button and processing logic ---

if st.button("✨ Generate with AI → Audio/Video ✨"):
    if not input_text.strip():
        st.error("Please enter text to convert")
    else:
        api_keys = {
            'openai': openai_key,
            'anthropic': anthropic_key,
            'google': google_key,
            'huggingface': hf_key,
            'elevenlabs': elevenlabs_key,
            'did': did_key
        }
        try:
            # Only validate API key for selected LLM
            if llm_model == 'openai' and not api_keys['openai']:
                raise Exception("OpenAI API key required for selected LLM")
            if llm_model == 'claude' and not api_keys['anthropic']:
                raise Exception("Claude API key required for selected LLM")
            if llm_model == 'gemini' and not api_keys['google']:
                raise Exception("Google Gemini API key required for selected LLM")
            if llm_model == 'huggingface' and not api_keys['huggingface']:
                raise Exception("Hugging Face API key required for selected LLM")

            with st.spinner('🧠 Generating/Enhancing text with AI...'):
                enhanced = generate_with_llm(input_text, llm_model, api_keys, enhance_mode)
                st.session_state['generated_text'] = enhanced
                st.success('✅ Text enhanced successfully!')

            # Only validate API key for selected TTS/Video model
            if tts_model == 'openai-tts' and not api_keys['openai']:
                raise Exception("OpenAI API key required for TTS")
            if tts_model == 'elevenlabs' and not api_keys['elevenlabs']:
                raise Exception("ElevenLabs API key required for TTS")
            if tts_model == 'did' and not api_keys['did']:
                raise Exception("D-ID API key required for Video generation")

            with st.spinner('🎙️ Converting text to audio/video...'):
                media = generate_audio_video(enhanced, tts_model, voice, api_keys)
                if media['type'] == 'audio':
                    st.session_state['media_type'] = 'audio'
                    st.audio(media['content'])
                    st.download_button('⬇️ Download Audio', data=media['content'], file_name='generated_audio.mp3', mime='audio/mpeg')
                else:
                    st.session_state['media_type'] = 'video'
                    if media.get('url') and isinstance(media.get('url'), str) and media.get('url').startswith('http'):
                        st.video(media.get('url'))
                        st.markdown(f"[Download Video]({media.get('url')})")
                    else:
                        st.write('Video generation response:', media)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.error(f"❌ Error: {str(e)}")

# --- Display generated text if present ---
if 'generated_text' in st.session_state and st.session_state['generated_text']:
    st.markdown("---")
    st.markdown("### 🧠 AI Enhanced Text")
    st.text_area('', st.session_state['generated_text'], height=160)

st.markdown("</div>", unsafe_allow_html=True)

# Footer info
st.markdown("<div style='margin-top:18px' class='footer'>Built from your React design — preserved layout & visuals.</div>", unsafe_allow_html=True)
