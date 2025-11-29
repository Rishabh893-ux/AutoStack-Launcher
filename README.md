# Travel & Lifestyle Agent - Starter

## Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

## Frontend
cd frontend
npm install
npm run dev

Open http://localhost:3000
Make sure backend runs at http://localhost:8000
