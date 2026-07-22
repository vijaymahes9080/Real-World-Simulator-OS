#!/bin/bash
# Unix Launch Script for Real-World Simulator OS

echo -e "\033[36m==============================================\033[0m"
echo -e "\033[36mStarting Real-World Simulator OS Service Suite\033[0m"
echo -e "\033[36m==============================================\033[0m"

# Check if environment setup exists
if [ ! -d "backend/venv" ]; then
    echo -e "\033[33mEnvironment not found. Running setup first...\033[0m"
    bash scripts/setup_unix.sh
fi

# Trap exits to kill background processes
trap "kill 0" EXIT

# 1. Start Backend
echo -e "\nLaunching Python FastAPI backend (Port 8000)..."
cd backend
./venv/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
cd ..

# 2. Start Frontend
echo -e "Launching React Vite UI client (Port 3000)..."
cd frontend
npm run dev &
cd ..

echo -e "\nBoth processes launched!"
echo -e "\033[36m----------------------------------------------\033[0m"
echo -e "Access Console: \033[33mhttp://localhost:3000\033[0m"
echo -e "Backend Docs:   \033[33mhttp://127.0.0.1:8000/docs\033[0m"
echo -e "\033[36m----------------------------------------------\033[0m"
echo -e "Press Ctrl+C to terminate both servers."

# Wait for background jobs to finish (which is infinite until interrupted)
wait
