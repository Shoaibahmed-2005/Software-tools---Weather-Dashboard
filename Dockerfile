# Experiment 8 — Docker Deployment
# Build: docker build -t weather-station .
# Run:   docker run -p 5000:5000 weather-station

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY server/     ./server/
COPY templates/  ./templates/
COPY static/     ./static/

# Expose Flask port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask server
CMD ["python", "server/app.py"]
