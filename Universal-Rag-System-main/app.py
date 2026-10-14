import streamlit as st
import os
import uuid
import numpy as np
import time
import gc
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from services.document_service import extract_document_pages
from services.web_service import extract_website_text
from services.chunk_service import create_parent_child_chunks
from services.embedding_service import generate_embeddings
from services.vector_service import store_chunks, delete_collection, get_db_stats, cleanup_expired_collections
from services.retrieval_service import search_chunks
import services.llm_service
try:
    from services.llm_service import generate_answer, is_conversational_query, get_available_models
except ImportError:
    import importlib
    importlib.reload(services.llm_service)
    from services.llm_service import generate_answer, is_conversational_query, get_available_models

# Page Configuration
st.set_page_config(
    page_title="Conversational RAG System",
    layout="centered"
)

# Custom 3D Glassmorphic Aesthetic & Micro-animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

/* 3D Immersive Ambient Background */
.stApp {
    background: 
        radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.16) 0%, transparent 45%),
        radial-gradient(circle at 90% 85%, rgba(168, 85, 247, 0.14) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.08) 0%, transparent 55%),
        #070a12 !important;
    background-attachment: fixed !important;
    color: #f1f5f9 !important;
}

/* Sleek 3D Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090e1a 0%, #050810 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 10px 0 35px rgba(0, 0, 0, 0.7) !important;
}

.sidebar-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 3D Hero Title & Floating Badge */
.hero-container {
    text-align: center;
    padding: 1.5rem 0 1.2rem 0;
    position: relative;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.15) 100%);
    border: 1px solid rgba(129, 140, 248, 0.4);
    border-top: 1px solid rgba(255, 255, 255, 0.4);
    color: #c7d2fe;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 0.35rem 0.95rem;
    border-radius: 9999px;
    margin-bottom: 0.9rem;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    text-transform: uppercase;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    background: #38bdf8;
    border-radius: 50%;
    box-shadow: 0 0 12px #38bdf8;
    animation: pulseGlow 2s infinite ease-in-out;
}

@keyframes pulseGlow {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.5; }
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 15%, #cbd5e1 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.025em;
    margin-bottom: 0.35rem;
    filter: drop-shadow(0 4px 16px rgba(99, 102, 241, 0.35));
}

.hero-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    font-weight: 400;
    max-width: 620px;
    margin: 0 auto 1.8rem auto;
    line-height: 1.5;
}

/* 3D Glassmorphic HUD Status Box */
.status-box {
    background: linear-gradient(135deg, rgba(20, 28, 48, 0.75) 0%, rgba(11, 17, 31, 0.85) 100%) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(99, 102, 241, 0.28) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
    border-radius: 14px !important;
    padding: 1rem 1.4rem !important;
    color: #e2e8f0 !important;
    margin: 1.2rem 0 !important;
    box-shadow: 
        0 12px 30px -5px rgba(0, 0, 0, 0.6), 
        0 0 25px -4px rgba(99, 102, 241, 0.25), 
        inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    transform: translateY(0);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.status-box:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 18px 36px -5px rgba(0, 0, 0, 0.7), 
        0 0 35px -2px rgba(99, 102, 241, 0.4), 
        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
}

/* 3D Tactile Push Buttons */
.stButton>button {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #4338ca 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-top: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.25rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
    box-shadow: 
        0 4px 0 #312e81, 
        0 8px 22px rgba(79, 70, 229, 0.45), 
        inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
    transform: translateY(0) !important;
    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    box-shadow: 
        0 6px 0 #312e81, 
        0 14px 28px rgba(99, 102, 241, 0.55), 
        inset 0 1px 0 rgba(255, 255, 255, 0.45) !important;
    transform: translateY(-2px) !important;
}

.stButton>button:active {
    box-shadow: 
        0 1px 0 #312e81, 
        0 4px 12px rgba(79, 70, 229, 0.3), 
        inset 0 1px 2px rgba(0, 0, 0, 0.3) !important;
    transform: translateY(3px) !important;
}

