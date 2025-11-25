import streamlit as st
import requests  # For potential API calls; placeholder for now
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Clean Web Search UI",
    page_icon="🔍",
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
    .search-results {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    .result-item {
        border-bottom: 1px solid #eee;
        padding: 1rem 0;
    }
    .result-title {
        font-size: 1.1rem;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .result-snippet {
        color: #666;
        margin-bottom: 0.5rem;
    }
    .result-url {
        font-size: 0.9rem;
        color: #007bff;
        text-decoration: none;
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
st.title("🔍 Clean Web Search UI")
st.markdown('<p>Simple and elegant search across the web</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Mock search function (replace with real API like Google Custom Search, DuckDuckGo, etc.)
def perform_web_search(query: str) -> List[Dict[str, str]]:
    # Placeholder mock results; in production, integrate with a search API
    mock_results = [
        {
            "title": f"Sample Result 1 for '{query}'",
            "url": "https://example.com/result1",
            "snippet": f"Brief description of the first result related to {query}. This is a mock snippet."
        },
        {
            "title": f"Sample Result 2 for '{query}'",
            "url": "https://example.com/result2",
            "snippet": f"Another relevant snippet about {query}. Expand with real data from API."
        },
        {
            "title": f"Sample Result 3 for '{query}'",
            "url": "https://example.com/result3",
            "snippet": f"Third result snippet demonstrating search across the web for {query}."
        }
    ]
    return mock_results

# Search Form
with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("search_form"):
        st.subheader("Web Search")
        search_query = st.text_input("Search Query", placeholder="Enter your search terms here...", help="Search across the web for anything!")
        
        submitted = st.form_submit_button("🔍 Search", use_container_width=True)
        
        if submitted:
            if search_query:
                with st.spinner("Searching the web..."):
                    results = perform_web_search(search_query)
                
                st.success(f"Found {len(results)} results for '{search_query}'.")
                st.balloons()
                
                # Display Results
                st.markdown('<div class="search-results">', unsafe_allow_html=True)
                st.markdown(f"<h3>Search Results</h3>", unsafe_allow_html=True)
                for result in results:
                    st.markdown(f'<div class="result-item">', unsafe_allow_html=True)
                    st.markdown(f'<a href="{result["url"]}" target="_blank" class="result-title">{result["title"]}</a>', unsafe_allow_html=True)
                    st.markdown(f'<p class="result-snippet">{result["snippet"]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<a href="{result["url"]}" target="_blank" class="result-url">Go to source</a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Note on integration
                with st.expander("ℹ️ Pro Tip: Integrate Real Search"):
                    st.markdown("""
                    To make this functional:
                    - Use DuckDuckGo API: `pip install duckduckgo-search`
                    - Or Google Custom Search JSON API.
                    - Replace `perform_web_search` with actual API call.
                    Example:
                    ```python
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        results = [r for r in ddgs.text(query, max_results=3)]
