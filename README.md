AI Chatbot for BIM Design - Level 1
=================================

Project Overview
----------------
This project is a simple AI-assisted BIM design chatbot built with Flask. It provides a frontend interface and a backend API that uses Google Gemini to extract structural beam design inputs from natural language and calculate reinforcement requirements for RCC beams.

Repository Structure
--------------------
- backend/
  - app.py            : Flask application routes and server startup
  - chatbot.py        : Gemini API integration, prompt generation, and request handling
  - calculator_2.py   : RCC beam design calculations, moment, steel area, shear checks, and safety logic
  - test_api.py       : API test script (if present)
  - .env              : Environment variables file (not committed)
  - venv/             : Python virtual environment for backend dependencies
- static/
  - script.js         : Frontend JavaScript for chat interaction
  - style.css         : Frontend styling
- templates/
  - index.html        : Frontend HTML page
- .gitignore          : Git ignore rules for environment files and caches
- read_me.txt         : Project documentation and setup instructions

Key Features
------------
- Natural language chatbot interface for beam design requests
- Backend validation for RCC beam parameters (span, load, concrete grade, steel grade, dimensions)
- Beam design logic with flexure, shear, deflection, and reinforcement suggestions
- Google Gemini integration via `google.generativeai`

Setup Instructions
------------------
1. Install Python 3.11+ if not already installed.
2. Create a virtual environment in the project root:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install flask python-dotenv google-generativeai
   ```
4. Create a `.env` file in `backend/` with your Google Gemini API key:
   ```text
   GEMINI_API_KEY=your_api_key_here
   ```
5. Run the backend server from the `backend` folder:
   ```powershell
   cd backend
   python app.py
   ```
6. Open the app in your browser at:
   ```text
   http://127.0.0.1:5000
   ```

Environment and Secrets
-----------------------
- Do not commit `.env` or any API keys to GitHub.
- The `.gitignore` file excludes `.env`, virtual environments, and Python cache files.
- Keep your Gemini API key private and only store it locally.

Usage
-----
- Use the frontend page to send a beam design request.
- The backend `/chat` endpoint receives JSON like:
  ```json
  { "message": "Design a 6m RCC beam for 25 kN/m load with fck 25, fy 415, b 300, d 500" }
  ```
- The server returns a JSON response with design status, reinforcement, shear status, and explanation.

Notes
-----
- The current backend uses `app.run(debug=True)` for development only.
- If you want to publish or deploy, switch `debug=False` and use a production server such as Gunicorn or Waitress.
- The `.gitignore` file is already configured to ignore local environment data and temporary files.
