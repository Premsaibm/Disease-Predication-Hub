import os
import pandas as pd
import numpy as np
import traceback
import pickle
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Custom Imports
import database  
# Updated loader names to match the new models you just trained
from models_loader import diabetes_model, heart_model, parkinsons_model, liver_model, parkinsons_scaler
from chatbot import get_chatbot_response

app = FastAPI(title="Disease Prediction Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class PredictRequest(BaseModel):
    username: str
    disease: str
    values: list

class ChatRequest(BaseModel):
    question: str
    disease: str


def extract_confidence(model, X):
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        return round(float(np.max(proba)) * 100, 2)
    return None

@app.on_event("startup")
def startup():
    database.init_db()

# --- PREDICTION LOGIC ---

@app.post("/predict/diabetes")
def predict_diabetes(req: PredictRequest):
    try:
        # UPDATE: Now expecting 14 features based on the new clinical dataset
        if len(req.values) != 14:
            raise ValueError(f"Model expects 14 inputs, but received {len(req.values)}")

        # Convert to numpy array
        X = np.array(req.values, dtype=float).reshape(1, -1)
        
        # Predict using the 83% accuracy Tuned Random Forest
        prediction = diabetes_model.predict(X)[0]
        confidence = extract_confidence(diabetes_model, X)
        
        pred_val = int(prediction)
        result = "Diabetic" if pred_val == 1 else "Not Diabetic"
        
        database.log_prediction(req.username, "Diabetes", req.values, result, confidence)
        
        report = f"Patient: {req.username}\nPrediction: {result}\n\nDisclaimer: Based on clinical risk markers. Consult a doctor."
        return {"result": bool(pred_val), "report": report, "confidence": confidence}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/heart")
def predict_heart(req: PredictRequest):
    try:
        # Updated to match the UCI Fixed dataset (13 features)
        if len(req.values) != 13:
            raise ValueError(f"Model expects 13 inputs, but received {len(req.values)}")

        X = np.array(req.values, dtype=float).reshape(1, -1)
        
        # Predict using the 88.5% accuracy Logistic Regression
        prediction = heart_model.predict(X)[0]
        confidence = extract_confidence(heart_model, X)
        
        pred_val = int(prediction)
        result = "Heart Disease Detected" if pred_val == 1 else "Normal Heart"
        
        database.log_prediction(req.username, "Heart", req.values, result, confidence)
        
        report = f"Patient: {req.username}\nPrediction: {result}\n\nDisclaimer: Results based on UCI cardiovascular markers."
        return {"result": bool(pred_val), "report": report, "confidence": confidence}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/parkinsons")
def predict_parkinsons(req: PredictRequest):
    try:
        # Voice data typically has 22 features
        if len(req.values) != 22:
            raise ValueError(f"Model expects 22 inputs, but received {len(req.values)}")

        # Convert to array
        X = np.array(req.values, dtype=float).reshape(1, -1)
        
        # CRITICAL: Parkinson's model was trained with a Scaler (89% accuracy)
        # We must transform the user input before predicting
        X_scaled = parkinsons_scaler.transform(X)
        
        prediction = parkinsons_model.predict(X_scaled)[0]
        confidence = extract_confidence(parkinsons_model, X_scaled)
        
        pred_val = int(prediction)
        result = "Parkinson's Detected" if pred_val == 1 else "Healthy"
        
        database.log_prediction(req.username, "Parkinsons", req.values, result, confidence)
        
        report = f"Patient: {req.username}\nPrediction: {result}\n\nDisclaimer: Based on voice frequency analysis."
        return {"result": bool(pred_val), "report": report, "confidence": confidence}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/liver")
async def predict_liver(req: PredictRequest):
    try:
        if liver_model is None:
            raise HTTPException(
                status_code=503,
                detail="Liver model is unavailable. Re-export it with the current scikit-learn version or install the version used to train it."
            )

        # Liver dataset features (10 features)
        feature_names = [
            'Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin', 
            'Alkaline_Phosphotase', 'Alamine_Aminotransferase', 
            'Aspartate_Aminotransferase', 'Total_Protiens', 
            'Albumin', 'Albumin_and_Globulin_Ratio'
        ]

        if len(req.values) != len(feature_names):
            raise ValueError(f"Model expects {len(feature_names)} inputs, but received {len(req.values)}")

        liver_values = list(req.values)
        gender_value = liver_values[1]
        if gender_value in [1, "1", "Male", "male"]:
            liver_values[1] = "Male"
        elif gender_value in [0, "0", "Female", "female"]:
            liver_values[1] = "Female"

        # Use DataFrame for liver model as it handles categorical 'Gender' better
        X = pd.DataFrame([liver_values], columns=feature_names)
        
        prediction = liver_model.predict(X)[0]
        confidence = extract_confidence(liver_model, X)
        
        # Interpretation based on dataset labels (1 = Disease, 2 = Healthy)
        is_disease = True if int(prediction) == 1 else False
        status = "Liver Disease Detected" if is_disease else "Healthy Liver"
        
        database.log_prediction(req.username, "Liver", req.values, status, confidence)
        
        return {"result": is_disease, "report": f"Status: {status}", "confidence": confidence}
    except Exception as e:
        print(f"LIVER ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- UTILS & CHAT ---

@app.get("/history")
def history(username: str = Query(...)):
    return database.get_user_history(username)


@app.get("/admin/history")
def admin_history():
    return database.get_all_history()


@app.get("/admin/status")
def admin_status():
    db_status = database.get_system_status()
    return {
        "model_status": {
            "diabetes": diabetes_model is not None,
            "heart": heart_model is not None,
            "parkinsons": parkinsons_model is not None and parkinsons_scaler is not None,
            "liver": liver_model is not None,
        },
        "backend": db_status["database"],
        "total_users": db_status["total_users"],
        "total_predictions": db_status["total_predictions"],
    }

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        answer = get_chatbot_response(req.question, req.disease)
        return {"answer": answer}
    except Exception as e:
        return {"answer": "I'm having trouble providing medical insights right now."}

if __name__ == "__main__":
    import uvicorn
    # Make sure port 8000 is free or change here
    uvicorn.run(app, host="127.0.0.1", port=8000)
