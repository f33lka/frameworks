# Defects Control Center — Flask + SQLite + React

## Быстрый старт

### Backend
```bash
cd backend
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py   # http://127.0.0.1:5000
```
Демо: `admin@example.com / admin123`

### Frontend
```bash
cd frontend
npm i
npm run dev   # http://127.0.0.1:5173
```

### Тесты
```bash
cd backend
pytest -q
```
