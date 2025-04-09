# GrafanaLLM-AlertAnalyzer

<p align="center">
  <strong>AI-Powered Alert Analysis System Using Grafana MCP and Large Language Models</strong>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#components">Components</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## Overview

GrafanaLLM-AlertAnalyzer is an intelligent platform that combines the power of Grafana's Machine Configuration Protocol (MCP) with Large Language Models (LLMs) to revolutionize system alert analysis. This tool automatically processes incoming alerts from Grafana, analyzes metrics data via MCP, and uses AI to generate comprehensive problem analyses with actionable solutions.

## Key Features

- **AI-Powered Analysis**: Leverages OpenAI's LLMs to interpret alert data and provide human-like reasoning about system issues
- **Grafana MCP Integration**: Directly accesses Grafana metrics and data sources through the Machine Configuration Protocol
- **Automated Root Cause Analysis**: Identifies underlying issues beyond surface-level symptoms
- **Intelligent Solution Recommendation**: Suggests specific technical actions based on AI analysis of metrics data
- **Email Notifications**: Sends detailed analysis reports via email with formatted problem, cause, and solution sections
- **Modular Architecture**: Easily extensible design for adding new features or supporting additional monitoring systems

## Installation

### Requirements

- Python 3.9+
- Docker (optional)
- Grafana instance with API key
- OpenAI API key

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-name/GrafanaLLM-AlertAnalyzer.git
cd GrafanaLLM-AlertAnalyzer

# Set up development environment
make setup

# Configure environment variables
cp .env.example .env
# Edit the .env file with your Grafana and OpenAI API keys

# Run the application
make run
```

### Docker Deployment

```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run
```

## Usage

### Configuring Grafana Webhook

1. Go to 'Alerting' > 'Contact points' in Grafana admin
2. Click 'Add contact point'
3. Select 'Webhook' type
4. Enter `http://your-host:8000/alert` in the URL field
5. Set HTTP method to 'POST'
6. Save

### API Endpoints

- `POST /alert` - Receive alert data from Grafana and trigger AI analysis
- `GET /health` - Check service status

### Email Notification Setup

Configure the following settings in your `.env` file to enable email notifications with the AI analysis results:

```
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-password
ALERT_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

## Components

GrafanaLLM-AlertAnalyzer consists of the following main components:

- **API Server**: FastAPI-based web server that receives webhook notifications from Grafana
- **LLM Agent**: LangChain-based ReAct agent that uses OpenAI models to analyze alerts
- **MCP Client**: Grafana MCP adapter that allows direct querying of Grafana data sources
- **Notification Service**: Email notification service that sends formatted analysis results

## Development Guide

### Project Structure

```
grafanallm-alertanalyzer/
│
├── app/                      # Application code
│   ├── api/                  # API endpoints
│   ├── core/                 # Core functionality and settings
│   ├── services/             # Business logic
│   │   ├── agent.py          # LLM agent implementation
│   │   ├── alert_analyzer.py # Alert analysis orchestration
│   │   └── notification.py   # Email notification service
│   └── utils/                # Utility functions
│
├── tests/                    # Test code
├── Dockerfile                # Docker image definition
├── Makefile                  # Build and development scripts
├── main.py                   # Application entry point
└── requirements.txt          # Dependency packages
```

### Development Commands

```bash
# Install dependencies and set up development environment
make setup

# Run tests
make test

# Check code with linters
make lint

# Format code
make format

# Run the application
make run
```

## How It Works

1. When a Grafana alert is triggered, it sends a webhook notification to the `/alert` endpoint
2. The application extracts alert information and launches the LLM-powered analysis
3. The LLM agent uses Grafana MCP to query relevant metrics and data sources
4. The agent analyzes the data, identifies the problem, determines the root cause, and suggests solutions
5. Results are formatted and sent via email to the configured recipients
6. The API returns the analysis results to the caller

## Contributing

GrafanaLLM-AlertAnalyzer is an open-source project, and contributions are welcome:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
