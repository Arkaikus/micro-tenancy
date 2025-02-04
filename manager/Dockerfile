# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install FastAPI and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY main.py .

# Command to run the FastAPI application using uvicorn
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]