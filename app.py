import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Clean Streamlit UI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# Main title
st.title("✨ Clean Streamlit UI")
st.subheader("A simple, elegant interface")

# Simple form
with st.form("simple_form"):
    st.write("Enter some information below:")
    
    name = st.text_input("Name", placeholder="Enter your name")
    email = st.text_input("Email", placeholder="Enter your email")
    message = st.text_area("Message", placeholder="Enter your message here...")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        if name and email and message:
            st.success(f"Thank you {name}! Your message has been received.")
            st.balloons()
        else:
            st.error("Please fill in all fields.")

# Add some spacing
st.divider()

# Simple columns layout
col1, col2 = st.columns(2)

with col1:
    st.header("Features")
    st.write("- Simple and clean design")
    st.write("- Easy to use interface")
    st.write("- Responsive layout")
    st.write("- Minimal dependencies")

with col2:
    st.header("Usage")
    st.write("1. Fill in the form")
    st.write("2. Click submit")
    st.write("3. View results")
    st.write("4. Enjoy simplicity!")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit")