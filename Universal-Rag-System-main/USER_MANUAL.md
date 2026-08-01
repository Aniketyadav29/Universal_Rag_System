# 📖 Universal RAG System - User Manual & Operating Guide

Welcome to the **Universal RAG System** user manual! This document provides step-by-step instructions on how to use the web application to ingest your documents or website links, configure the search engine, ask questions, and get instant, accurate, fact-grounded AI responses.

---

## 📌 Table of Contents
1. [🚀 Quick Start (3-Minute Guide)](#-quick-start-3-minute-guide)
2. [📂 Ingesting Your Knowledge Base](#-ingesting-your-knowledge-base)
   - [Option A: Uploading Document Files](#option-a-uploading-document-files)
   - [Option B: Indexing Live Website URLs](#option-b-indexing-live-website-urls)
   - [Understanding the Ingestion Progress Bar](#understanding-the-ingestion-progress-bar)
3. [🎛️ Using the Control Panel (Sidebar Settings)](#️-using-the-control-panel-sidebar-settings)
   - [Selecting the AI Model](#selecting-the-ai-model)
   - [Adjusting Temperature](#adjusting-temperature)
   - [Advanced Settings & Limits](#advanced-settings--limits)
   - [Toggling Hybrid Search & Re-ranking](#toggling-hybrid-search--re-ranking)
   - [Resetting Session Context](#resetting-session-context)
4. [💬 Asking Questions & Chatting with your Documents](#-asking-questions--chatting-with-your-documents)
   - [General & Analytical Queries](#general--analytical-queries)
   - [Spreadsheet & Tabular Row Queries](#spreadsheet--tabular-row-queries)
   - [Conversational Chit-Chat & Greetings](#conversational-chit-chat--greetings)
   - [Reading Source Citations](#reading-source-citations)
5. [🔒 Data Privacy & Session Isolation](#-data-privacy--session-isolation)
6. [💡 Tips for Best Results](#-tips-for-best-results)
7. [❓ Troubleshooting Guide](#-troubleshooting-guide)

---

## 🚀 Quick Start (3-Minute Guide)

If you are using the app for the first time, follow these 3 simple steps:

1. **Open the Application**: Go to the live app at [https://universalragsystemgit-ani.streamlit.app/](https://universalragsystemgit-ani.streamlit.app/) (or `http://localhost:8501` if running locally).
2. **Ingest a Document or URL**:
   - In the **Ingest Document or Web Page** box, upload a PDF/DOCX/TXT/CSV file OR click **Website URL** tab and paste a website link.
   - Click **Index Document** (or **Index Web Page**). Wait a few seconds for the green success message `✓ Ready for questions`.
3. **Ask Any Question**: Type your prompt into the bottom chat box (`Ask a question...`) and hit **Enter**.

---

## 📂 Ingesting Your Knowledge Base

Before the system can answer questions, you must provide source material. You can ingest either a **Document File** or a **Website URL**.

### Option A: Uploading Document Files

1. Ensure the **Document File** tab is selected.
2. Click **Browse files** or drag-and-drop your file into the box.
3. **Supported Formats**:
   - 📄 **PDF (`.pdf`)**: Native digital PDFs containing readable text.
   - 📝 **Word Documents (`.docx`)**: Microsoft Word files.
   - 📄 **Text & Markdown (`.txt`, `.md`)**: Plain text notes or markdown files.
   - 📊 **Spreadsheets (`.csv`, `.xlsx`, `.xls`)**: Tabular data files.
   - 💻 **JSON (`.json`)**: Structured data files.
4. **File Size Limit**: Maximum **30 MB** per file.
5. Click **Index Document**.

> ⚠️ **Important Note on PDFs**: The application parses *digital* text layers. If your PDF is a scanned image of paper without OCR text, PyMuPDF cannot read the text. Ensure your PDF text is selectable with your mouse.

---

### Option B: Indexing Live Website URLs

1. Click on the **Website URL** tab.
2. Type or paste a valid web address starting with `http://` or `https://` (e.g., `https://en.wikipedia.org/wiki/Artificial_intelligence`).
3. Click **Index Web Page**.
4. The system will automatically fetch the web page, remove navigation menus, footers, and advertisement scripts, and index the main body content.

---

### Understanding the Ingestion Progress Bar

When indexing starts, a real-time progress tracker displays:

```
✓ File uploaded
🔄 Extracting text... [██████████ 100%]
🔄 Chunking... (24 chunks)
🔄 Generating embeddings... (24/24 generated)
🔄 Indexing vectors...
```

Once completed, you will see a green summary card:
- **Pages**: Total pages parsed.
- **Chunks**: Total text segments indexed.
- **Processing Time**: Exact seconds taken.

The **Active Context** status bar below will update to show your active filename and chunk count.

---

## 🎛️ Using the Control Panel (Sidebar Settings)

The left sidebar gives you full control over how queries are answered:

### Selecting the AI Model

Choose the LLM backend from the **Model Selection** dropdown:

- 🚀 **`llama-3.1-8b-instant`**: Best for ultra-fast, sub-second responses and simple factual lookups.
- 🧠 **`llama-3.3-70b-versatile`** *(Default / Recommended)*: Ideal for complex questions, deep reasoning, logic, and comprehensive summaries.
- ⚡ **`mixtral-8x7b-32768`**: Excellent for large context comprehension and technical documentation.
- 💎 **`gemma2-9b-it`**: Google's open weights model for balanced performance.

---

### Adjusting Temperature

- Range: `0.0` to `1.0` (Default: `0.2`).
- **Low (0.0 - 0.2)**: Highly strict, precise, factual responses. Ideal for legal, medical, or tabular data.
- **High (0.5 - 0.8)**: More creative, expressive phrasing.

---

### Advanced Settings & Limits

Click **Advanced Settings** to open fine-tuning sliders:

- **Max Processing Timeout (s)** (Default: `120s`): Controls maximum seconds allowed for text extraction before timing out on huge PDFs.
- **Max Chunk Limit** (Default: `3,000`): Maximum allowed text chunks per document. If a massive document exceeds 3,000 chunks, the system automatically opens this panel and guides you to increase this slider.

---

### Toggling Hybrid Search & Re-ranking

- **Use Hybrid Search** *(Checked by Default)*:
  - Combines **Dense Vector Search** (semantic similarity) + **BM25 Lexical Search** (exact keyword matching).
  - Strongly recommended to keep enabled so specific names, IDs, dates, and technical acronyms are never missed.
- **Use Cross-Encoder Re-ranking** *(Unchecked by Default)*:
  - Re-evaluates top search results using a deep Cross-Encoder neural model (`ms-marco-MiniLM-L-6-v2`) for ultra-high precision scoring.

---

### Resetting Session Context

If you want to clear your current document index and chat history to start fresh:
1. Click the red **Reset Session Context** button in the sidebar.
2. The active collection will be purged from the database, memory will be freed, and you can upload a new file.

---

## 💬 Asking Questions & Chatting with your Documents

Once your document is indexed, type your prompt into the bottom chat box.

### General & Analytical Queries
- *"Summarize the key points of this document in bullet points."*
- *"What are the main risks discussed in section 3?"*
- *"Compare the findings in quarterly report A versus report B."*

---

### Spreadsheet & Tabular Row Queries
When you upload CSV or Excel files, the system parses data into explicit row numbers. You can ask row-specific questions:
- *"What is the salary of John Doe in Row 15?"*
- *"List all entries where Status is Pending."*

---

### Conversational Chit-Chat & Greetings
If you type general polite messages like `"hi"`, `"hello"`, or `"thank you"`, the system automatically detects this and responds politely **without wasting API tokens** on document retrieval.

---

### Reading Source Citations

At the end of every answer, the system automatically attaches a clean **Sources** section showing exactly where the answer was retrieved from:

```markdown
Here is the summary of the project guidelines...

Sources:
- PDF: project_report.pdf (Page 4)
- PDF: project_report.pdf (Page 12)
```

If the information is not contained in your uploaded document, the system strictly responds:
> *"I cannot find the answer in the provided documents."*

This prevents hallucinated or false information.

---

## 🔒 Data Privacy & Session Isolation

- **Isolated Sessions**: Every time you open the app, a unique UUID (`rag_<timestamp>_<uuid>`) is generated. Your uploaded vectors are stored in a dedicated session workspace.
- **Automatic Lifecycle Purging**: Inactive vector stores older than 2 hours are automatically cleaned up in the background.
- **Data Security**: Your files are processed locally in your session and are not shared with other users.

---

## 💡 Tips for Best Results

1. **Use Searchable Digital Files**: Avoid blurry scanned image PDFs.
2. **Keep Hybrid Search Enabled**: Hybrid search delivers the highest accuracy for both semantic context and exact keywords.
3. **Be Specific in Queries**: Instead of asking *"Tell me about the file"*, ask *"What is the primary conclusion regarding revenue growth?"*.
4. **Use Llama-3.3 70B for Deep Analysis**: For long complex documents requiring multi-step reasoning, choose `llama-3.3-70b-versatile` in the sidebar.

---

## ❓ Troubleshooting Guide

| Problem | Cause | Solution |
|---|---|---|
| **`GROQ_API_KEY is missing`** | No API key found in `.env` file | Add `GROQ_API_KEY=gsk_...` to your `.env` file or Streamlit Secrets. |
| **PDF upload shows 0 chunks** | Scanned PDF without text layer | Perform OCR on your PDF or upload a text-native PDF. |
| **`Max Chunk Limit Exceeded`** | File generated more than 3,000 chunks | Go to **Sidebar ➔ Advanced Settings**, increase **Max Chunk Limit** slider, and re-index. |
| **`Status 429: Rate limit reached`** | Groq API hourly token limit reached | Wait 10-15 seconds and resubmit, or switch to `llama-3.1-8b-instant`. |
| **Website extraction fails** | Site requires login or blocks scrapers | Ensure the URL is publicly accessible without login/CAPTCHA walls. |

---

<p align="center"><b>Universal RAG System User Manual</b> • Made with ❤️ using Streamlit & Groq</p>
