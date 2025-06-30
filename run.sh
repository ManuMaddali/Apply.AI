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
