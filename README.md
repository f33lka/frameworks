# Habit Tracker Lite

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](#)
[![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)](#)
[![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?logo=sqlite)](#)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=000)](#)
[![MUI](https://img.shields.io/badge/MUI-5-007FFF?logo=mui)](#)
[![Recharts](https://img.shields.io/badge/Recharts-2.x-ff7300)](#)

Трекер привычек: добавляй привычки и отмечай выполнение по дням. График активности за 14 дней.

## 🚀 Быстрый старт
**Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
# Linux/Mac:
# source .venv/bin/activate && pip install -r requirements.txt && python app.py
```
**Frontend**
```bash
cd frontend
npm install
npm start
```
API: `http://localhost:5000`, UI: `http://localhost:3000`

## 🔌 API (кратко)
`GET/POST/PATCH /api/habits`, `GET/POST/DELETE /api/checkins`, `GET /api/health`
