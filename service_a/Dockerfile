# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app
RUN touch __init__.py
# Copy the requirements file
COPY service_a/requirements.txt .
COPY middleware/ /app/middleware

# Install FastAPI and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY service_a/main.py .

# Command to run the FastAPI application
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]