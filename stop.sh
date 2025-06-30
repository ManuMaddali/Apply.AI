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
