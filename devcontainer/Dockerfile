# devcontainer/Dockerfile
FROM python:3.10-slim-bullseye

# Install Java (needed for PySpark)
RUN apt-get update && apt-get install -y openjdk-11-jdk curl && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Default workdir
WORKDIR /workspace
