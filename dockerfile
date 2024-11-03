# Dockerfile
FROM python:3.10-slim
 
WORKDIR /app
 
# Copy the requirements first
COPY requirements.txt .
 
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the app directory into the container
COPY ./app /app/app
 
# Expose the port for FastAPI
EXPOSE 8000
 
# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]