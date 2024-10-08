# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /chat_authenticator

# Copy the current directory contents into the container at /app
COPY . /chat/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run manage.py runserver when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
