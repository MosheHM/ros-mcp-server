# Quick Start Guide - Environment Setup

This guide will help you quickly set up the ROS MCP Server for development or production.

## Prerequisites

- Docker and Docker Compose (for production)
- Python 3.10+ and uv (for development)
- ROS/ROS2 with rosbridge running on your robot

## Development Setup (5 minutes)

### Option 1: Quick Start Script

```bash
# Run the development startup script
./scripts/start-dev.sh
```

### Option 2: Manual Setup

```bash
# 1. Copy environment file
cp .env.example .env.development

# 2. (Optional) Edit .env.development for your setup
nano .env.development

# 3. Set environment and run
export ENVIRONMENT=development
uv run server.py
```

### Verify Development Setup

```bash
# The server should be running in stdio mode
# Configure your MCP client (Claude Desktop, etc.) to connect
```

## Production Setup (10 minutes)

### Option 1: Quick Start Script

```bash
# Run the production startup script
./scripts/start-prod.sh
# Choose option 1 (Docker Compose)
```

### Option 2: Manual Docker Deployment

```bash
# 1. Copy and configure production environment
cp .env.example .env.production
nano .env.production  # Edit as needed

# 2. Start with Docker Compose
docker-compose -f docker-compose.production.yml up -d --build

# 3. Verify services are running
docker-compose -f docker-compose.production.yml ps

# 4. Test the gateway
curl http://localhost/health
```

### Verify Production Setup

```bash
# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Test health endpoint
curl http://localhost/health

# Test MCP endpoint (should get response or auth challenge)
curl http://localhost/mcp
```

## Environment Comparison

| Feature | Development | Production |
|---------|-------------|------------|
| Transport | stdio | http |
| Host | 127.0.0.1 | 0.0.0.0 |
| Gateway | None | Nginx |
| SSL/TLS | No | Optional |
| Rate Limiting | No | Yes |
| Debug Logging | Yes | No |
| Auto-reload | Yes | No |

## Next Steps

### Development
- Configure your MCP client (see [installation.md](../docs/installation.md))
- Start rosbridge on your robot
- Test with example commands

### Production
- Enable HTTPS (see [deployment.md](../docs/deployment.md))
- Configure firewall rules
- Set up monitoring
- Review security settings

## Troubleshooting

### Common Issues

**Cannot connect to ROS Bridge**
```bash
# Check ROSBRIDGE_IP and ROSBRIDGE_PORT in your .env file
# Test connectivity
ping <ROSBRIDGE_IP>
nc -zv <ROSBRIDGE_IP> <ROSBRIDGE_PORT>
```

**Docker services won't start**
```bash
# Check Docker is running
docker ps

# Check for port conflicts
netstat -tulpn | grep :80
netstat -tulpn | grep :9000

# View detailed logs
docker-compose -f docker-compose.production.yml logs
```

**Permission denied on scripts**
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

## Configuration Files Reference

```
ros-mcp-server/
├── .env.example              # Template configuration
├── .env.development          # Development settings
├── .env.production           # Production settings
├── docker-compose.development.yml
├── docker-compose.production.yml
├── Dockerfile                # Production container
├── nginx/
│   ├── nginx.conf           # HTTP gateway config
│   └── nginx-ssl.conf       # HTTPS gateway config
└── scripts/
    ├── start-dev.sh         # Development startup
    └── start-prod.sh        # Production startup
```

## Getting Help

- Read the full [Deployment Guide](../docs/deployment.md)
- Check [Nginx Configuration](../nginx/README.md)
- Review [Main README](../README.md)
- Open an issue on GitHub

## Tips

### Development Tips
- Use `LOG_LEVEL=DEBUG` for detailed logging
- Mount volumes in docker-compose for live code updates
- Use stdio transport for direct MCP client integration

### Production Tips
- Always use Docker Compose for production
- Enable HTTPS with valid certificates
- Set up log rotation for nginx logs
- Monitor resource usage regularly
- Keep Docker images updated

## Command Cheatsheet

### Development
```bash
# Start dev server
./scripts/start-dev.sh

# Or manually
export ENVIRONMENT=development
uv run server.py
```

### Production
```bash
# Start production (Docker)
docker-compose -f docker-compose.production.yml up -d

# Stop production
docker-compose -f docker-compose.production.yml down

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart services
docker-compose -f docker-compose.production.yml restart

# Update and rebuild
docker-compose -f docker-compose.production.yml up -d --build
```

### Monitoring
```bash
# Check service health
curl http://localhost/health

# Monitor nginx access logs
docker-compose -f docker-compose.production.yml logs -f nginx

# Monitor MCP server logs
docker-compose -f docker-compose.production.yml logs -f ros-mcp-server

# Check resource usage
docker stats
```
