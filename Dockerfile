# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set working directory
WORKDIR .

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Making main python file executable
RUN chmod +x generate_report.py

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the script
ENTRYPOINT ["python", "generate_report.py"]
CMD ["results.jtl", "output"]
