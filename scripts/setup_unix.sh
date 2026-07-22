#!/bin/bash
# Unix Setup Script for Real-World Simulator OS

echo -e "\033[36m==============================================\033[0m"
echo -e "\033[36mSetting up Real-World Simulator OS (No Docker)\033[0m"
echo -e "\033[36m==============================================\033[0m"

# 1. Check commands
if ! command -v python3 &> /dev/null; then
    echo -e "\033[31mError: Python3 is required but was not found. Please install Python and try again.\033[0m"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "\033[31mError: NodeJS (npm) is required but was not found. Please install Node.js and try again.\033[0m"
    exit 1
fi

# 2. Configure Backend Venv
echo -e "\n\033[32m[1/4] Configuring Python Virtual Environment...\033[0m"
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
fi

# 3. Install Python Dependencies
echo -e "\n\033[32m[2/4] Installing Backend dependencies...\033[0m"
backend/venv/bin/pip install -r backend/requirements.txt

# 4. Configure Frontend Packages
echo -e "\n\033[32m[3/4] Installing Frontend npm dependencies...\033[0m"
cd frontend
npm install
cd ..

# 5. Success
echo -e "\n\033[32m[4/4] Installation Complete!\033[0m"
echo -e "\033[36m----------------------------------------------\033[0m"
echo -e "To start the application, execute:"
echo -e "  bash scripts/run_unix.sh"
echo -e "\033[36m----------------------------------------------\033[0m"
