#creating dockerfile for backend folder
# Dockerfile for the backend service
# This Dockerfile sets up a Python environment, installs dependencies, and runs the FastAPI application
# using Uvicorn.

FROM python:3.11-slim   

RUN apt-get update && apt-get install -y

WORKDIR /app    

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

