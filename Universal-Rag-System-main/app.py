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

# Custom 3D Ancient Codex / Oracle Aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800;900&family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

/* 3D Ancient Obsidian & Ember Background */
.stApp {
    background: 
        radial-gradient(circle at 15% 10%, rgba(217, 119, 6, 0.16) 0%, transparent 45%),
        radial-gradient(circle at 85% 85%, rgba(180, 83, 9, 0.14) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(120, 53, 15, 0.09) 0%, transparent 55%),
        #0a0705 !important;
    background-attachment: fixed !important;
    color: #fef3c7 !important;
}

/* 3D Temple Sanctum Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #110c08 0%, #080503 100%) !important;
    border-right: 1px solid rgba(217, 119, 6, 0.25) !important;
    box-shadow: 10px 0 35px rgba(0, 0, 0, 0.85) !important;
}

.sidebar-title {
    font-family: 'Cinzel', serif !important;
    font-size: 1.15rem;
    font-weight: 700;
    color: #fef3c7;
    letter-spacing: 0.1em;
    margin-top: 0.5rem;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(217, 119, 6, 0.25);
    display: flex;
    align-items: center;
    gap: 8px;
    text-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
}

/* 3D Hero Ancient Title & Floating Relic Badge */
.hero-container {
    text-align: center;
    padding: 1.5rem 0 1.2rem 0;
    position: relative;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, rgba(217, 119, 6, 0.22) 0%, rgba(180, 83, 9, 0.15) 100%);
    border: 1px solid rgba(245, 158, 11, 0.45);
    border-top: 1px solid rgba(254, 240, 138, 0.5);
    color: #fde68a;
    font-family: 'Cinzel', serif !important;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    padding: 0.35rem 1rem;
    border-radius: 9999px;
    margin-bottom: 0.9rem;
    box-shadow: 0 4px 18px rgba(217, 119, 6, 0.35), inset 0 1px 0 rgba(254, 240, 138, 0.35);
    text-transform: uppercase;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    background: #fbbf24;
    border-radius: 50%;
    box-shadow: 0 0 12px #fbbf24;
    animation: emberPulse 2s infinite ease-in-out;
}

@keyframes emberPulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.5; }
}

.hero-title {
    font-family: 'Cinzel', serif !important;
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 15%, #fde68a 50%, #d97706 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
    filter: drop-shadow(0 4px 18px rgba(217, 119, 6, 0.45));
    text-transform: uppercase;
}

.hero-subtitle {
    font-size: 1.02rem;
    color: #d4af37;
    font-weight: 400;
    max-width: 620px;
    margin: 0 auto 1.8rem auto;
    line-height: 1.5;
    opacity: 0.9;
}

/* 3D Inscribed Stone Slab Status Box */
.status-box {
    background: linear-gradient(135deg, rgba(28, 20, 14, 0.85) 0%, rgba(15, 11, 7, 0.95) 100%) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(217, 119, 6, 0.35) !important;
    border-top: 1px solid rgba(254, 240, 138, 0.35) !important;
    border-radius: 14px !important;
    padding: 1rem 1.4rem !important;
    color: #fef3c7 !important;
    margin: 1.2rem 0 !important;
    box-shadow: 
        0 14px 35px -5px rgba(0, 0, 0, 0.85), 
        0 0 25px -4px rgba(217, 119, 6, 0.25), 
        inset 0 1px 0 rgba(254, 240, 138, 0.15) !important;
    transform: translateY(0);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.status-box:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 18px 40px -5px rgba(0, 0, 0, 0.95), 
        0 0 35px -2px rgba(245, 158, 11, 0.4), 
        inset 0 1px 0 rgba(254, 240, 138, 0.3) !important;
}

/* 3D Forged Bronze Tactile Buttons */
.stButton>button {
    background: linear-gradient(135deg, #d97706 0%, #b45309 50%, #92400e 100%) !important;
    color: #fffbeb !important;
    border: 1px solid rgba(254, 240, 138, 0.3) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.55) !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.25rem !important;
    font-weight: 700 !important;
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    box-shadow: 
        0 4px 0 #451a03, 
        0 8px 24px rgba(217, 119, 6, 0.45), 
        inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
    transform: translateY(0) !important;
    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    box-shadow: 
        0 6px 0 #451a03, 
        0 14px 28px rgba(245, 158, 11, 0.6), 
        inset 0 1px 0 rgba(255, 255, 255, 0.55) !important;
    transform: translateY(-2px) !important;
}

