# 🧠 Universal RAG System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://universalragsystemgit-ani.streamlit.app/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://universalragsystemgit-ani.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Groq API](https://img.shields.io/badge/LLM-Groq%20LPU-F34B21?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-7A00FF?style=for-the-badge)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

An end-to-end, enterprise-grade **Retrieval-Augmented Generation (RAG) System** built with Python, Streamlit, ChromaDB, and Groq LPU acceleration. Upload multi-format documents (`PDF`, `DOCX`, `TXT`, `CSV`, `XLSX`, `JSON`) or scrape live website links to query your custom knowledge base in real-time with sub-second LLM streaming responses.

👉 **[Experience the Live Web Application](https://universalragsystemgit-ani.streamlit.app/)** | 📘 **[Read the User Manual](../USER_MANUAL.md)**

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack & Technologies](#️-tech-stack--technologies)
- [📐 System Architecture](#-system-architecture)
- [📂 Project Structure](#-project-structure)
- [⚙️ Modular Backend Services](#️-modular-backend-services)
- [🚀 Quick Start (Local Setup)](#-quick-start-local-setup)
- [☁️ Streamlit Community Cloud Deployment](#️-streamlit-community-cloud-deployment)
- [🎛️ Control Panel & Tuning Parameters](#️-control-panel--tuning-parameters)
- [🔍 Hybrid Search & Parent-Child Chunking Deep Dive](#-hybrid-search--parent-child-chunking-deep-dive)
- [❓ Frequently Asked Questions & Troubleshooting](#-frequently-asked-questions--troubleshooting)
- [📜 License & Acknowledgments](#-license--acknowledgments)

---

## ✨ Key Features

- **🌐 Multi-Source Ingestion Engine**:
  - **Document Processing**: Parses `PDF`, `DOCX`, `TXT`, `CSV`, `XLSX`/`XLS`, and `JSON` files.
  - **Structured Tabular Data Parsing**: Converts CSV & Excel spreadsheets into structured row-by-row key-value formats to prevent context dilution.
  - **Live Web Scraping**: Extracts readable body text from website URLs using `BeautifulSoup4`, automatically filtering out script tags, styles, footers, and navigation bars.
- **🧩 Parent-Child Chunking Architecture**:
  - Uses `RecursiveCharacterTextSplitter` to generate compact **Child Chunks (400 chars)** for vector indexing and high-precision similarity matching.
  - Links each child chunk to a broader **Parent Block (3,000 chars)** provided as rich context to the LLM during generation, eliminating context truncation errors.
- **🔍 Advanced Hybrid Search & Re-ranking**:
  - **Dense Vector Search**: Powered by `sentence-transformers/all-MiniLM-L6-v2` embeddings stored in ChromaDB.
  - **Sparse Lexical Keyword Search**: Powered by `BM25Okapi` (`rank_bm25`) for exact token/acronym matching.
  - **Reciprocal Rank Fusion (RRF)**: Merges dense and lexical search candidates into a unified relevance ordering.
  - **Cross-Encoder Re-ranking**: Optional second-stage re-ranking using `ms-marco-MiniLM-L-6-v2` for maximum precision.
- **⚡ Sub-Second LLM Streaming Generation**:
  - Leverages **Groq LPU Engine** for ultra-fast response streaming.
  - Supports multiple model backends: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, and `gemma2-9b-it`.
  - Automatic exponential backoff and retry mechanism for API rate limits (`429`).
- **💬 Conversational Query Filter**:
  - Smart detection of greetings, acknowledgments, and politeness turns (`"hi"`, `"hello"`, `"thank you"`) to bypass vector retrieval, conserving API token budgets and speeding up responses.
- **🎨 Sleek ChatGPT-Inspired UI**:
  - Customized Streamlit interface featuring `Outfit` Google Typography, dark slate palette, responsive mobile layout, real-time stage progress trackers, and clean source citation rendering.
- **🔒 Session Isolation & Automatic Lifecycle Cleanup**:
  - Unique UUID per browser session creating isolated ChromaDB collections.
  - Automatic TTL background cleaner that purges stale vector collections older than 2 hours.

---

## 🛠️ Tech Stack & Technologies

| Layer | Technology / Library | Purpose |
|---|---|---|
| **Frontend UI** | [Streamlit](https://streamlit.io/) | Web interface, custom CSS theme, sidebar controls, streaming chat |
| **LLM Acceleration** | [Groq API](https://groq.com/) | Ultra-fast inference with Llama 3.3, Llama 3.1, Mixtral |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) | Local persistent vector collection management |
| **Embeddings Model** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dimensional dense semantic text embeddings |
| **Cross-Encoder Re-ranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Deep contextual query-chunk score re-ranking |
| **Lexical Search** | `rank_bm25` | Sparse keyword matching (BM25Okapi) |
| **Text Chunking** | `langchain-text-splitters` | Parent-child hierarchical text splitting |
| **PDF Extraction** | `PyMuPDF` (`fitz`) | High-speed PDF text parsing with timeout protection |
| **Document Processing** | `python-docx`, `pandas`, `openpyxl` | DOCX document and CSV/Excel spreadsheet extraction |
| **Web Scraping** | `requests`, `beautifulsoup4` | Web page fetching and DOM noise cleanup |
| **Environment Management** | `python-dotenv` | Secure API key configuration |

---

## 📐 System Architecture

```
                               ┌─────────────────────────────────────────┐
                               │  User Input (File Upload or Web URL)    │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │       Document & Web Extractor          │
                               │  (PDF, DOCX, TXT, CSV, Excel, Web URL) │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │      Parent-Child Text Chunker          │
                               │  (Parent: 3000 chars | Child: 400 chars)│
                               └──────────┬───────────────────┬──────────┘
                                          │                   │
                                          ▼                   ▼
                     ┌──────────────────────────────┐       ┌──────────────────────────────┐
                     │   SentenceTransformers       │       │       BM25Okapi Index        │
                     │   (all-MiniLM-L6-v2)         │       │   (Sparse Keyword Index)     │
                     └────────────┬─────────────────┘       └──────────────┬───────────────┘
                                  │                                        │
                                  ▼                                        ▼
                     ┌──────────────────────────────┐       ┌──────────────────────────────┐
                     │     ChromaDB Vector Store    │       │     Lexical Keyword Search   │
                     └────────────┬─────────────────┘       └──────────────┬───────────────┘
                                  │                                        │
                                  └─────────────────┬──────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │   Hybrid Search & Reciprocal Rank       │
                               │               Fusion (RRF)              │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼ (Optional)
                               ┌─────────────────────────────────────────┐
                               │     Cross-Encoder Re-Ranking Stage      │
                               │     (ms-marco-MiniLM-L-6-v2)           │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │         Groq LPU Inference Engine       │
                               │    (Strict Grounded Context Prompt)     │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │   Streamlit Real-Time Output Stream     │
                               └─────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Universal_Rag_System/
│
├── .gitignore                      # Git exclusion list (vector DBs, weights, .env)
├── README.md                       # Main repository documentation
├── USER_MANUAL.md                  # Comprehensive end-user operational manual
│
└── Universal-Rag-System-main/
    ├── app.py                      # Main Streamlit web app entry point & UI
    ├── requirements.txt            # Python dependencies
    ├── deployment_guide.md         # Step-by-step Streamlit Cloud deployment guide
    ├── Overview.txt                # High-level architecture summary
    ├── .env                        # Local environment secrets (GROQ_API_KEY)
    ├── .streamlit/
    │   └── config.toml             # Streamlit server config (file upload limit: 200MB)
    │
    ├── services/                   # Modular backend service components
    │   ├── document_service.py     # Master document routing & parsing dispatcher
    │   ├── pdf_service.py          # PyMuPDF fast text extraction with timeout checks
    │   ├── web_service.py          # Web scraper & HTML cleaner using BeautifulSoup4
    │   ├── chunk_service.py        # Parent-child chunk generation logic
    │   ├── embedding_service.py    # SentenceTransformer embedding generator
    │   ├── vector_service.py       # ChromaDB collection & session manager
    │   ├── retrieval_service.py    # Hybrid search (Vector + BM25 + RRF + Re-ranker)
    │   └── llm_service.py          # Groq API streaming integration & conversational filter
    │
    ├── local_model/                # Pre-downloaded embedding model weights
    └── local_reranker/             # Pre-downloaded cross-encoder re-ranker weights
```

---

## ⚙️ Modular Backend Services

The backend is built around a decoupled service architecture located in `services/`:

1. **`document_service.py`**:
   - Inspects file extension (`.pdf`, `.txt`, `.md`, `.json`, `.docx`, `.csv`, `.xlsx`, `.xls`).
   - Parses tabular files into explicit `Row X: Column: Value` records so spreadsheet rows remain structured.
2. **`pdf_service.py`**:
   - Uses PyMuPDF (`fitz`) to extract page-level text.
   - Enforces configurable timeout limits (`timeout_seconds`) to prevent server freezing on corrupted PDFs.
3. **`web_service.py`**:
   - Fetches web content via `requests` with standard User-Agent headers.
   - Parses HTML with `BeautifulSoup4`, stripping `<script>`, `<style>`, `<nav>`, and `<footer>` elements.
4. **`chunk_service.py`**:
   - Implements parent-child chunking.
   - Short pages are assigned directly as parent blocks; long pages are chunked into 3,000-character parent blocks, each subdivided into 400-character child vectors.
5. **`embedding_service.py`**:
   - Loads `all-MiniLM-L6-v2` locally or from HuggingFace.
   - Automatically selects `cuda` if GPU is available, or CPU fallback. Batch processes embeddings (batch size 32) with progress callbacks.
6. **`vector_service.py`**:
   - Manages ChromaDB collections stored at `./chroma_db`.
   - Generates session-based isolated collection keys (`rag_<timestamp>_<session_id>`).
   - Runs `cleanup_expired_collections` to delete session stores older than 2 hours.
7. **`retrieval_service.py`**:
   - Executes dense vector search on ChromaDB collections.
   - Builds in-memory `BM25Okapi` index over ingested text chunks.
   - Blends vector and lexical scores via Reciprocal Rank Fusion (RRF score: `1.0 / (60 + rank)`).
   - Resolves child matches back to full parent context blocks (`parent_text`) and deduplicates results.
   - Optionally applies Cross-Encoder re-ranking (`ms-marco-MiniLM-L-6-v2`).
8. **`llm_service.py`**:
   - Filters simple greetings/politeness queries via `is_conversational_query`.
   - Constructs strict system prompts instructing the model to rely *only* on provided context chunks.
   - Streams responses chunk-by-chunk from Groq's OpenAI-compatible completions endpoint with exponential backoff on HTTP 429 rate limits.

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- **Python 3.10 or higher** installed.
- A free **Groq API Key** from [console.groq.com](https://console.groq.com).

### 2. Clone the Repository
```bash
git clone https://github.com/Aniketyadav29/Universal_Rag_System.git
cd Universal_Rag_System/Universal-Rag-System-main
```

### 3. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note for Windows Users**: If you encounter PyTorch DLL loading issues on Windows, install the CPU-only version of PyTorch:
> ```bash
> pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu
> ```

### 5. Configure Environment Variables
Create a `.env` file in the `Universal-Rag-System-main` directory:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 6. Run the Application
```bash
python -m streamlit run app.py
```
Open your web browser and navigate to **`http://localhost:8501`**.

---

## ☁️ Streamlit Community Cloud Deployment

To host this application for free on Streamlit Community Cloud:

1. Push or fork this repository to your GitHub account.
2. Log in to [share.streamlit.io](https://share.streamlit.io).
3. Click **New App** and configure:
   - **Repository**: `Aniketyadav29/Universal_Rag_System`
   - **Branch**: `main`
   - **Main file path**: `Universal-Rag-System-main/app.py`
4. Go to **Advanced Settings ⚙️ ➔ Secrets** and paste your API key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
   ```
5. Click **Deploy!** 🚀

---

## 🎛️ Control Panel & Tuning Parameters

The sidebar **Control Panel** allows runtime adjustments:

| Parameter | Default Value | Description |
|---|---|---|
| **Model Selection** | `llama-3.3-70b-versatile` | Choose between speed (`8b-instant`) or deep reasoning (`70b-versatile`, `mixtral-8x7b`). |
| **Temperature** | `0.2` | Controls randomness. Low value (0.0 - 0.2) is recommended for strict factual Q&A. |
| **Max Processing Timeout** | `120s` | Maximum time allowed for parsing complex PDF documents before throwing a timeout warning. |
| **Max Chunk Limit** | `3,000` | Safety threshold for total text chunks per document. If exceeded, the app alerts you to raise the limit. |
| **Use Hybrid Search** | `Enabled` (Checked) | Combines dense vector similarity with sparse BM25 keyword matching via RRF. |
| **Use Cross-Encoder Re-ranking**| `Disabled` (Unchecked)| Re-scores candidate passages using a Cross-Encoder model for enhanced top-k precision. |
| **Reset Session Context** | Button | Purges current session ChromaDB vectors, clears memory, and resets session state. |

---

## 🔍 Hybrid Search & Parent-Child Chunking Deep Dive

### Parent-Child Chunking Strategy
Standard chunking often faces a dilemma:
- **Small chunks** yield precise vector search matches but lack sufficient context for the LLM.
- **Large chunks** provide comprehensive context but dilute vector embedding precision.

**Universal RAG System solves this with Parent-Child Chunking**:
1. Documents are parsed into **Parent Blocks** (~3,000 characters).
2. Each parent block is subdivided into **Child Chunks** (~400 characters).
3. **Child chunks are indexed** in ChromaDB for high-precision similarity retrieval.
4. When a child chunk matches a user query, the system **retrieves its full Parent Block** and passes that rich context to Groq LLM.

### Reciprocal Rank Fusion (RRF) Formula
When Hybrid Search is enabled, the system computes RRF scores across vector and keyword ranks:

$$RRF(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where $k = 60$, and $r_m(d)$ is the rank of document $d$ in retrieval method $m$ (Vector Search or BM25 Search).

---

## ❓ Frequently Asked Questions & Troubleshooting

<details>
<summary><b>1. "GROQ_API_KEY is missing from environment" error</b></summary>
Ensure you have created a <code>.env</code> file inside <code>Universal-Rag-System-main/</code> containing <code>GROQ_API_KEY=gsk_...</code> or entered the key in Streamlit Secrets.
</details>

<details>
<summary><b>2. Uploaded PDF shows "0 chunks generated" or scanned image warning</b></summary>
The system extracts native digital text. If your PDF consists purely of scanned images without an OCR text layer, PyMuPDF cannot extract text. Convert or OCR the PDF before uploading.
</details>

<details>
<summary><b>3. Groq API Rate Limit reached (Status 429)</b></summary>
The system includes built-in exponential backoff retries. If your query hits Groq's Tokens Per Minute (TPM) limit, wait a few seconds and submit again, or switch to <code>llama-3.1-8b-instant</code> in the sidebar.
</details>

<details>
<summary><b>4. Maximum Chunk Limit Warning triggered</b></summary>
If your document generates more than 3,000 chunks, the sidebar <b>Advanced Settings</b> expander will open automatically. Increase the <b>Max Chunk Limit</b> slider to accommodate your document size and click <b>Index Document</b> again.
</details>

---

## 📜 License & Acknowledgments

Distributed under the **MIT License**. See `LICENSE` for details.

- **Built with**: [Streamlit](https://streamlit.io/) | [Groq](https://groq.com/) | [ChromaDB](https://www.trychroma.com/) | [SentenceTransformers](https://www.sbert.net/)
- **Author**: [Aniketyadav29](https://github.com/Aniketyadav29)
