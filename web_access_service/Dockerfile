# Use the official Python image.
FROM python:3.12

# Set the working directory in the container.
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Flask and requests
RUN pip install Flask requests

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD [ "python", "app.py" ]