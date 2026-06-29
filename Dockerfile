# Step 1 starting with an official, lightweight python blueprint
FROM python:3.11-slim

# step 2 Creating a folder name /app inside the container and switch to it
WORKDIR /app

# step 3 copy the dependencies 
COPY requirements.txt .

# Step 4 Install all the required librared inside the container evironment
RUN pip install --no-cache-dir -r requirements.txt

# step 5 Copy your API script and exported ML model files into the container
COPY app.py .
COPY linear_regression_model.joblib .
COPY standard_scaler.joblib .

# step 6 export port 8000 so we can access the API from outside the container
EXPOSE 8000

# step 7 the execution command to launch your FastAPI app when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

