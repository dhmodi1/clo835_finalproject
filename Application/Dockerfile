FROM ubuntu:20.04

# Update package list and install necessary dependencies
RUN apt-get update -y


# Copy the application files to the container
COPY . /app
WORKDIR /app

# Install dependencies
RUN set -xe \
    && apt-get update -y \
    && apt-get install -y python3-pip \
    && apt-get install -y mysql-client

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the .env file into the container
COPY .env /app/.env

# Expose port 81 for the Flask app
EXPOSE 81

# Set the entry point and default command to run the app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]

