# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app

# Install dependencies
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app

# Expose default port for Render
EXPOSE 10000

# Launch the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
