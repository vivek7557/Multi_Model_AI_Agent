import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Generation",
    page_icon="🤖",
    layout="centered",  # Keeps content centered
    initial_sidebar_state="collapsed"
)

# Custom CSS for matching the reference UI + improved aesthetics
st.markdown("""
<style>
    /* Main container - narrower and centered */
    .main-container {
        max-width: 600px;
        margin: 2rem auto;
        padding: 1.5rem;
        background-color: #fafafa;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.4rem;
        color: #2d3748;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: left;
    }
    
    /* Navigation bar styling */
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
    
    /* Text area styling */
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
    
    /* Feature cards grid */
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
    
    /* Generate button styling */
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
    
    /* Footer styling */
    .footer {
        margin-top: 2rem;
        text-align: center;
        color: #718096;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="header-title">AI Generation</h1>', unsafe_allow_html=True)

# Navigation bar
st.markdown('<div class="nav-bar"><span class="nav-item">Home</span></div>', unsafe_allow_html=True)

# Content description input
st.markdown('<textarea class="content-input" placeholder="Describe the content you want to create..."></textarea>', unsafe_allow_html=True)

# Feature selection (Audio & Video)
st.markdown('<div class="feature-grid">', unsafe_allow_html=True)

# Audio card
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">🔊</div>
    <div class="feature-label">Audio</div>
</div>
""", unsafe_allow_html=True)

# Video card
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">▶️</div>
    <div class="feature-label">Video</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Generate button
st.markdown('<button class="generate-button">Generate</button>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Built with ❤️ using Streamlit</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
