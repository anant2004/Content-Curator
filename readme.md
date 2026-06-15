# Content Curator 🎯

AI-powered content generation platform for Tata Steel. Upload documents and generate polished presentations, reports, SOPs, handbooks, video scripts, and more — powered by LLMs.

## Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI + Python 3.11+
- **LLM**: OpenRouter (free tier — `mistralai/mistral-7b-instruct:free`)
- **File parsing**: PyMuPDF, python-docx, python-pptx
- **Export**: python-pptx (PPTX), python-docx (Word), openpyxl (Excel), ReportLab (PDF)
- **Deploy**: Render (free tier)

---

## ⚡ Quick Start — Streamlit Frontend

### Step 1 — First Time Setup (do this once)

```powershell
# Navigate to the project folder
cd "...\Content-Curator"

# Create a virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install Streamlit frontend dependencies
pip install streamlit python-pptx python-docx openpyxl reportlab pandas

# Install backend dependencies
pip install -r backend/requirements.txt
```

> **Note:** If `Activate.ps1` is blocked by PowerShell, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 2 — Run the App (every time)

```powershell
cd "...\Content-Curator"

.venv\Scripts\python.exe -m streamlit run frontend/streamlit_app/app.py
```

Then open **http://localhost:8501** in your browser.

> Run this from the `Content-Curator` folder (project root), not from inside `frontend/`.

---

## Dependencies at a Glance

| Package | Purpose |
|---|---|
| `streamlit` | Frontend UI framework |
| `python-pptx` | PPTX export |
| `python-docx` | Word / DOCX export |
| `openpyxl` | Excel export |
| `reportlab` | PDF export |
| `pandas` | Data tables in the app |
| `backend/requirements.txt` | FastAPI backend (file parsing, LLM, etc.) |

---

## Get a Free OpenRouter Key

1. Sign up at https://openrouter.ai
2. Go to **Keys → Create Key**
3. Free models available: `mistralai/mistral-7b-instruct:free`, `google/gemma-3-4b-it:free`
4. Add to `.env` as `OPENROUTER_API_KEY=sk-or-...`

---

## API Flow (Backend)

```
POST /api/v1/ingest/upload        → { session_id }
POST /api/v1/ingest/paste         → { session_id }

POST /api/v1/generate/outline     → { outline[] }
POST /api/v1/generate/slides      → { slides[] }

PATCH /api/v1/slides/edit         → { updated_slide }
PUT  /api/v1/slides/{id}/{num}    → { slide }

POST /api/v1/export               → { download_url }
GET  /api/v1/export/download/{f}  → file download
```

API docs available at http://127.0.0.1:8000/docs when backend is running.

---

## Themes

| Theme | Primary | Use Case |
|-------|---------|----------|
| `midnight_executive` | Navy `#1E2761` | Corporate / Finance |
| `forest_moss` | Forest `#2C5F2D` | Sustainability / Nature |
| `coral_energy` | Coral `#F96167` | Startup / Marketing |
| `charcoal_minimal` | Charcoal `#36454F` | Minimal / Design |

---

## Running Tests

```bash
pytest backend/tests/ -v
```

---

## Deploy to Render

1. Push to GitHub
2. Connect repo in Render dashboard
3. Set `OPENROUTER_API_KEY` in Environment
4. Deploy — `render.yaml` handles the rest

---

## Project Structure

```
Content-Curator/
├── frontend/
│   └── streamlit_app/
│       ├── app.py           # Streamlit entry point — run this
│       ├── state.py         # Session state management
│       ├── api_client.py    # Backend API client
│       ├── exporters.py     # DOCX / XLSX / PPTX / PDF exporters
│       ├── components/      # UI components
│       ├── services/        # Frontend services
│       ├── styles/          # CSS styles
│       └── config/          # Configuration & mock data
├── backend/
│   ├── requirements.txt     # Backend Python dependencies
│   └── app/
│       ├── main.py          # FastAPI app + CORS + routes
│       ├── config.py        # Settings via pydantic-settings
│       ├── api/             # Route handlers
│       │   ├── ingestion.py
│       │   ├── generation.py
│       │   ├── slides.py
│       │   └── export.py
│       ├── services/
│       │   ├── ingestion/   # PDF, DOCX, PPTX, email parsers
│       │   ├── llm/         # OpenRouter client + prompt templates
│       │   └── generation/  # python-pptx builder + PDF builder
│       ├── schemas/         # Pydantic request/response models
│       └── utils/           # Logger, file utilities
└── .streamlit/
    └── config.toml          # Streamlit light theme (run app from project root)
```
