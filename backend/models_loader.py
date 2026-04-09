import os
import pickle
import warnings

from sklearn.exceptions import InconsistentVersionWarning

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")


def load_model(filename):
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "rb") as file:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", InconsistentVersionWarning)
                    return pickle.load(file)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None

    print(f"Warning: File '{filename}' not found at {path}")
    return None


# --- LOAD THE MODELS & SCALERS ---
print(f"Searching for models in: {MODELS_DIR}")

diabetes_model = load_model("diabetes_model.sav")
heart_model = load_model("heart_model.sav")
parkinsons_model = load_model("parkinsons_model.sav")
liver_model = load_model("liver_model.sav")
parkinsons_scaler = load_model("parkinsons_scaler.sav")

if all([diabetes_model, heart_model, parkinsons_model, liver_model, parkinsons_scaler]):
    print("All models and scalers loaded successfully.")
else:
    print("Check the filenames in your 'models' folder. One or more files failed to load.")
