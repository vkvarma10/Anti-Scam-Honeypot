# Use Python 3.9
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create the SQLite DB (if included) or ensure writable directory
# For HF Spaces, we can't persist SQLite easily without a dataset, 
# but for a demo, this is fine.
RUN chmod -R 777 .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
