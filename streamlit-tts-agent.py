import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Clean Streamlit UI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.2rem;
        color: #666;
    }
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("✨ Clean Streamlit UI")
st.markdown('<p>Simple and elegant form interface</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Form
with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("clean_form"):
        st.subheader("Contact Form")
        name = st.text_input("Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        message = st.text_area("Message", placeholder="Type your message here", height=150)
        
        submitted = st.form_submit_button("Submit", use_container_width=True)
        
        if submitted:
            if name and email and message:
                st.success(f"Thank you {name}! Your message has been sent successfully.")
                st.balloons()
            else:
                st.error("Please fill in all fields")
    st.markdown('</div>', unsafe_allow_html=True)

# Features and instructions
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.subheader("📋 Features")
    st.markdown("""
    - Clean, minimalist design
    - Responsive layout
    - Form validation
    - Success feedback
    - Mobile-friendly
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.subheader("⚙️ How to Use")
    st.markdown("""
    1. Fill in your name
    2. Enter your email
    3. Type your message
    4. Click submit
    5. See success confirmation
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("Built with ❤️ using Streamlit", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
