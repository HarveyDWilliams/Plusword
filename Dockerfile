# Use a slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your app will run on
EXPOSE 8501

# Start cron and Gunicorn together
CMD streamlit run Home.py --server.enableCORS false --server.enableXsrfProtection false --server.headless true --server.port 8501 --server.address 0.0.0.0
