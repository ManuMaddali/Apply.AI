#!/bin/bash

echo "🚀 Setting up AI Resume Tailoring App with LangChain..."

# Check Python version compatibility
echo "🔍 Checking Python version compatibility..."
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python version: $PYTHON_VERSION"

# Check if Python version is compatible
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  WARNING: Python 3.13 detected!"
    echo "   Most LangChain and ML libraries don't support Python 3.13 yet."
    echo "   Recommended versions: Python 3.8, 3.9, 3.10, 3.11, or 3.12"
    echo ""
    echo "📋 TO FIX THIS:"
    echo "1. Install Python 3.11 or 3.12:"
    echo "   brew install python@3.11"
    echo "2. Use specific Python version:"
    echo "   python3.11 -m venv resume_env"
    echo "3. Or continue anyway (may have issues)"
    echo ""
    read -p "Continue with Python 3.13? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Please install Python 3.8-3.12 and try again."
        exit 1
    fi
    echo "⚠️  Proceeding with Python 3.13 (expect some package failures)..."
fi

# Create project directories
echo "📁 Creating project structure..."
mkdir -p backend/utils
mkdir -p backend/routes
mkdir -p backend/uploads
mkdir -p backend/generated_resumes
mkdir -p backend/vector_stores
mkdir -p frontend/components
mkdir -p frontend/pages

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv resume_env
source resume_env/bin/activate

# Upgrade pip and setuptools for Python 3.13 compatibility
echo "⬆️ Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install core dependencies first
echo "📦 Installing core Python dependencies..."
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install python-multipart==0.0.6
pip install python-docx==1.1.0
pip install PyPDF2==3.0.1
pip install beautifulsoup4==4.12.2
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install aiofiles==23.2.0
pip install reportlab==4.0.7

# Install OpenAI with latest version for Python 3.13 compatibility
echo "🤖 Installing OpenAI..."
pip install openai==1.93.0

# Install LangChain dependencies (with fallback versions)
echo "🔗 Installing LangChain dependencies..."
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "   Using Python 3.13 compatible versions..."
    pip install --no-deps langchain || echo "⚠️ LangChain install failed, will use fallback"
    pip install --no-deps langchain-openai || echo "⚠️ LangChain-OpenAI install failed, will use fallback"
    pip install --no-deps langchain-community || echo "⚠️ LangChain-Community install failed, will use fallback"
else
    pip install langchain==0.1.0
    pip install langchain-openai==0.0.2
    pip install langchain-community==0.0.10
fi

# Install vector and ML dependencies (with fallback for Python 3.13)
echo "🧠 Installing ML dependencies..."
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "   Attempting Python 3.13 compatible versions..."
    pip install numpy==1.24.3 || pip install numpy
    pip install faiss-cpu || echo "⚠️ FAISS install failed - RAG features may be limited"
    pip install sentence-transformers || echo "⚠️ Sentence-transformers install failed"
    pip install chromadb || echo "⚠️ ChromaDB install failed - using alternative storage"
else
    pip install faiss-cpu==1.7.4
    pip install chromadb==0.4.18
    pip install sentence-transformers==2.2.2
    pip install numpy==1.24.3
fi

# Install text processing dependencies
echo "📝 Installing text processing dependencies..."
pip install tiktoken==0.5.2 || pip install tiktoken
pip install Levenshtein==0.25.0

# Create .env file template
echo "📝 Creating .env template..."
cat > .env << EOL
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# FastAPI Configuration
HOST=localhost
PORT=8000

# CORS Settings
FRONTEND_URL=http://localhost:3000

# LangChain Configuration
LANGCHAIN_VERBOSE=False
LANGCHAIN_CACHE=True

# Vector Store Configuration
VECTOR_STORE_PATH=./vector_stores
EMBEDDING_MODEL=text-embedding-ada-002

# Resume Processing Settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,docx
TEMP_DIR=./temp

# Python 3.13 Compatibility Mode
PYTHON_VERSION=$PYTHON_VERSION
FALLBACK_MODE=true
EOL

cd ..

# Setup frontend
echo "⚛️ Setting up React frontend..."
cd frontend

# Install Node.js dependencies with security fixes
echo "📦 Installing Node.js dependencies..."
npm install react@18.2.0
npm install react-dom@18.2.0  
npm install next@14.0.0
npm install axios@1.6.0

# Install dev dependencies with security fixes
echo "🔧 Installing dev dependencies..."
npm install --save-dev tailwindcss@3.3.6
npm install --save-dev postcss@8.4.31
npm install --save-dev autoprefixer@10.4.16
npm install --save-dev @types/node@20.8.10
npm install --save-dev @types/react@18.2.33
npm install --save-dev @types/react-dom@18.2.14
npm install --save-dev eslint@8.57.1  # Updated for security
npm install --save-dev eslint-config-next@14.0.0

# Fix security vulnerabilities
echo "🔒 Fixing security vulnerabilities..."
npm audit fix || echo "⚠️ Some vulnerabilities couldn't be auto-fixed"

