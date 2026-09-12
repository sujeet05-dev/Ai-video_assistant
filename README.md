# 🎙️ AI Video Assistant — Meeting Intelligence & RAG Chatbot

An intelligent meeting assistant and video summarization pipeline that transforms video/audio recordings and YouTube links into actionable insights, transcripts, summaries, and an interactive **Retrieval-Augmented Generation (RAG)** chatbot.

Built with **Streamlit**, **LangChain**, **OpenAI Whisper**, **Mistral AI**, **Sarvam AI**, and **ChromaDB**.

---

## 🌟 Key Features

- 🎥 **Multi-Source Ingestion**:
  - Direct YouTube link extraction using `yt-dlp`.
  - Local video/audio file upload (`.mp4`, `.mkv`, `.wav`, `.mp3`).
  - Automatic audio normalization & conversion to 16kHz mono WAV via `pydub` and `FFmpeg`.

- 🗣️ **Dual Speech-to-Text Support**:
  - **OpenAI Whisper**: High-accuracy local speech-to-text transcription (configurable models: `tiny` to `large`).
  - **Sarvam AI (`saaras:v2.5`)**: High-fidelity Speech-to-Text & Translation specifically optimized for Hinglish and Indian languages.

- 🧠 **Smart Meeting Intelligence**:
  - **Automatic Title Generation**: Context-aware title extraction for meetings/lectures.
  - **Executive Summaries**: High-level and comprehensive meeting summaries.
  - **Action Items**: Identifies tasks, assignees, and next steps.
  - **Key Decisions**: Pinpoints conclusions and strategic choices made during the discussion.
  - **Open Questions**: Flags unresolved topics or follow-ups.

- 💬 **Interactive RAG Chatbot**:
  - Semantic vector search powered by **ChromaDB** and HuggingFace `all-MiniLM-L6-v2` embeddings.
  - Conversational Q&A backed by **Mistral AI (`open-mistral-7b`)** to answer questions grounded strictly in the transcript context.

- 💻 **Dual Interface**:
  - **Web UI**: Modern, glassmorphic, responsive interface built with **Streamlit**.
  - **CLI**: Fast terminal-based execution via `main.py`.

---

## 🏗️ Architecture & Pipeline

```
┌───────────────────────────┐
│ YouTube URL / Local Audio │
└─────────────┬─────────────┘
              │
              ▼
   [ Audio Extraction & ]
   [ Chunking (pydub)   ]
              │
              ▼
   [ Transcription:     ]  ──► (English: Whisper / Hinglish: Sarvam AI)
   [ Speech-to-Text     ]
              │
              ├─────────────────────────────────────────────────┐
              ▼                                                 ▼
   [ Meeting Intelligence ]                          [ Vector Store & RAG ]
   ├─ Meeting Title                                  ├─ Recursive Text Splitter
   ├─ Executive Summary                              ├─ HuggingFace MiniLM Embeddings
   ├─ Action Items                                   ├─ ChromaDB Vector Store
   ├─ Key Decisions                                  └─ LangChain + Mistral AI
   └─ Open Questions                                              │
                                                                  ▼
                                                      💬 Interactive Q&A Chat
```

---

## 📂 Project Structure

```bash
AI-Video-Assistant/
├── core/
│   ├── extractor.py        # Extracts action items, decisions & questions
│   ├── rag_engine.py       # LangChain RAG pipeline with Mistral AI
│   ├── summarizer.py       # Summarization and title generation
│   ├── transcriber.py      # Whisper & Sarvam AI STT integration
│   └── vector_store.py     # ChromaDB vector store & embeddings
├── utils/
│   └── audio_processor.py  # yt-dlp downloader, conversion & chunking
├── app.py                  # Streamlit web application
├── main.py                 # Terminal / CLI entry point
├── packages.txt            # System dependencies (ffmpeg)
├── Requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.10+** installed on your system.
- **FFmpeg**:
  - **Windows**: Install via `winget install Gyan.FFmpeg` or `choco install ffmpeg`, or add `ffmpeg` to your system `PATH`.
  - **Linux / macOS**: `sudo apt install ffmpeg` or `brew install ffmpeg`.

---

### 2. Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sujeet05-dev/Ai-video_assistant.git
   cd Ai-video_assistant
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r Requirements.txt
   ```

---

### 3. Environment Configuration

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
# Required for RAG Chat & Insights
MISTRAL_API_KEY="your_mistral_api_key_here"

# Whisper model for local transcription (tiny, base, small, medium, large)
WHISPER_MODEL="small"

# Required for Hinglish / Indian language transcription & translation
SARVAM_API_KEY="your_sarvam_api_key_here"
```

> **API Key Resources:**
> - Get a Mistral API key: [Mistral AI Console](https://console.mistral.ai/)
> - Get a Sarvam AI key: [Sarvam AI Dashboard](https://www.sarvam.ai/)

---

## 🖥️ Usage

### Option A: Launch the Streamlit Web Application (Recommended)

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.
1. Enter a YouTube URL or upload a video/audio file.
2. Select the audio language (`English` or `Hinglish / Indian Languages`).
3. Click **Process Video / Audio**.
4. View the generated Title, Summary, Action Items, Key Decisions, and chat with the meeting via the conversational assistant.

---

### Option B: Run via CLI

```bash
python main.py
```

Follow the interactive prompts in the terminal to process media and chat with your transcript.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Web UI** | [Streamlit](https://streamlit.io/) |
| **Orchestration** | [LangChain](https://www.langchain.com/) |
| **Speech-to-Text** | [OpenAI Whisper](https://github.com/openai/whisper) & [Sarvam AI](https://www.sarvam.ai/) |
| **LLM & Inference** | [Mistral AI (`open-mistral-7b`)](https://mistral.ai/) |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) |
| **Embeddings** | [Sentence Transformers (`all-MiniLM-L6-v2`)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| **Audio Processing** | [yt-dlp](https://github.com/yt-dlp/yt-dlp), [pydub](https://github.com/jiaaro/pydub), [FFmpeg](https://ffmpeg.org/) |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
