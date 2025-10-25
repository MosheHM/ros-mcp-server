# Startup Scripts

This directory contains convenience scripts for starting the ROS MCP Server in different environments.

## Scripts

### start-dev.sh
Starts the ROS MCP Server in development mode.

**Usage:**
```bash
./scripts/start-dev.sh
```

**Features:**
- Automatically loads `.env.development` configuration
- Sets `ENVIRONMENT=development`
- Displays current configuration
- Checks for required tools (uv)
- Starts server with appropriate transport

**Default Configuration:**
- Transport: stdio
- Host: 127.0.0.1
- Port: 9000
- Log Level: DEBUG
- Debug Mode: true

### start-prod.sh
Starts the ROS MCP Server in production mode.

**Usage:**
```bash
./scripts/start-prod.sh
```

**Features:**
- Automatically loads `.env.production` configuration
- Sets `ENVIRONMENT=production`
- Interactive deployment method selection:
  1. Docker Compose (recommended)
  2. Direct Python (not recommended)
- Validates configuration files
- Provides helpful commands and endpoints

**Default Configuration:**
- Transport: http
- Host: 0.0.0.0
- Port: 9000
- Log Level: INFO
- Debug Mode: false

## Prerequisites

### For Development
- Python 3.10+
- uv (Python package manager)
- Optional: Docker (for containerized development)

### For Production
- Docker and Docker Compose (recommended)
- Python 3.10+ and uv (for direct deployment)

## Installation

### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Docker
Follow the official Docker installation guide for your OS:
https://docs.docker.com/get-docker/

## Environment Files

Before running the scripts, ensure you have the appropriate environment file:

### Development
```bash
# Copy from example
cp .env.example .env.development

# Or edit existing
nano .env.development
```

### Production
```bash
# Copy from example
cp .env.example .env.production

# Edit for your production setup
nano .env.production
```

## Examples

### Development Workflow

```bash
# 1. Set up environment
cp .env.example .env.development

# 2. Start server
./scripts/start-dev.sh

# 3. The server is now running
# Configure your MCP client to connect
```

### Production Deployment

```bash
# 1. Set up environment
cp .env.example .env.production
nano .env.production  # Configure for production

# 2. Start production stack
./scripts/start-prod.sh
# Choose option 1 (Docker Compose)

# 3. Verify deployment
curl http://localhost/health

# 4. View logs
docker-compose -f docker-compose.production.yml logs -f

# 5. Stop when needed
docker-compose -f docker-compose.production.yml down
```

## Troubleshooting

### "uv not found"
Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

### ".env.production not found"
Create the file:
```bash
cp .env.example .env.production
nano .env.production
```

### "Permission denied"
Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### "Docker Compose not found"
Install Docker Compose:
```bash
# For Docker Compose v2 (recommended)
docker compose version

# Or install standalone
sudo apt-get install docker-compose
```

### Port Already in Use
Check what's using the port:
```bash
# For port 9000
sudo netstat -tulpn | grep 9000

# Or
sudo lsof -i :9000
```

Stop the conflicting service or change the port in your .env file.

## Advanced Usage

### Custom Environment File

Use a custom environment file:
```bash
# Export variables manually
export ENVIRONMENT=development
export MCP_TRANSPORT=http
export MCP_PORT=8080

# Then run
uv run server.py --transport http --port 8080
```

### Running Without Scripts

Development:
```bash
export ENVIRONMENT=development
source .env.development
uv run server.py
```

Production:
```bash
export ENVIRONMENT=production
source .env.production
docker-compose -f docker-compose.production.yml up -d
```

### Debugging

Enable verbose logging:
```bash
# Edit .env file
LOG_LEVEL=DEBUG
DEBUG=true

# Restart service
./scripts/start-dev.sh
```

## Script Modification

Feel free to customize these scripts for your needs:

- Add pre-flight checks
- Integrate with your CI/CD
- Add custom environment variables
- Extend logging or monitoring

## Related Documentation

- [Deployment Guide](../docs/deployment.md) - Complete deployment instructions
- [Quick Start Guide](../docs/quickstart.md) - Getting started quickly
- [Main README](../README.md) - Project overview

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Deployment Guide](../docs/deployment.md)
3. Check existing GitHub issues
4. Open a new issue with details about your setup