/* 3D Glass Expander */
[data-testid="stExpander"] {
    background: linear-gradient(135deg, rgba(24, 33, 53, 0.55) 0%, rgba(13, 20, 36, 0.75) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 14px !important;
    box-shadow: 
        0 10px 30px -5px rgba(0, 0, 0, 0.5), 
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(14px) !important;
    overflow: hidden !important;
    transition: all 0.25s ease !important;
}

[data-testid="stExpander"]:hover {
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 
        0 14px 35px -5px rgba(0, 0, 0, 0.6), 
        0 0 22px rgba(99, 102, 241, 0.2) !important;
}

/* 3D Segmented Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13, 20, 36, 0.7) !important;
    border-radius: 11px !important;
    padding: 5px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.4) !important;
    gap: 6px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.1rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
}

/* 3D File Uploader Box */
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.25) 0%, rgba(15, 23, 42, 0.45) 100%) !important;
    border: 2px dashed rgba(99, 102, 241, 0.38) !important;
    border-radius: 12px !important;
    padding: 1.6rem !important;
    transition: all 0.25s ease !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: #818cf8 !important;
    background: linear-gradient(135deg, rgba(49, 46, 129, 0.25) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
    box-shadow: 0 0 25px rgba(99, 102, 241, 0.25) !important;
}

/* 3D Chat Messages with Depth */
[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, rgba(22, 30, 49, 0.75) 0%, rgba(13, 20, 36, 0.85) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 14px !important;
    padding: 1.15rem 1.4rem !important;
    margin-bottom: 1.1rem !important;
    box-shadow: 
        0 12px 28px -5px rgba(0, 0, 0, 0.5), 
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(14px) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatMessage"]:hover {
    transform: translateY(-1px);
    box-shadow: 
        0 16px 34px -5px rgba(0, 0, 0, 0.6), 
        0 0 20px rgba(99, 102, 241, 0.15) !important;
}

