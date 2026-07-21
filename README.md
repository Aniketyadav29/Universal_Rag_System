# 🧠 Universal RAG System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://universalragsystemgit-ani.streamlit.app/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://universalragsystemgit-ani.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Groq API](https://img.shields.io/badge/LLM-Groq-F34B21?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-7A00FF?style=for-the-badge)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

An end-to-end, production-grade **Retrieval-Augmented Generation (RAG) System** built with Python, Streamlit, ChromaDB, and Groq. Upload multi-format documents (PDF, DOCX, TXT, CSV, XLSX) or scrape web links to query your knowledge base in real-time with sub-second LLM responses.

👉 **[Experience the Live Web Application](https://universalragsystemgit-ani.streamlit.app/)**

---

## ✨ Key Features

- **🌐 Multi-Source Ingestion**:
  - Upload documents in **PDF, DOCX, TXT, CSV, Excel (XLSX)** formats.
  - Scrape & parse live **Web pages / URLs** on-the-fly.
- **🧩 Parent-Child Chunking**:
  - Implements hierarchical chunking to retain wide context (Parent chunks) while maintaining precise retrieval vectors (Child chunks).
- **🔍 Hybrid Search Engine**:
  - **Dense Vector Search**: Powered by `sentence-transformers/all-MiniLM-L6-v2` embeddings.
  - **Sparse Lexical Search**: Powered by `BM25Okapi` (`rank_bm25`).
  - **Cross-Encoder Re-ranking**: Re-ranks search candidates for maximum relevance.
- **⚡ Sub-Second LLM Generation**:
  - Powered by **Groq LPU Acceleration** for ultra-fast response times.
- **🎨 Modern ChatGPT-Inspired UI**:
  - Styled with custom CSS, dark-mode sleek design, clean tab navigation, and responsive mobile layouts.

---

## 🛠️ Tech Stack

- **Frontend / Framework**: [Streamlit](https://streamlit.io/)
- **LLM Provider**: [Groq API](https://groq.com/) (Llama-3 / Mixtral models)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Embeddings & Re-ranking**: `sentence-transformers`, `torch`
- **Text Processing**: `PyMuPDF`, `python-docx`, `beautifulsoup4`, `pandas`, `openpyxl`, `langchain-text-splitters`
- **Keyword Search**: `rank_bm25`

---

## 📐 Architecture Overview

```
[ Documents / URLs ]
        │
        ▼
[ Document Parser & Extractor ] (PDF, DOCX, TXT, CSV, Web Scraping)
        │
        ▼
[ Parent-Child Chunking ] (Small child chunks for vector indexing, large parent context)
        │
        ├──► [ SentenceTransformer Embeddings ] ──► [ ChromaDB Vector Store ]
        │
        └──► [ BM25 Keyword Indexing ]
                               │
                               ▼
               [ Hybrid Search & Re-Ranker ] (Dense + BM25)
                               │
                               ▼
                   [ Groq LPU LLM Engine ]
                               │
                               ▼
                     [ Streamlit UI Response ]
```

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- Python 3.10+
- A free **Groq API Key** from [console.groq.com](https://console.groq.com)

### 2. Clone Repository
```bash
git clone https://github.com/Aniketyadav29/Universal_Rag_System.git
cd Universal_Rag_System/Universal-Rag-System-main
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Note for Windows users: Install CPU-only PyTorch if you encounter DLL loading issues)*
```bash
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu
```

### 4. Set Environment Variables
Create a `.env` file inside the `Universal-Rag-System-main` folder:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 5. Run the Streamlit App
```bash
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser!

---

## ☁️ Streamlit Community Cloud Deployment

1. Fork or push this repository to your GitHub account.
2. Log in to **[share.streamlit.io](https://share.streamlit.io)**.
3. Click **New App** and select:
   - **Repository**: `Aniketyadav29/Universal_Rag_System`
   - **Branch**: `main`
   - **Main file path**: `Universal-Rag-System-main/app.py`
4. In **Settings ⚙️ ➔ Secrets**, add your key:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
5. Click **Deploy!** 🚀

---

## 📂 Project Structure

```
Universal_Rag_System/
│
├── Universal-Rag-System-main/
│   ├── app.py                 # Streamlit UI & main app entry point
│   ├── requirements.txt       # Python dependencies
│   ├── deployment_guide.md    # Deployment guide for Streamlit Cloud
│   ├── .streamlit/            # Streamlit config (theme & layout settings)
│   └── services/              # Modular backend services
│       ├── document_service.py # Multi-format document parser
│       ├── web_service.py      # Web page scraper & extractor
│       ├── chunk_service.py    # Parent-child chunker
│       ├── embedding_service.py# Embedding generator
│       ├── vector_service.py   # ChromaDB vector collection manager
│       ├── retrieval_service.py# Hybrid search (Dense + BM25 + Re-ranker)
│       └── llm_service.py      # Groq LLM integration
│
├── .gitignore                 # Excludes heavy model weights & secrets
└── README.md                  # Project documentation & live badges
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">Made with ❤️ using Streamlit & Groq</p>
