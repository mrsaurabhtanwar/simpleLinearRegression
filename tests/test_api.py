"""
Sample tests for the Height Prediction API
Run with: pytest tests/test_api.py
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, '.')

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'linear_regression_model.joblib'
SCALER_PATH = BASE_DIR / 'standard_scaler.joblib'

# Note: Uncomment and adjust when you have the full app setup
# from app import app, InferenceInput

# client = TestClient(app)


# Test 1: API is accessible
def test_imports():
    """Test that all required dependencies can be imported"""
    import fastapi
    import joblib
    # import mysql.connector
    assert fastapi is not None
    assert joblib is not None
    # assert mysql.connector is not None


# Test 2: Check if model files exist
def test_model_files_exist():
    """Test that required model files are present"""
    assert MODEL_PATH.exists(), "Model file missing"
    assert SCALER_PATH.exists(), "Scaler file missing"


# Test 3: Model can be loaded
def test_model_loading():
    """Test that the model loads without errors"""
    import joblib
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        assert model is not None
        assert scaler is not None
    except Exception as e:
        pytest.fail(f"Failed to load model: {e}")


# Uncomment these tests once your app is fully set up:

# def test_read_root():
#     """Test if root endpoint works"""
#     response = client.get("/")
#     assert response.status_code == 200


# def test_predict_endpoint():
#     """Test if prediction endpoint works"""
#     response = client.post("/predict", json={"weight_lbs": 150})
#     assert response.status_code == 200
#     assert "predicated_height_inches" in response.json()


# def test_invalid_input():
#     """Test if API handles invalid input"""
#     response = client.post("/predict", json={"weight_lbs": "invalid"})
#     assert response.status_code == 422  # Validation error


# def test_prediction_value():
#     """Test if prediction is within reasonable range"""
#     response = client.post("/predict", json={"weight_lbs": 150})
#     data = response.json()
#     assert 50 < data["predicated_height_inches"] < 84  # Reasonable height range
