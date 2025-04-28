# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make sure mcp-grafana is executable
RUN chmod +x /app/mcp-grafana
RUN chmod +x /app/github-mcp-server

# Add mcp-grafana to PATH
ENV PATH="/app:${PATH}"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]