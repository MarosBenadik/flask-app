# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN ls -la \
  && pip install -r flask-source/requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000
EXPOSE 8000

# Define environment variable
ENV NAME=World

# Run app.py when the container launches
CMD ["python", "flask-source/app.py"]
