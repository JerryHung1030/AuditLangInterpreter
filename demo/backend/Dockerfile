# Dockerfile

# Use the official Python 3.10 image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files to the working directory
COPY . .

# create log config
RUN echo "version: 1\nhandlers:\n  console:\n    class: logging.StreamHandler\n    formatter: default\nformatters:\n  default:\n    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'\nroot:\n  handlers: [console]\n  level: INFO" > /app/uvicorn_log_config.yaml

# Expose port 8080 for the backend
EXPOSE 8080

# Command to run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "/app/uvicorn_log_config.yaml"]
