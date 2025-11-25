import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Generation",
    page_icon="🤖",
    layout="centered",  # Centered layout for cleaner appearance
    initial_sidebar_state="collapsed"
)

# Custom CSS for matching the reference UI
st.markdown("""
<style>
    /* Main container styling */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.8rem;
        color: #333;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: left;
    }
    
    /* Navigation bar styling */
    .nav-bar {
        background-color: #3a4750;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
    }
    
    .nav-item {
        color: white;
        font-size: 1.2rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 6px;
    }
    
    /* Text area styling */
    .content-input {
        width: 100%;
        padding: 1.2rem;
        border: 2px solid #d1d5da;
        border-radius: 8px;
        font-size: 1.1rem;
        color: #6b7280;
        background-color: white;
        margin-bottom: 2rem;
        transition: border-color 0.3s ease;
    }
    
    .content-input:focus {
        outline: none;
        border-color: #3b82f6;
    }
    
    /* Feature cards styling */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border: 2px solid #d1d5da;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 120px;
    }
    
    .feature-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #6b7280;
    }
    
    .feature-label {
        font-size: 1.1rem;
        font-weight: 500;
        color: #333;
    }
    
    /* Generate button styling */
    .generate-button {
        width: 100%;
        padding: 1.2rem;
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.3rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .generate-button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Footer styling */
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
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
