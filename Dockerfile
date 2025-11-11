# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the local requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install flask and tmux
RUN pip install flask
RUN apt-get update && apt-get install -y tmux

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 8888

# Set Flask environment variable and run the application
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=8888"]