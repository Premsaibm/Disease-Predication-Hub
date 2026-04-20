# Disease Predication Hub

A full-stack health screening application that combines machine learning models with a FastAPI backend and a Streamlit frontend. The project supports prediction workflows for diabetes, heart disease, Parkinson's disease, and liver disease, along with user history tracking and an AI-assisted health chatbot.

## Features

- Diabetes risk assessment using clinical markers
- Heart disease prediction using cardiovascular inputs
- Parkinson's screening using voice-analysis features
- Liver disease prediction using lab and demographic values
- FastAPI backend with prediction, history, admin, and chatbot endpoints
- Streamlit frontend with login, dashboard, prediction forms, and history views
- SQLite-based local storage for user accounts and prediction logs
- Groq-powered chatbot with a rule-based fallback when no API key is available

## Project Structure

```text
README.md
requirements.txt
frontend/
backend/
models/
dataset/
  diabetes_risk_factors.csv
  heart_fixed.csv
  Liver Patient Dataset (LPD)_train.csv
  parkinsons_fixed.csv
```

## Requirements

- Python 3.10+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a file at `backend/.env` with:

```env
GROQ_API_KEY=your_groq_api_key_here
```

If no API key is provided, the chatbot still works in fallback mode with simple rule-based responses.

## Run The Project

Start the backend:

```bash
python backend/main.py
```

Start the frontend in a second terminal:

```bash
streamlit run frontend/app.py
```

Backend default URL:

```text
http://127.0.0.1:8000
```

Frontend default URL:

```text
http://localhost:8501
```

## Main API Endpoints

- `POST /predict/diabetes`
- `POST /predict/heart`
- `POST /predict/parkinsons`
- `POST /predict/liver`
- `GET /history`
- `GET /admin/history`
- `GET /admin/status`
- `POST /chat`

## Notes

- This project is for educational and screening purposes only.
- Predictions are not medical diagnoses.
- Keep `backend/.env` private and never commit real API keys.
## How to Use

1. Start backend using: python backend/main.py
2. Start frontend using: streamlit run frontend/app.py
3. Open browser and use the application
