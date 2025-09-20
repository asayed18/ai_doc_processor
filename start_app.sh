#!/bin/bash

echo "🚀 Starting AI Document Processor Application..."
echo "This will start both backend and frontend services."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

# Start backend
echo "📡 Starting backend (FastAPI)..."
cd backend
pip install -r requirements.txt >/dev/null 2>&1
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend  
echo "🌐 Starting frontend (Next.js)..."
cd frontend
npm install >/dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started successfully!"
echo ""
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend:  http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo ""
echo "📁 Test documents are in: ./Tender documents/"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait