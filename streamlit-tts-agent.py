     	import streamlit as st
     2	import requests
     3	import json
     4	import base64
     5	from io import BytesIO
     6	import os
     7	import hashlib
     8	import time
     9	from datetime import datetime, timedelta
    10	import sqlite3
    11	from contextlib import contextmanager
    12	import logging
    13	from typing import Dict, Any, Optional
    14	import secrets
    15	
    16	# -------------------------------------------------------
    17	# Configuration & Constants
    18	# -------------------------------------------------------
    19	DB_PATH = "enterprise_ai_agent.db"
    20	LOG_LEVEL = logging.INFO
    21	LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    22	
    23	# Initialize logging
    24	logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    25	logger = logging.getLogger(__name__)
    26	
    27	# -------------------------------------------------------
    28	# Database Setup (for usage tracking only)
    29	# -------------------------------------------------------
    30	def init_db():
    31	    conn = sqlite3.connect(DB_PATH)
    32	    c = conn.cursor()
    33	    
    34	    # Usage logs (no user authentication needed)
    35	    c.execute('''
    36	        CREATE TABLE IF NOT EXISTS usage_logs (
    37	            id INTEGER PRIMARY KEY AUTOINCREMENT,
    38	            session_id TEXT NOT NULL,
    39	            service_type TEXT NOT NULL,
    40	            input_text TEXT,
    41	            output_text TEXT,
    42	            media_url TEXT,
    43	            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    44	            ip_address TEXT
    45	        )
    46	    ''')
    47	    
    48	    conn.commit()
    49	    conn.close()
    50	
    51	# -------------------------------------------------------
    52	# Session Management
    53	# -------------------------------------------------------
    54	def get_session_id():
    55	    if 'session_id' not in st.session_state:
    56	        st.session_state.session_id = secrets.token_hex(16)
    57	    return st.session_state.session_id
    58	
    59	def log_usage(session_id: str, service_type: str, input_text: str, output_text: str, media_url: str = None, ip_address: str = "unknown"):
    60	    conn = sqlite3.connect(DB_PATH)
    61	    c = conn.cursor()
    62	    c.execute('''
    63	        INSERT INTO usage_logs (session_id, service_type, input_text, output_text, media_url, ip_address)
    64	        VALUES (?, ?, ?, ?, ?, ?)
    65	    ''', (session_id, service_type, input_text, output_text, media_url, ip_address))
    66	    conn.commit()
    67	    conn.close()
    68	
    69	# -------------------------------------------------------
    70	# Enhanced Custom CSS with Modern Enterprise Design
    71	# -------------------------------------------------------
    72	st.markdown("""
    73	<style>
    74	    /* Import Google Fonts */
    75	    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    76	    
    77	    /* Global Styles */
    78	    * {
    79	        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    80	    }
    81	    
    82	    /* Main Background with Gradient Animation */
    83	    .stApp {
    84	        background: linear-gradient(-45deg, #1a0b2e, #2d1b69, #6b2d5c, #1a0b2e);
    85	        background-size: 400% 400%;
    86	        animation: gradientShift 15s ease infinite;
    87	    }
    88	    
    89	    @keyframes gradientShift {
    90	        0% { background-position: 0% 50%; }
    91	        50% { background-position: 100% 50%; }
    92	        100% { background-position: 0% 50%; }
    93	    }
    94	    
    95	    /* Header Styling */
    96	    .main-header {
    97	        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    98	        backdrop-filter: blur(10px);
    99	        border-radius: 20px;
   100	        padding: 32px;
   101	        margin-bottom: 30px;
   102	        border: 1px solid rgba(255,255,255,0.2);
   103	        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
   104	    }
   105	    
   106	    .header-icon {
   107	        width: 64px;
   108	        height: 64px;
   109	        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   110	        border-radius: 16px;
   111	        display: inline-flex;
   112	        align-items: center;
   113	        justify-content: center;
   114	        font-size: 36px;
   115	        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
   116	        animation: float 3s ease-in-out infinite;
   117	    }
   118	    
   119	    @keyframes float {
   120	        0%, 100% { transform: translateY(0px); }
   121	        50% { transform: translateY(-10px); }
   122	    }
   123	    
   124	    .main-title {
   125	        color: #ffffff;
   126	        font-size: 42px;
   127	        font-weight: 700;
   128	        margin: 0;
   129	        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
   130	    }
   131	    
   132	    .subtitle {
   133	        color: #c7b3ff;
   134	        font-size: 16px;
   135	        margin-top: 8px;
   136	    }
   137	    
   138	    /* Card Styles */
   139	    .glass-card {
   140	        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
   141	        backdrop-filter: blur(10px);
   142	        border-radius: 16px;
   143	        padding: 28px;
   144	        border: 1px solid rgba(255,255,255,0.18);
   145	        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
   146	        margin-bottom: 20px;
   147	        transition: all 0.3s ease;
   148	    }
   149	    
   150	    .glass-card:hover {
   151	        transform: translateY(-2px);
   152	        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
   153	        border-color: rgba(255,255,255,0.3);
   154	    }
   155	    
   156	    .step-card {
   157	        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
   158	        backdrop-filter: blur(10px);
   159	        border-radius: 14px;
   160	        padding: 24px;
   161	        border: 1px solid rgba(255,255,255,0.15);
   162	        margin-bottom: 16px;
   163	        position: relative;
   164	        overflow: hidden;
   165	    }
   166	    
   167	    .step-card::before {
   168	        content: '';
   169	        position: absolute;
   170	        top: 0;
   171	        left: 0;
   172	        right: 0;
   173	        height: 3px;
   174	        background: linear-gradient(90deg, #667eea, #764ba2);
   175	    }
   176	    
   177	    .section-title {
   178	        color: #ffffff;
   179	        font-size: 20px;
   180	        font-weight: 600;
   181	        margin-bottom: 20px;
   182	        display: flex;
   183	        align-items: center;
   184	        gap: 10px;
   185	    }
   186	    
   187	    .section-icon {
   188	        display: inline-block;
   189	        width: 32px;
   190	        height: 32px;
   191	        background: linear-gradient(135deg, #667eea, #764ba2);
   192	        border-radius: 8px;
   193	        text-align: center;
   194	        line-height: 32px;
   195	        font-size: 18px;
   196	    }
   197	    
   198	    /* Input Styles */
   199	    .stTextInput > div > div > input,
   200	    .stTextArea > div > div > textarea,
   201	    .stSelectbox > div > div > select {
   202	        background: rgba(255,255,255,0.08) !important;
   203	        color: #ffffff !important;
   204	        border: 1px solid rgba(255,255,255,0.15) !important;
   205	        border-radius: 10px !important;
   206	        padding: 12px !important;
   207	        font-size: 14px !important;
   208	        transition: all 0.3s ease !important;
   209	    }
   210	    
   211	    .stTextInput > div > div > input:focus,
   212	    .stTextArea > div > div > textarea:focus,
   213	    .stSelectbox > div > div > select:focus {
   214	        background: rgba(255,255,255,0.12) !important;
   215	        border-color: rgba(102, 126, 234, 0.6) !important;
   216	        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
   217	    }
   218	    
   219	    /* Button Styles */
   220	    .stButton > button {
   221	        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
   222	        color: white !important;
   223	        border: none !important;
   224	        border-radius: 12px !important;
   225	        padding: 16px 32px !important;
   226	        font-size: 16px !important;
   227	        font-weight: 600 !important;
   228	        width: 100%;
   229	        transition: all 0.3s ease !important;
   230	        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
   231	        text-transform: none !important;
   232	    }
   233	    
   234	    .stButton > button:hover {
   235	        transform: translateY(-2px) !important;
   236	        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6) !important;
   237	    }
   238	    
   239	    .stButton > button:active {
   240	        transform: translateY(0px) !important;
   241	    }
   242	    
   243	    /* Download Button */
   244	    .stDownloadButton > button {
   245	        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
   246	        color: white !important;
   247	        border: none !important;
   248	        border-radius: 10px !important;
   249	        padding: 12px 24px !important;
   250	        font-weight: 600 !important;
   251	        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
   252	    }
   253	    
   254	    /* Sidebar Styles */
   255	    [data-testid="stSidebar"] {
   256	        background: linear-gradient(180deg, rgba(26, 11, 46, 0.95) 0%, rgba(45, 27, 105, 0.95) 100%);
   257	        backdrop-filter: blur(10px);
   258	        border-right: 1px solid rgba(255,255,255,0.1);
   259	    }
   260	    
   261	    [data-testid="stSidebar"] .stTextInput > div > div > input {
   262	        background: rgba(255,255,255,0.06) !important;
   263	        border-color: rgba(255,255,255,0.1) !important;
   264	    }
   265	    
   266	    /* Success/Error Messages */
   267	    .stSuccess {
   268	        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%) !important;
   269	        border-left: 4px solid #10b981 !important;
   270	        border-radius: 8px !important;
   271	        color: #d1fae5 !important;
   272	        backdrop-filter: blur(10px);
   273	    }
   274	    
   275	    .stError {
   276	        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%) !important;
   277	        border-left: 4px solid #ef4444 !important;
   278	        border-radius: 8px !important;
   279	        color: #fecaca !important;
   280	        backdrop-filter: blur(10px);
   281	    }
   282	    
   283	    .stWarning {
   284	        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.2) 100%) !important;
   285	        border-left: 4px solid #fbbf24 !important;
   286	        border-radius: 8px !important;
   287	        color: #fef3c7 !important;
   288	        backdrop-filter: blur(10px);
   289	    }
   290	    
   291	    /* Spinner */
   292	    .stSpinner > div {
   293	        border-top-color: #667eea !important;
   294	    }
   295	    
   296	    /* Divider */
   297	    hr {
   298	        border-color: rgba(255,255,255,0.1) !important;
   299	        margin: 30px 0 !important;
   300	    }
   301	    
   302	    /* Audio Player */
   303	    audio {
   304	        width: 100%;
   305	        border-radius: 10px;
   306	        background: rgba(255,255,255,0.05);
   307	    }
   308	    
   309	    /* Caption Text */
   310	    .stCaption {
   311	        color: #a78bfa !important;
   312	        font-size: 13px !important;
   313	    }
   314	    
   315	    /* Footer */
   316	    .footer {
   317	        text-align: center;
   318	        color: #a78bfa;
   319	        font-size: 14px;
   320	        padding: 30px;
   321	        margin-top: 50px;
   322	        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
   323	        border-radius: 12px;
   324	        border: 1px solid rgba(255,255,255,0.08);
   325	    }
   326	    
   327	    /* Selectbox Dropdown */
   328	    [data-baseweb="select"] {
   329	        background: rgba(255,255,255,0.08) !important;
   330	    }
   331	    
   332	    /* Hide Streamlit Branding */
   333	    #MainMenu {visibility: hidden;}
   334	    footer {visibility: hidden;}
   335	    
   336	    /* Responsive */
   337	    @media (max-width: 768px) {
   338	        .main-title {
   339	            font-size: 28px;
   340	        }
   341	        .header-icon {
   342	            width: 48px;
   343	            height: 48px;
   344	            font-size: 28px;
   345	        }
   346	    }
   347	</style>
   348	""", unsafe_allow_html=True)
   349	
   350	# Initialize database
   351	init_db()
   352	
   353	# -------------------------------------------------------
   354	# Initialize Session State
   355	# -------------------------------------------------------
   356	if 'generated_text' not in st.session_state:
   357	    st.session_state.generated_text = ""
   358	if 'media_result' not in st.session_state:
   359	    st.session_state.media_result = None
   360	if 'api_keys' not in st.session_state:
   361	    st.session_state.api_keys = {}
   362	
   363	# Get session ID for usage tracking
   364	session_id = get_session_id()
   365	
   366	# -------------------------------------------------------
   367	# Sidebar API Keys - Enhanced Design
   368	# -------------------------------------------------------
   369	with st.sidebar:
   370	    # Sidebar Header
   371	    st.markdown("""
   372	    <div style='text-align: center; padding: 20px 0 30px 0; border-bottom: 1px solid rgba(255,255,255,0.1);'>
   373	        <div style='font-size: 40px; margin-bottom: 10px;'>🔑</div>
   374	        <h2 style='color: white; margin: 0; font-size: 24px; font-weight: 700;'>API Configuration</h2>
   375	        <p style='color: #a78bfa; font-size: 12px; margin-top: 8px;'>Enter only the keys you need</p>
   376	    </div>
   377	    """, unsafe_allow_html=True)
   378	    
   379	    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
   380	    
   381	    # Required Section - Claude
   382	    st.markdown("""
   383	    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(168, 85, 247, 0.15)); 
   384	                padding: 16px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3); margin-bottom: 20px;'>
   385	        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 12px;'>
   386	            <span style='font-size: 20px;'>⚡</span>
   387	            <span style='color: white; font-weight: 600; font-size: 15px;'>Required: Text Generation</span>
   388	        </div>
   389	        <div style='color: #c7b3ff; font-size: 11px; line-height: 1.5;'>
   390	            Enter your Claude API key to enable AI text generation
   391	        </div>
   392	    </div>
   393	    """, unsafe_allow_html=True)
   394	    
   395	    claude_key = st.text_input(
   396	        "Claude API Key (Anthropic)",
   397	        type="password",
   398	        key="claude_key",
   399	        placeholder="sk-ant-api03-...",
   400	        help="Get your key from console.anthropic.com"
   401	    )
   402	    
   403	    if claude_key:
   404	        st.markdown("""
   405	        <div style='background: rgba(16, 185, 129, 0.15); padding: 10px; border-radius: 8px; 
   406	                    border-left: 3px solid #10b981; margin-top: 8px;'>
   407	            <div style='color: #6ee7b7; font-size: 12px; display: flex; align-items: center; gap: 6px;'>
   408	                <span>✓</span> Claude API key configured
   409	            </div>
   410	        </div>
   411	        """, unsafe_allow_html=True)
   412	    
   413	    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
   414	    
   415	    # Optional Models Expander
   416	    with st.expander("🔧 Optional: Additional LLM Models", expanded=False):
   417	        st.markdown("""
   418	        <div style='color: #a78bfa; font-size: 11px; margin-bottom: 15px; line-height: 1.5;'>
   419	            Add more AI models for variety. These are completely optional.
   420	        </div>
   421	        """, unsafe_allow_html=True)
   422	        
   423	        openai_key = st.text_input(
   424	            "OpenAI GPT-4",
   425	            type="password",
   426	            key="openai_key",
   427	            placeholder="sk-...",
   428	            help="For GPT-4 text generation"
   429	        )
   430	        
   431	        google_key = st.text_input(
   432	            "Google Gemini",
   433	            type="password",
   434	            key="google_key",
   435	            placeholder="AIza...",
   436	            help="For Gemini text generation"
   437	        )
   438	        
   439	        hf_key = st.text_input(
   440	            "HuggingFace",
   441	            type="password",
   442	            key="hf_key",
   443	            placeholder="hf_...",
   444	            help="For Llama-2 text generation"
   445	        )
   446	    
   447	    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
   448	    st.markdown("<div style='border-top: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'></div>", unsafe_allow_html=True)
   449	    
   450	    # Audio/Video Section
   451	    st.markdown("""
   452	    <div style='background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(239, 68, 68, 0.15)); 
   453	                padding: 16px; border-radius: 12px; border: 1px solid rgba(236, 72, 153, 0.3); margin-bottom: 20px;'>
   454	        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 12px;'>
   455	            <span style='font-size: 20px;'>🎵</span>
   456	            <span style='color: white; font-weight: 600; font-size: 15px;'>Audio/Video Generation</span>
   457	        </div>
   458	        <div style='color: #fbbf24; font-size: 11px; line-height: 1.5;'>
   459	            Choose your preferred TTS provider
   460	        </div>
   461	    </div>
   462	    """, unsafe_allow_html=True)
   463	    
   464	    # TTS Provider Selection with custom styling
   465	    tts_choice = st.radio(
   466	        "Select Provider:",
   467	        ["OpenAI TTS (Recommended)", "ElevenLabs", "D-ID Video"],
   468	        help="Choose the service for converting text to audio/video",
   469	        label_visibility="visible"
   470	    )
   471	    
   472	    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
   473	    
   474	    # Show appropriate key input based on selection
   475	    if tts_choice == "OpenAI TTS (Recommended)":
   476	        if openai_key:
   477	            openai_tts_key = openai_key
   478	            st.markdown("""
   479	            <div style='background: rgba(16, 185, 129, 0.15); padding: 12px; border-radius: 8px; 
   480	                        border-left: 3px solid #10b981; margin-bottom: 15px;'>
   481	                <div style='color: #6ee7b7; font-size: 12px; display: flex; align-items: c<response clipped>