# Initialize Tailwind CSS
echo "🎨 Setting up Tailwind CSS..."
npx tailwindcss init -p --yes

# Create Tailwind config
cat > tailwind.config.js << EOL
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  plugins: [],
}
EOL

# Create global CSS with Tailwind
mkdir -p styles
cat > styles/globals.css << EOL
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Diff highlighting */
.diff-added {
  background-color: #d4edda;
  border-left: 4px solid #28a745;
  padding-left: 8px;
}

.diff-removed {
  background-color: #f8d7da;
  border-left: 4px solid #dc3545;
  padding-left: 8px;
}

.diff-modified {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
  padding-left: 8px;
}
EOL

cd ..

# Create run script with better error handling
echo "🔧 Creating enhanced run script..."
cat > run.sh << 'EOL'
#!/bin/bash

echo "🚀 Starting AI Resume Tailoring App with LangChain..."

# Function to kill processes on ports
cleanup_ports() {
    echo "🧹 Cleaning up existing processes..."
    
    # Kill processes on port 8000 (backend)
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    # Kill processes on port 3000 (frontend)  
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    sleep 2
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is still in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Cleanup existing processes
cleanup_ports

# Verify ports are available
if ! check_port 8000 || ! check_port 3000; then
    echo "⚠️  Ports still in use. Please wait and try again."
    exit 1
fi

echo "✅ Ports are clean and ready"

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Please create backend/.env file with your OpenAI API key"
    echo "📝 Template created at backend/.env"
    exit 1
fi

# Start backend in background
echo "🐍 Starting Python backend..."
cd backend
source resume_env/bin/activate

# Check Python version and warn if using 3.13
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Running with Python 3.13 - some features may be limited"
fi

# Check if OpenAI API key is set
if ! grep -q "sk-" .env 2>/dev/null; then
    echo "⚠️  Please add your OpenAI API key to backend/.env"
    echo "   OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Start backend with error handling
echo "🔄 Starting backend server..."
nohup python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 8

# Check if backend is running
if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "❌ Backend failed to start. Check backend.log for details."
    echo "📋 Last 20 lines of backend.log:"
    tail -20 backend.log
    exit 1
fi

echo "✅ Backend is running on http://localhost:8000"

# Start frontend
echo "⚛️ Starting React frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
echo "🔄 Starting frontend server..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 15

# Check if frontend is running
if ! curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "❌ Frontend failed to start. Check frontend.log for details."
    echo "📋 Last 20 lines of frontend.log:"
    tail -20 frontend.log
    exit 1
fi

echo "✅ Frontend is running on http://localhost:3000"

echo ""
echo "🎉 AI Resume Tailoring App is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  PYTHON 3.13 MODE:"
    echo "   Some LangChain features may be limited"
    echo "   RAG system might run in fallback mode"
    echo ""
fi
echo "🆕 FEATURES AVAILABLE:"
echo "   🔍 Resume Upload & Tailoring"
echo "   🌐 Job Description Scraping"
echo "   📊 Basic Diff Analysis" 
echo "   💾 Session Management"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "⏹️  To stop: ./stop.sh"

# Save PIDs for stop script
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid
EOL

chmod +x run.sh

# Create enhanced stop script
echo "⏹️  Creating stop script..."
cat > stop.sh << 'EOL'
#!/bin/bash

echo "⏹️  Stopping AI Resume Tailoring App..."

# Function to kill process by PID
kill_pid() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo "🔴 Stopping $name (PID: $pid)..."
        kill -TERM $pid 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "🔪 Force killing $name (PID: $pid)..."
            kill -9 $pid 2>/dev/null
        fi
    fi
}

# Kill processes by saved PIDs
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill_pid $BACKEND_PID "Backend"
    rm .backend_pid
fi

if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill_pid $FRONTEND_PID "Frontend"
    rm .frontend_pid
fi

# Kill any remaining processes on the ports
echo "🧹 Cleaning up remaining processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Clean up log files
rm -f backend.log frontend.log

echo "✅ All processes stopped successfully!"
EOL

chmod +x stop.sh

# Create directory structure info
cat > PROJECT_STRUCTURE.md << 'EOL'
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
EOL

echo ""
echo "🎉 Setup Complete!"
echo ""
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  PYTHON 3.13 DETECTED:"
    echo "   Some packages may have failed to install"
    echo "   App will run in compatibility mode"
    echo "   For best experience, consider using Python 3.11 or 3.12"
    echo ""
fi
echo "📋 Next Steps:"
echo "1. Add your OpenAI API key to backend/.env"
echo "2. Run './run.sh' to start the application"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 Documentation: Read PROJECT_STRUCTURE.md for details"
echo "🆕 New Features: Enhanced AI Resume Tailoring"
echo ""
echo "⚠️  Note: If you encounter issues, try using Python 3.11 or 3.12 for full compatibility" 