"""
0. import the libraries
1. Initialize FastAPI and setup logging
2. Load the predication artifacts
3. Define the expected incoming data structure
4. Create the prediction endpoint
5. Integrate MySQL into API

"""


import joblib
import numpy as np
import time
import logging
# import mysql.connector
from pathlib import Path

from fastapi import FastAPI, HTTPException
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


# def save_predication_to_db(weight: float, predication: float, latency: float):
    # try:
    #     # connect to XAMPP mysql 
    #     connection = mysql.connector.connect(
    #         host="host.docker.internal",
    #         user="root",
    #         password="",
    #         database="mlops_db"
    #     )
    #     cursor = connection.cursor()
    #     # sql raw query
    #     sql_query = """
    #         INSERT INTO predication_logs (weight_lbs, predicated_height_inches, latency_seconds) VALUES (%s, %s, %s)
    #     """
    #     # Execute the query safely using placeholders to prevent SQL injection
    #     cursor.execute(sql_query, (weight, predication, latency))

    #     # commit the transcation to save it permanently
    #     connection.commit()

    #     cursor.close()
    #     connection.close()
    #     logging.info("Successfully logged predication to MySQL database.")

    # except Exception as e:
    #     logging.error(f"Database logging error : {e}")


@app.post("/predict")
def predict_height(data: InferenceInput):
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

        # Save the workflow execution to your database
        # save_predication_to_db(
        #     weight=data.weight_lbs,
        #     predication=round(predict_height, 2),
        #     latency=round(latency, 4)
        # )

        return {
            "Predicted_height_inches": round(predict_height, 2),
            "status": "success",
            "latency_seconds": round(latency, 4)
        }
    except Exception as e:
        logging.error(f"Interence error : {e}")
        raise HTTPException(status_code=500, detail="Internal server error during predication.")



