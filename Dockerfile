# Base image for Python
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Expose the port (optional if using a health check)
EXPOSE 8080

# Command to run the application
CMD ["python", "qualitay.py"]
