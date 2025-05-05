FROM python:3.11

# Install socat
RUN apt-get update && apt-get install -y socat

# Set up your application directory
WORKDIR /app

# Copy your code into the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Run socat to create virtual ports and start pytest
CMD socat -d -d pty,raw,echo=0,link=/app/writer pty,raw,echo=0,link=/app/reader & sleep 1 && pytest tests/serial/test_serial.py
