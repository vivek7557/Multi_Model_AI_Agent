import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Text to Audio & Video",
    page_icon="🎙️🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for layout and styling
st.markdown("""
<style>
    /* Main container */
    .main-container {
        max-width: 600px;
        margin: 2rem auto;
        padding: 1.5rem;
        background-color: #fafafa;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        position: relative;
    }

    /* Settings button */
    .settings-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background-color: #edf2f7;
        border: none;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        font-size: 0.95rem;
        color: #4a5568;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        transition: background-color 0.2s;
    }
    .settings-btn:hover {
        background-color: #e2e8f0;
    }

    /* Header */
    .header-title {
        font-size: 2.4rem;
        color: #2d3748;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: left;
    }

    /* Nav bar */
    .nav-bar {
        background-color: #4a5568;
        padding: 0.75rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
    }
    .nav-item {
        color: white;
        font-size: 1.1rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 6px;
    }

    /* Text area */
    .content-input {
        width: 100%;
        padding: 1rem;
        border: 2px solid #cbd5e0;
        border-radius: 8px;
        font-size: 1.05rem;
        color: #718096;
        background-color: white;
        margin-bottom: 1.5rem;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        resize: none;
        height: 100px;
    }
    .content-input:focus {
        outline: none;
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }

    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .feature-card {
        background-color: white;
        padding: 1rem;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .feature-card:hover {
        border-color: #4f46e5;
        box-shadow: 0 4px 8px rgba(79, 70, 229, 0.1);
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        color: #4a5568;
    }
    .feature-label {
        font-size: 1.05rem;
        font-weight: 500;
        color: #2d3748;
    }

    /* Generate button */
    .generate-button {
        width: 100%;
        padding: 1rem;
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(79, 70, 229, 0.2);
    }
    .generate-button:hover {
        background-color: #4338ca;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(79, 70, 229, 0.3);
    }

    /* Footer */
    .footer {
        margin-top: 2rem;
        text-align: center;
        color: #718096;
        font-size: 0.85rem;
    }

    /* Settings panel styling */
    .settings-panel {
        background-color: white;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .settings-panel label {
        display: block;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #2d3748;
        font-size: 0.95rem;
    }
    .settings-panel select, .settings-panel input {
        width: 100%;
        padding: 0.6rem;
        border: 1px solid #cbd5e0;
        border-radius: 6px;
        font-size: 0.95rem;
        background-color: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Settings button (top-right)
st.markdown('<button class="settings-btn">⚙️ Settings</button>', unsafe_allow_html=True)

# Settings panel - initially collapsed
with st.expander("", expanded=False):
    st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
    
    api_key = st.text_input("API Key", type="password", placeholder="Enter your API key")
    
    model = st.selectbox(
        "Model",
        options=["gpt-4o", "gpt-4", "claude-3.5", "llama-3.1", "gemini-1.5"],
        index=0
    )
    
    # Voice Type Selector (10 realistic voices)
    voice_type = st.selectbox(
        "Voice Type",
        options=[
            "Male - Neutral",
            "Female - Calm",
            "Male - Energetic",
            "Female - Professional",
            "Male - Deep & Slow",
            "Female - Friendly",
            "Male - Young & Casual",
            "Female - Authoritative",
            "Male - Storyteller",
            "Female - Singing Tone"
        ],
        index=0
    )
    
    # Video Style Selector (8 diverse styles)
    video_style = st.selectbox(
        "Video Style",
        options=[
            "Cinematic Short Film",
            "YouTube Tutorial",
            "Social Media Reel",
            "Corporate Explainer",
            "Animated Cartoon",
            "Documentary Narration",
            "Product Demo",
            "News Report Style"
        ],
        index=0
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Header — Changed to "Text to Audio & Video"
st.markdown('<h1 class="header-title">Text to Audio & Video</h1>', unsafe_allow_html=True)

# Nav bar
st.markdown('<div class="nav-bar"><span class="nav-item">Home</span></div>', unsafe_allow_html=True)

# Prompt input
prompt = st.text_area("", placeholder="Describe the content you want to create...", height=100)

# Feature cards
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔊</div>
        <div class="feature-label">Audio</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">▶️</div>
        <div class="feature-label">Video</div>
    </div>
    """, unsafe_allow_html=True)

# Generate button
if st.button("Generate", use_container_width=True, type="primary"):
    if not prompt.strip():
        st.warning("Please describe what you'd like to generate.")
    else:
        st.success(f"✅ Generation started! Using: {voice_type} voice & {video_style} style")
        st.balloons()

# Footer
st.markdown('<div class="footer">Built with ❤️ using Streamlit</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
