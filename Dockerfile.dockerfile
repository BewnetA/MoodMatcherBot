# Start with an official Python image
FROM python:3.9-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy your project files
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Command to run your bot (change according to how your app is structured)
CMD ["python", "MoodMatcherBot.py"]