.stButton>button:active {
    box-shadow: 
        0 1px 0 #451a03, 
        0 4px 10px rgba(180, 83, 9, 0.35), 
        inset 0 1px 2px rgba(0, 0, 0, 0.4) !important;
    transform: translateY(3px) !important;
}

/* 3D Ancient Glass Expander */
[data-testid="stExpander"] {
    background: linear-gradient(135deg, rgba(28, 21, 14, 0.65) 0%, rgba(14, 10, 7, 0.85) 100%) !important;
    border: 1px solid rgba(217, 119, 6, 0.25) !important;
    border-top: 1px solid rgba(254, 240, 138, 0.25) !important;
    border-radius: 14px !important;
    box-shadow: 
        0 10px 30px -5px rgba(0, 0, 0, 0.75), 
        inset 0 1px 0 rgba(254, 240, 138, 0.1) !important;
    backdrop-filter: blur(14px) !important;
    overflow: hidden !important;
    transition: all 0.25s ease !important;
}

[data-testid="stExpander"]:hover {
    border-color: rgba(245, 158, 11, 0.5) !important;
    box-shadow: 
        0 14px 35px -5px rgba(0, 0, 0, 0.85), 
        0 0 25px rgba(217, 119, 6, 0.25) !important;
}

/* 3D Segmented Inscribed Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(16, 12, 8, 0.8) !important;
    border-radius: 11px !important;
    padding: 5px !important;
    border: 1px solid rgba(217, 119, 6, 0.25) !important;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5) !important;
    gap: 6px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #d4af37 !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.55rem 1.1rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #b45309 0%, #d97706 100%) !important;
    color: #fffbeb !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(217, 119, 6, 0.5), inset 0 1px 0 rgba(254, 240, 138, 0.4) !important;
}

/* 3D Ancient Scroll Uploader */
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, rgba(35, 25, 16, 0.3) 0%, rgba(18, 12, 8, 0.55) 100%) !important;
    border: 2px dashed rgba(217, 119, 6, 0.45) !important;
    border-radius: 12px !important;
    padding: 1.6rem !important;
    transition: all 0.25s ease !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: #fbbf24 !important;
    background: linear-gradient(135deg, rgba(55, 35, 20, 0.4) 0%, rgba(20, 14, 9, 0.7) 100%) !important;
    box-shadow: 0 0 28px rgba(217, 119, 6, 0.3) !important;
}

/* 3D Ancient Codex Messages */
[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, rgba(28, 20, 14, 0.8) 0%, rgba(15, 11, 7, 0.92) 100%) !important;
    border: 1px solid rgba(217, 119, 6, 0.22) !important;
    border-top: 1px solid rgba(254, 240, 138, 0.22) !important;
    border-left: 3px solid #d97706 !important;
    border-radius: 14px !important;
    padding: 1.15rem 1.4rem !important;
    margin-bottom: 1.1rem !important;
    box-shadow: 
        0 12px 28px -5px rgba(0, 0, 0, 0.7), 
        inset 0 1px 0 rgba(254, 240, 138, 0.1) !important;
    backdrop-filter: blur(14px) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatMessage"]:hover {
    transform: translateY(-1px);
    box-shadow: 
        0 16px 34px -5px rgba(0, 0, 0, 0.85), 
        0 0 20px rgba(217, 119, 6, 0.25) !important;
}

/* 3D Obsidian Inscription Input Dock */
[data-testid="stChatInput"] {
    background: transparent !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    background: linear-gradient(135deg, rgba(24, 18, 12, 0.95) 0%, rgba(13, 9, 6, 0.98) 100%) !important;
    border: 1px solid rgba(217, 119, 6, 0.4) !important;
    border-top: 1px solid rgba(254, 240, 138, 0.3) !important;
    border-radius: 14px !important;
    box-shadow: 
        0 12px 35px -5px rgba(0, 0, 0, 0.85), 
        0 0 25px rgba(217, 119, 6, 0.2), 
        inset 0 2px 4px rgba(0, 0, 0, 0.6) !important;
    color: #fef3c7 !important;
    font-size: 0.96rem !important;
    transition: all 0.25s ease !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #f59e0b !important;
    box-shadow: 
        0 16px 40px -5px rgba(0, 0, 0, 0.95), 
        0 0 35px rgba(245, 158, 11, 0.5), 
        inset 0 1px 2px rgba(0, 0, 0, 0.3) !important;
}

