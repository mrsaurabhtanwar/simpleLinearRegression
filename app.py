"""
0. import the libraries
1. Initialize FastAPI and setup logging
2. Load the predication artifacts
3. Define the expected incoming data structure
4. Create the prediction endpoint
5. Integrate SQL into API using the SQLAlchemy

"""


import joblib
import numpy as np
import time
import logging
from pathlib import Path
from datetime import datetime

from sqlalchemy import create_engine, Column, Float, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="Height Predication Service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "linear_regression_model.joblib"
SCALER_PATH = BASE_DIR / "standard_scaler.joblib"

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    logging.error(f"Failed to load the model artificates : {e}")

class InferenceInput(BaseModel):
    weight_lbs: float


engine = create_engine("sqlite:///weight_height_prediction.db", connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Height(Base):
    __tablename__ = "weight_height_prediction"
    id = Column(Integer, primary_key=True)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    date_time = Column(DateTime, nullable=False)
    latency = Column(Float, nullable=False)
    error = Column(String, default=None)
    
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/predict")
def predict_height(data: InferenceInput, db: Session = Depends(get_db)):
    current_dt = datetime.now()
    start_time = time.time()

    if data.weight_lbs <= 0:
        raise HTTPException(status_code=400, detail="Weight must be a positive number.")
    
    try:
        # Preprocess: Scale the input
        scaled_input = scaler.transform([[data.weight_lbs]])

        # Predict
        prediction = model.predict(scaled_input)
        predict_height = float(prediction[0][0])

        # Calculate latency (Crucial MLOps metric!)
        latency = time.time() - start_time
        db.add(
            Height(
                weight=data.weight_lbs, 
                height=predict_height, 
                date_time=current_dt, 
                latency=latency,
                error=None
            ) 
        )
        db.commit()

        return {
            "Predicted_height_inches": round(predict_height, 2),
            "status": "success",
            "latency_seconds": round(latency, 4)
        }
    
    except Exception as e:
        logging.error(f"Inference error : {e}")
        db.rollback()
        db.add(
            Height(
                weight=data.weight_lbs, 
                height=0, 
                date_time=current_dt,
                latency=0, 
                error=str(e)

            )
        )
        db.commit()
        raise HTTPException(status_code=500, detail="Internal server error during predication.")



