# Use an official Python runtime as a parent image
FROM python:3.13-slim

RUN apt-get update && apt-get install -y build-essential
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py"]