/* 3D Selectbox & Sliders in Sidebar */
[data-baseweb="select"] > div {
    background: rgba(24, 18, 12, 0.85) !important;
    border: 1px solid rgba(217, 119, 6, 0.35) !important;
    border-top: 1px solid rgba(254, 240, 138, 0.2) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
}

/* Custom 3D Antique Gold Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0a0705;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #d97706 0%, #78350f 100%);
    border-radius: 9999px;
    border: 1px solid rgba(254, 240, 138, 0.25);
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #f59e0b 0%, #92400e 100%);
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
    st.markdown("<div class='sidebar-title'><span style='color: #f59e0b;'>⚜️</span> ORACLE SANCTUM</div>", unsafe_allow_html=True)
    
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

# 3D Hero Title & Ancient Relic Badge
st.markdown("""
<div class='hero-container'>
    <div class='hero-badge'><span class='pulse-dot'></span> ⚜️ ANCIENT CODEX • GROQ ORACLE ENGINE ⚜️</div>
    <div class='hero-title'>ARCHIVAL ORACLE</div>
    <div class='hero-subtitle'>Consult the ancient scrolls, sacred codices, and modern texts through 3D vector alchemy.</div>
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

# Active status indicator (3D Ancient Inscribed HUD)
if db_stats['chunks'] > 0:
    source_type = "Sacred Scroll" if st.session_state.indexed_source == "Document" else "Oracle Web"
    if st.session_state.indexed_source == "None":
        source_type = "Preserved Relic"
        st.session_state.source_name = "Inscribed Codex Vectors"
        st.session_state.chunk_count = db_stats['chunks']
        
    st.markdown(f"""
    <div class='status-box'>
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>
            <div>
                <span style='color: #f59e0b; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em; font-family: "Cinzel", serif;'>📜 Active Inscribed Codex</span>
                <div style='font-size: 1.05rem; font-weight: 600; color: #fef3c7; margin-top: 2px;'>{st.session_state.source_name} <span style='font-size: 0.8rem; color: #d97706; font-weight: 400;'>({source_type})</span></div>
            </div>
            <div style='background: rgba(217, 119, 6, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 8px; padding: 0.35rem 0.85rem; text-align: center; box-shadow: inset 0 1px 0 rgba(254, 240, 138, 0.2);'>
                <span style='font-size: 0.68rem; color: #fde68a; display: block; font-weight: 700; font-family: "Cinzel", serif; letter-spacing: 0.08em;'>SEALS INSCRIBED</span>
                <span style='font-size: 1.2rem; font-weight: 800; color: #fbbf24; font-family: "Cinzel", serif;'>{st.session_state.chunk_count}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class='status-box' style='border-color: rgba(217, 119, 6, 0.35); background: linear-gradient(135deg, rgba(28, 20, 14, 0.85) 0%, rgba(14, 10, 7, 0.95) 100%);'>
        <div style='display: flex; align-items: center; gap: 12px; color: #fbbf24;'>
            <span style='font-size: 1.4rem;'>🏺</span>
            <div>
                <div style='font-weight: 700; font-size: 0.95rem; font-family: "Cinzel", serif; letter-spacing: 0.05em;'>The Archive is Quiet</div>
                <div style='font-size: 0.82rem; color: #d4af37; opacity: 0.85;'>Inscribe a manuscript or sacred web scroll above to awaken the Oracle.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# CHAT LIST & INPUT
# ----------------------------------------------------
chat_container = st.container()

with chat_container:
    # Print clean chat history with Ancient Scribe & Oracle avatars
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🪶" if msg["role"] == "user" else "🏛️"):
            st.markdown(msg["content"])

# Lock prompt if database contains no documents or a query is processing
prompt = st.chat_input("Inquire of the ancient codex...", disabled=is_db_empty or st.session_state.get("processing", False))

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
        with st.chat_message("assistant", avatar="🏛️"):
            with st.spinner("Consulting the sacred archives..."):
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