/* 3D Floating Chat Input Dock */
[data-testid="stChatInput"] {
    background: transparent !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    background: linear-gradient(135deg, rgba(19, 27, 44, 0.92) 0%, rgba(11, 17, 30, 0.98) 100%) !important;
    border: 1px solid rgba(99, 102, 241, 0.35) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
    border-radius: 14px !important;
    box-shadow: 
        0 12px 35px -5px rgba(0, 0, 0, 0.7), 
        0 0 25px rgba(99, 102, 241, 0.18), 
        inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
    color: #f8fafc !important;
    font-size: 0.96rem !important;
    transition: all 0.25s ease !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 
        0 16px 40px -5px rgba(0, 0, 0, 0.8), 
        0 0 35px rgba(99, 102, 241, 0.45), 
        inset 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

/* 3D Selectbox & Sliders in Sidebar */
[data-baseweb="select"] > div {
    background: rgba(19, 27, 44, 0.8) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

/* Custom 3D Neon Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #080c14;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #4f46e5 0%, #312e81 100%);
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #6366f1 0%, #4338ca 100%);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    [data-testid="stAppViewBlockContainer"], .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.2rem !important;
        padding-bottom: 3.5rem !important;
    }
    
    .hero-title {
        font-size: 1.8rem !important;
    }
    
    .hero-subtitle {
        font-size: 0.88rem !important;
        margin-bottom: 1.2rem !important;
    }
    
    .status-box {
        padding: 0.75rem 0.95rem !important;
        font-size: 0.85rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Read Groq API Key silently from .env or Streamlit Secrets
api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

# Initialize session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize collection name (rag_<timestamp>_<session_id_suffix>)
if "collection_name" not in st.session_state:
    st.session_state.collection_name = f"rag_{int(time.time())}_{st.session_state.session_id[:8]}"
    # Auto-cleanup expired collections (>2 hours old) on spin-up
    cleanup_expired_collections(max_age_seconds=7200)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_source" not in st.session_state:
    st.session_state.indexed_source = "None"
if "source_name" not in st.session_state:
    st.session_state.source_name = ""
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0
if "db_stats" not in st.session_state:
    st.session_state.db_stats = get_db_stats(st.session_state.collection_name)
if "advanced_expanded" not in st.session_state:
    st.session_state.advanced_expanded = False

# Fetch current database statistics from session state
db_stats = st.session_state.db_stats

# ----------------------------------------------------
# SIDEBAR: CONFIGURATIONS
# ----------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'><span style='color: #818cf8;'>✦</span> SYSTEM CONTROL</div>", unsafe_allow_html=True)
    
    available_models = get_available_models(api_key)
    model_choice = st.selectbox(
        "Model Selection",
        options=available_models,
        index=0,
        help="Select the model for response generation."
    )
    
    # Group settings inside collapsible expander to avoid sidebar clutter
    with st.expander("Advanced Settings", expanded=st.session_state.advanced_expanded):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05
        )
        
        timeout_val = st.slider(
            "Max Processing Timeout (s)",
            min_value=30,
            max_value=600,
            value=120,
            step=10,
            help="Maximum time allowed for PDF parsing before warning."
        )
        
        max_chunk_val = st.slider(
            "Max Chunk Limit",
            min_value=100,
            max_value=20000,
            value=3000,
            step=100,
            help="Maximum number of text chunks allowed per ingested document."
        )
        
        use_hybrid = st.checkbox("Use Hybrid Search", value=True)
        use_reranker = st.checkbox("Use Cross-Encoder Re-ranking", value=False)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("Reset Session Context"):
        # Purge current session collection and data states
        delete_collection(st.session_state.collection_name)
        st.session_state.messages = []
        st.session_state.indexed_source = "None"
        st.session_state.source_name = ""
        st.session_state.chunk_count = 0
        st.session_state.db_stats = {"chunks": 0, "pdfs": 0, "websites": 0}
        st.session_state.advanced_expanded = False
        st.session_state.collection_name = f"rag_{int(time.time())}_{st.session_state.session_id[:8]}"
        gc.collect()
        st.success("Session context reset complete.")
        st.rerun()

# ----------------------------------------------------
# MAIN CONTENT PANEL
# ----------------------------------------------------

# 3D Hero Title & Floating Badge
st.markdown("""
<div class='hero-container'>
    <div class='hero-badge'><span class='pulse-dot'></span> Universal RAG Engine • Groq Accelerated</div>
    <div class='hero-title'>Conversational Intelligence</div>
    <div class='hero-subtitle'>Explore and query documents, reports, and web sources with real-time vector synthesis.</div>
</div>
""", unsafe_allow_html=True)

if not api_key or not api_key.strip():
    st.error("GROQ_API_KEY is missing from environment. Please verify your .env configuration.")

# COLLAPSIBLE INGESTION SECTION (Expands by default if database is empty)
is_db_empty = (db_stats['chunks'] == 0)
with st.expander("Ingest Document or Web Page", expanded=is_db_empty):
    tab_pdf, tab_web = st.tabs(["Document File", "Website URL"])
    
    # Document Tab
    with tab_pdf:
        uploaded_file = st.file_uploader(
            "Upload File",
            type=["pdf", "txt", "docx", "csv", "xlsx", "xls", "json"],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        
        # Reset database immediately if document was removed by user
        if st.session_state.indexed_source == "Document" and not uploaded_file:
            delete_collection(st.session_state.collection_name)
            st.session_state.messages = []
            st.session_state.indexed_source = "None"
            st.session_state.source_name = ""
            st.session_state.chunk_count = 0
            st.session_state.db_stats = {"chunks": 0, "pdfs": 0, "websites": 0}
            st.session_state.advanced_expanded = False
            st.session_state.collection_name = f"rag_{int(time.time())}_{st.session_state.session_id[:8]}"
            gc.collect()
            st.rerun()
            
        if uploaded_file:
            # File Size validation check (Max 30 MB)
            MAX_FILE_SIZE = 30 * 1024 * 1024
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error("File size exceeds the 30 MB limit. Please upload a smaller file.")
            else:
                if st.button("Index Document", key="btn_pdf"):
                    try:
                        t_start_processing = time.time()
                        
                        # Purge old session collection before replacing
                        delete_collection(st.session_state.collection_name)
                        st.session_state.messages = []
                        st.session_state.collection_name = f"rag_{int(time.time())}_{st.session_state.session_id[:8]}"
                        cleanup_expired_collections(max_age_seconds=7200) # Maintenance purge
                        gc.collect()
                        
                        progress_placeholder = st.empty()
                        
                        # Set initial stages progress parameters (without OCR)
                        step_states = {
                            "extract": {"name": "Extracting text", "status": "pending", "pct": 0, "detail": ""},
                            "chunk": {"name": "Chunking", "status": "pending", "pct": 0, "detail": ""},
                            "embed": {"name": "Generating embeddings", "status": "pending", "pct": 0, "detail": ""},
                            "index": {"name": "Indexing vectors", "status": "pending", "pct": 0, "detail": ""}
                        }
                        
                        def render_progress_text(states):
                            lines = ["**✓ File uploaded**\n"]
                            for key, step in states.items():
                                name = step["name"]
                                status = step["status"]
                                pct = step["pct"]
                                detail = step["detail"]
                                
                                if status == "pending":
                                    lines.append(f"⏳ {name}...")
                                elif status == "running":
                                    filled = int(pct / 10)
                                    bar = "█" * filled + "░" * (10 - filled)
                                    lines.append(f"🔄 **{name}...**\n`{bar} {pct}%` {detail}")
                                elif status == "done":
                                    lines.append(f"✓ {name} {detail}")
                                elif status == "skipped":
                                    lines.append(f"✓ {name} (Skipped)")
                            return "\n\n".join(lines)
                        
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        # Run document extractor
                        step_states["extract"]["status"] = "running"
                        step_states["extract"]["pct"] = 50
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        pages = extract_document_pages(
                            uploaded_file,
                            filename=uploaded_file.name,
                            timeout_seconds=timeout_val
                        )
                        
                        # Finalize extraction phase statuses
                        step_states["extract"]["status"] = "done"
                        step_states["extract"]["pct"] = 100
                        step_states["extract"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        # Stage 3: Chunking
                        step_states["chunk"]["status"] = "running"
                        step_states["chunk"]["pct"] = 50
                        step_states["chunk"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        total_extracted_pages = len(pages)
                        chunks_list, metadata_list = create_parent_child_chunks(
                            pages=pages,
                            source_type="pdf", # Treated as pdf internally for status logs compatibility
                            filename=uploaded_file.name
                        )
                        
                        # Guard against empty chunk generation
                        if len(chunks_list) == 0:
                            delete_collection(st.session_state.collection_name)
                            st.error("No extractable digital text layers found in this document. Since OCR is disabled, purely scanned images or empty documents cannot be processed. Please upload a document containing digital text.")
                            st.stop()
                            
                        # Max chunk limit threshold verification
                        if len(chunks_list) > max_chunk_val:
                            delete_collection(st.session_state.collection_name)
                            st.session_state.advanced_expanded = True
                            st.error(
                                f"⚠️ The uploaded document yields {len(chunks_list)} chunks, which exceeds your current limit of {max_chunk_val} chunks.\n\n"
                                f"We have automatically opened the **Advanced Settings** expander in the left sidebar's Control Panel for you. "
                                f"Please adjust the **Max Chunk Limit** to at least **{len(chunks_list)}** chunks and rebuild the index."
                            )
                            st.stop()
                            
                        step_states["chunk"]["status"] = "done"
                        step_states["chunk"]["pct"] = 100
                        step_states["chunk"]["detail"] = f"({len(chunks_list)} chunks)"
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        # Stage 4: Embeddings
                        step_states["embed"]["status"] = "running"
                        step_states["embed"]["pct"] = 0
                        step_states["embed"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        def embed_progress(completed, total):
                            pct_embed = int((completed / total) * 100)
                            step_states["embed"]["pct"] = pct_embed
                            step_states["embed"]["detail"] = f"({completed}/{total} generated)"
                            progress_placeholder.markdown(render_progress_text(step_states))
                            
                        embeddings = generate_embeddings(chunks_list, progress_callback=embed_progress)
                        
                        step_states["embed"]["status"] = "done"
                        step_states["embed"]["pct"] = 100
                        step_states["embed"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        # Stage 5: Indexing Vectors
                        step_states["index"]["status"] = "running"
                        step_states["index"]["pct"] = 0
                        step_states["index"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        store_chunks(st.session_state.collection_name, chunks_list, embeddings, metadata_list)
                        
                        step_states["index"]["status"] = "done"
                        step_states["index"]["pct"] = 100
                        step_states["index"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        time.sleep(0.5)
                        progress_placeholder.empty()
                        
                        # Save session active context profiles
                        st.session_state.indexed_source = "Document"
                        st.session_state.source_name = uploaded_file.name
                        st.session_state.chunk_count = len(chunks_list)
                        st.session_state.db_stats = {"chunks": len(chunks_list), "pdfs": 1, "websites": 0}
                        st.session_state.advanced_expanded = False
                        
                        processing_time = time.time() - t_start_processing
                        st.markdown(f"""
                        <div style="background-color:#1e293b; color:#e2e8f0; border-radius:8px; border:1px solid #334155; padding:1.2rem; margin-bottom:1.5rem;">
                            <span style="color:#22c55e; font-weight:bold; font-size:1.05rem;">✓ Document processed successfully</span><br><br>
                            Pages: <b>{total_extracted_pages}</b><br>
                            Chunks: <b>{len(chunks_list)}</b><br>
                            Processing time: <b>{processing_time:.1f} s</b><br><br>
                            <span style="color:#3b82f6; font-weight:600;">Ready for questions.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        time.sleep(1.5)
                        st.rerun()
                        
                    except TimeoutError:
                        progress_placeholder.empty()
                        delete_collection(st.session_state.collection_name)
                        st.error("This document is too complex to process efficiently. Please upload a smaller or cleaner PDF.")
                    except Exception as e:
                        progress_placeholder.empty()
                        delete_collection(st.session_state.collection_name)
                        st.error(f"Failed to process PDF: {str(e)}")
                        
    # Website Tab
    with tab_web:
        web_url = st.text_input("Web URL", placeholder="https://example.com/article", label_visibility="collapsed")
        
        if st.button("Index Web Page", key="btn_web"):
            if web_url.strip():
                try:
                    t_start_processing = time.time()
                    
                    # Delete collection metadata before replacing
                    delete_collection(st.session_state.collection_name)
                    st.session_state.messages = []
                    st.session_state.collection_name = f"rag_{int(time.time())}_{st.session_state.session_id[:8]}"
                    cleanup_expired_collections(max_age_seconds=7200) # Maintenance purge
                    gc.collect()
                    
                    progress_placeholder = st.empty()
                    
                    # Web visual status tracker
                    step_states = {
                        "extract": {"name": "Scraping page contents", "status": "pending", "pct": 0, "detail": ""},
                        "chunk": {"name": "Chunking", "status": "pending", "pct": 0, "detail": ""},
                        "embed": {"name": "Generating embeddings", "status": "pending", "pct": 0, "detail": ""},
                        "index": {"name": "Indexing vectors", "status": "pending", "pct": 0, "detail": ""}
                    }
                    
                    def render_progress_text(states):
                        lines = ["**✓ URL provided**\n"]
                        for key, step in states.items():
                            name = step["name"]
                            status = step["status"]
                            pct = step["pct"]
                            detail = step["detail"]
                            
                            if status == "pending":
                                lines.append(f"⏳ {name}...")
                            elif status == "running":
                                filled = int(pct / 10)
                                bar = "█" * filled + "░" * (10 - filled)
                                lines.append(f"🔄 **{name}...**\n`{bar} {pct}%` {detail}")
                            elif status == "done":
                                lines.append(f"✓ {name} {detail}")
                        return "\n\n".join(lines)
                        
                    step_states["extract"]["status"] = "running"
                    step_states["extract"]["pct"] = 50
                    progress_placeholder.markdown(render_progress_text(step_states))
                    
                    web_text = extract_website_text(web_url)
                    if web_text and not web_text.startswith("Error:"):
                        web_text_clean = web_text.strip()
                        
                        # Guard against zero-character extractable HTML parsed text
                        if not web_text_clean:
                            progress_placeholder.empty()
                            delete_collection(st.session_state.collection_name)
                            st.error("Scraped website contains no extractable text content (cookie wall, redirect protection, or empty page).")
                            st.stop()
                            
                        step_states["extract"]["status"] = "done"
                        step_states["extract"]["pct"] = 100
                        
                        # Stage 2: Chunking
                        step_states["chunk"]["status"] = "running"
                        step_states["chunk"]["pct"] = 50
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        # Use unified parent-child chunking for web pages
                        web_pages = [{"page": 1, "text": web_text_clean}]
                        web_chunks, metadata = create_parent_child_chunks(
                            pages=web_pages,
                            source_type="website",
                            filename=web_url
                        )
                        
                        # Guard against empty chunk generation
                        if not web_chunks:
                            progress_placeholder.empty()
                            delete_collection(st.session_state.collection_name)
                            st.error("Scraped website content resulted in 0 text chunks.")
                            st.stop()
                            
                        # Validate chunks limit
                        if len(web_chunks) > max_chunk_val:
                            delete_collection(st.session_state.collection_name)
                            st.session_state.advanced_expanded = True
                            st.error(
                                f"⚠️ The scraped website yields {len(web_chunks)} chunks, which exceeds your current limit of {max_chunk_val} chunks.\n\n"
                                f"We have automatically opened the **Advanced Settings** expander in the left sidebar's Control Panel for you. "
                                f"Please adjust the **Max Chunk Limit** to at least **{len(web_chunks)}** chunks and rebuild the index."
                            )
                            st.stop()
                            
                        step_states["chunk"]["status"] = "done"
                        step_states["chunk"]["pct"] = 100
                        step_states["chunk"]["detail"] = f"({len(web_chunks)} chunks)"
                        
                        # Stage 3: Embeddings
                        step_states["embed"]["status"] = "running"
                        step_states["embed"]["pct"] = 0
                        step_states["embed"]["detail"] = ""
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        def embed_progress(completed, total):
                            pct_embed = int((completed / total) * 100)
                            step_states["embed"]["pct"] = pct_embed
                            step_states["embed"]["detail"] = f"({completed}/{total} generated)"
                            progress_placeholder.markdown(render_progress_text(step_states))
                            
                        embeddings = generate_embeddings(web_chunks, progress_callback=embed_progress)
                        
                        step_states["embed"]["status"] = "done"
                        step_states["embed"]["pct"] = 100
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        # Stage 4: Indexing Vectors
                        step_states["index"]["status"] = "running"
                        step_states["index"]["pct"] = 0
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        store_chunks(st.session_state.collection_name, web_chunks, embeddings, metadata)
                        
                        step_states["index"]["status"] = "done"
                        step_states["index"]["pct"] = 100
                        progress_placeholder.markdown(render_progress_text(step_states))
                        
                        time.sleep(0.5)
                        progress_placeholder.empty()
                        
                        st.session_state.indexed_source = "Website"
                        st.session_state.source_name = web_url
                        st.session_state.chunk_count = len(web_chunks)
                        st.session_state.db_stats = {"chunks": len(web_chunks), "pdfs": 0, "websites": 1}
                        st.session_state.advanced_expanded = False
                        
                        processing_time = time.time() - t_start_processing
                        st.markdown(f"""
                        <div style="background-color:#1e293b; color:#e2e8f0; border-radius:8px; border:1px solid #334155; padding:1.2rem; margin-bottom:1.5rem;">
                            <span style="color:#22c55e; font-weight:bold; font-size:1.05rem;">✓ Website indexed successfully</span><br><br>
                            Chunks: <b>{len(web_chunks)}</b><br>
                            Processing time: <b>{processing_time:.1f} s</b><br><br>
                            <span style="color:#3b82f6; font-weight:600;">Ready for questions.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        progress_placeholder.empty()
                        delete_collection(st.session_state.collection_name)
                        st.error(f"Failed to index website: {web_text}")
                except Exception as e:
                    progress_placeholder.empty()
                    delete_collection(st.session_state.collection_name)
                    st.error(f"Failed to process website: {str(e)}")

# Active status indicator (3D HUD)
if db_stats['chunks'] > 0:
    source_type = "Document" if st.session_state.indexed_source == "Document" else "Website"
    if st.session_state.indexed_source == "None":
        source_type = "Previous Session"
        st.session_state.source_name = "Loaded session vectors"
        st.session_state.chunk_count = db_stats['chunks']
        
    st.markdown(f"""
    <div class='status-box'>
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>
            <div>
                <span style='color: #818cf8; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em;'>Active Knowledge Base</span>
                <div style='font-size: 1.05rem; font-weight: 600; color: #f8fafc; margin-top: 2px;'>{st.session_state.source_name} <span style='font-size: 0.8rem; color: #94a3b8; font-weight: 400;'>({source_type})</span></div>
            </div>
            <div style='background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 8px; padding: 0.35rem 0.75rem; text-align: center;'>
                <span style='font-size: 0.7rem; color: #a5b4fc; display: block; font-weight: 600;'>CHUNKS INDEXED</span>
                <span style='font-size: 1.15rem; font-weight: 700; color: #ffffff;'>{st.session_state.chunk_count}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class='status-box' style='border-color: rgba(245, 158, 11, 0.35); background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(15, 23, 42, 0.85) 100%);'>
        <div style='display: flex; align-items: center; gap: 10px; color: #fbbf24;'>
            <span style='font-size: 1.25rem;'>⚡</span>
            <div>
                <div style='font-weight: 600; font-size: 0.92rem;'>No Active Context</div>
                <div style='font-size: 0.82rem; color: #94a3b8;'>Ingest a document or web page above to start conversational querying.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# CHAT LIST & INPUT
# ----------------------------------------------------
chat_container = st.container()

with chat_container:
    # Print clean chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

# Lock prompt if database contains no documents or a query is processing
prompt = st.chat_input("Ask a question...", disabled=is_db_empty or st.session_state.get("processing", False))

if prompt:
    if not api_key:
        st.error("GROQ_API_KEY is not configured.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.current_prompt = prompt
        st.session_state.processing = True
        st.rerun()

# Call LLM with a simple thinking spinner (no emojis or intermediate statuses displayed)
if st.session_state.get("processing", False) and "current_prompt" in st.session_state:
    current_prompt = st.session_state.current_prompt
    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    # Filter out basic greetings, acknowledgments, or politeness turns to bypass retrieval and optimize TPM
                    if is_conversational_query(current_prompt):
                        retrieved = []
                    else:
                        retrieved = search_chunks(
                            st.session_state.collection_name, 
                            current_prompt, 
                            top_k=3, # optimized top_k from 4 to 3 to conserve token limit quota
                            use_hybrid=use_hybrid, 
                            use_reranker=use_reranker
                        )
                    
                    import inspect
                    sig = inspect.signature(generate_answer)
                    if "chat_history" in sig.parameters:
                        response_stream = generate_answer(
                            query=current_prompt,
                            context_chunks=retrieved,
                            api_key=api_key,
                            chat_history=st.session_state.messages[:-1],
                            model=model_choice,
                            temperature=temperature
                        )
                    else:
                        response_stream = generate_answer(
                            query=current_prompt,
                            context_chunks=retrieved,
                            api_key=api_key,
                            model=model_choice,
                            temperature=temperature
                        )
                    
                    placeholder = st.empty()
                    full_response = ""
                    for chunk in response_stream:
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    err = f"Error occurred: {str(e)}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})
                finally:
                    st.session_state.processing = False
                    if "current_prompt" in st.session_state:
                        del st.session_state.current_prompt
                    st.rerun()