# 🚀 AI Resume Tailoring App - LangChain Enhanced

## 📁 Project Structure

```
.
├── backend/                    # Python FastAPI Backend
│   ├── routes/                # API Route Handlers
│   │   ├── upload_resume.py   # Resume Upload & Processing
│   │   ├── scrape_jobs.py     # Job Description Scraping
│   │   └── generate_resumes.py # LangChain Resume Tailoring
│   ├── utils/                 # Utility Modules
│   │   ├── langchain_processor.py  # 🆕 LangChain RAG System
│   │   ├── resume_diff.py     # 🆕 Advanced Diff Analysis
│   │   ├── gpt_prompt.py      # GPT Processing (Fallback)
│   │   ├── resume_editor.py   # PDF/DOCX Processing
│   │   └── job_scraper.py     # Web Scraping Utilities
│   ├── vector_stores/         # 🆕 FAISS Vector Storage
│   ├── uploads/               # Uploaded Resume Files
│   ├── generated_resumes/     # Generated Output Files
│   ├── main.py               # FastAPI Application Entry
│   ├── requirements.txt      # Python Dependencies
│   └── .env                  # Environment Configuration
├── frontend/                  # React Next.js Frontend
│   ├── pages/
│   │   └── index.jsx         # 🆕 Enhanced Main Interface
│   ├── components/
│   │   └── ResumeCard.jsx    # 🆕 Advanced Resume Display
│   ├── styles/
│   │   └── globals.css       # 🆕 Enhanced Styling
│   ├── package.json          # Node.js Dependencies
│   └── tailwind.config.js    # Tailwind Configuration
├── run.sh                    # 🆕 Enhanced Startup Script
├── stop.sh                   # 🆕 Clean Shutdown Script
└── setup.sh                  # 🆕 Complete Installation Script
```

## 🆕 New LangChain Features

### 🔍 RAG (Retrieval-Augmented Generation)
- **Vector Storage**: FAISS-based job description storage
- **Semantic Search**: Find similar job postings for context
- **Industry Intelligence**: Learn from patterns across job descriptions
- **Enhanced Prompting**: Context-aware resume tailoring

### 📊 Advanced Diff Analysis
- **Section-by-Section Comparison**: Track changes in each resume section
- **Enhancement Scoring**: Quantitative assessment of improvements
- **Visual Diff Display**: Highlight additions, modifications, deletions
- **Content Analytics**: Word count, action verbs, keyword analysis

### 💾 Session Management
- **History Tracking**: Save and reload tailoring sessions
- **Version Control**: Compare multiple resume versions
- **Progress Analytics**: Track improvement over time
- **Resume Evolution**: See how your resume develops

### 🧠 Multi-Step Workflows
- **Intelligent Processing**: Step-by-step reasoning chains
- **Memory Systems**: Learn from previous interactions
- **Context Awareness**: Understand job requirements deeply
- **Adaptive Learning**: Improve recommendations over time

## 🚀 Getting Started

1. **Setup**: `./setup.sh`
2. **Configure**: Add OpenAI API key to `backend/.env`
3. **Run**: `./run.sh`
4. **Stop**: `./stop.sh`

## 🎯 Usage Features

- ✅ Upload PDF/DOCX resumes
- ✅ Scrape job descriptions from URLs
- ✅ Enable/disable RAG enhancement
- ✅ Toggle diff analysis
- ✅ View session history
- ✅ Copy/download results
- ✅ Real-time processing status
- ✅ Enhancement scoring
- ✅ Industry insights

## 🔧 Technical Stack

- **Backend**: FastAPI + LangChain + OpenAI
- **Frontend**: Next.js + React + Tailwind CSS
- **AI**: GPT-4o-mini + RAG + Vector Search
- **Storage**: FAISS + File System
- **Processing**: BeautifulSoup + PDF/DOCX Libraries
