# Use an official Python runtime as a parent image
FROM python:3.5-slim

arg path

#https://stackoverflow.com/questions/27273412/cannot-install-packages-inside-docker-ubuntu-image

# Set the working directory to /app
WORKDIR ${path}

# Copy the current directory contents into the container at /app
ADD . ${path}

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
#EXPOSE 80

# Define environment variable
#ENV NAME World

# Run bash when the container launches
CMD ["bash"]

