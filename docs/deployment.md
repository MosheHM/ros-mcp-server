# Environment Setup and Deployment Guide

This guide explains how to set up and deploy the ROS MCP Server in different environments (development and production) with nginx as a gateway server.

## Table of Contents

- [Overview](#overview)
- [Environment Configuration](#environment-configuration)
- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Nginx Gateway](#nginx-gateway)
- [Docker Deployment](#docker-deployment)
- [Security Considerations](#security-considerations)

## Overview

The ROS MCP Server supports two main environments:

- **Development**: Optimized for local development with debug logging and stdio transport
- **Production**: Optimized for production deployment with HTTP transport, nginx gateway, and enhanced security

## Environment Configuration

The server uses environment-specific configuration files to manage settings:

### Configuration Files

- `.env.development` - Development environment settings
- `.env.production` - Production environment settings
- `.env.example` - Example configuration template

### Environment Variables

Key environment variables:

| Variable | Description | Development Default | Production Default |
|----------|-------------|---------------------|-------------------|
| `ENVIRONMENT` | Environment type | development | production |
| `MCP_TRANSPORT` | MCP transport protocol | stdio | http |
| `MCP_HOST` | MCP server host | 127.0.0.1 | 0.0.0.0 |
| `MCP_PORT` | MCP server port | 9000 | 9000 |
| `ROSBRIDGE_IP` | ROS bridge IP address | 127.0.0.1 | 127.0.0.1 |
| `ROSBRIDGE_PORT` | ROS bridge port | 9090 | 9090 |
| `LOG_LEVEL` | Logging level | DEBUG | INFO |
| `DEBUG` | Debug mode | true | false |

## Development Environment

### Local Setup

1. **Copy the development environment file**:
   ```bash
   cp .env.example .env.development
   ```

2. **Edit `.env.development`** to match your local setup:
   ```bash
   ENVIRONMENT=development
   MCP_TRANSPORT=stdio
   ROSBRIDGE_IP=127.0.0.1
   LOG_LEVEL=DEBUG
   DEBUG=true
   ```

3. **Run the server**:
   ```bash
   # Using uv
   ENVIRONMENT=development uv run server.py

   # Or with Python directly
   ENVIRONMENT=development python server.py
   ```

### Docker Development

Run the development container with live code reloading:

```bash
docker-compose -f docker-compose.development.yml up
```

This mounts your source code into the container for live development.

## Production Environment

### Production Setup

1. **Copy the production environment file**:
   ```bash
   cp .env.example .env.production
   ```

2. **Edit `.env.production`** for your production setup:
   ```bash
   ENVIRONMENT=production
   MCP_TRANSPORT=http
   MCP_HOST=0.0.0.0
   MCP_PORT=9000
   LOG_LEVEL=INFO
   DEBUG=false
   ```

3. **Deploy with Docker Compose** (recommended):
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

### Production Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼──────────────┐
│  Nginx Gateway      │
│  (Port 80/443)      │
│  - Load Balancing   │
│  - SSL/TLS          │
│  - Rate Limiting    │
│  - Security Headers │
└──────┬──────────────┘
       │
       │ HTTP
       │
┌──────▼──────────────┐
│  ROS MCP Server     │
│  (Port 9000)        │
│  - MCP Protocol     │
│  - ROS Bridge       │
└─────────────────────┘
```

## Nginx Gateway

The nginx gateway provides:

- **Reverse Proxy**: Routes traffic to the MCP server
- **Load Balancing**: Distributes requests (can be configured for multiple backends)
- **Rate Limiting**: Protects against abuse (10 req/s with burst of 20)
- **Security Headers**: XSS protection, frame options, etc.
- **SSL/TLS Termination**: HTTPS support (optional)
- **Health Checks**: `/health` endpoint for monitoring

### Nginx Configuration

Two configurations are provided:

1. **nginx.conf** - HTTP only (default)
2. **nginx-ssl.conf** - HTTPS with SSL/TLS

### Using HTTP (Default)

```bash
docker-compose -f docker-compose.production.yml up -d
```

Access the server at: `http://localhost/mcp`

### Enabling HTTPS

1. **Generate SSL certificates**:
   ```bash
   mkdir -p nginx/ssl
   
   # Self-signed certificate (for testing)
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/key.pem \
     -out nginx/ssl/cert.pem
   
   # Or use Let's Encrypt for production
   ```

2. **Update docker-compose.production.yml**:
   Uncomment the SSL volume and port 443 mapping:
   ```yaml
   nginx:
     ports:
       - "80:80"
       - "443:443"  # Uncomment this
     volumes:
       - ./nginx/nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro  # Change to nginx-ssl.conf
       - ./nginx/ssl:/etc/nginx/ssl:ro  # Uncomment this
   ```

3. **Restart the services**:
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

Access the server at: `https://localhost/mcp`

## Docker Deployment

### Development Deployment

```bash
# Start development environment
docker-compose -f docker-compose.development.yml up

# Stop development environment
docker-compose -f docker-compose.development.yml down
```

### Production Deployment

```bash
# Build and start production environment
docker-compose -f docker-compose.production.yml up -d --build

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Stop production environment
docker-compose -f docker-compose.production.yml down

# Stop and remove volumes
docker-compose -f docker-compose.production.yml down -v
```

### Health Checks

Both the MCP server and nginx have health checks:

```bash
# Check MCP server health (direct)
curl http://localhost:9000/health

# Check through nginx gateway
curl http://localhost/health
```

### Monitoring

View nginx logs:

```bash
# Access logs
docker-compose -f docker-compose.production.yml exec nginx tail -f /var/log/nginx/ros-mcp-access.log

# Error logs
docker-compose -f docker-compose.production.yml exec nginx tail -f /var/log/nginx/ros-mcp-error.log
```

## Security Considerations

### Production Security Checklist

- [ ] Use HTTPS with valid SSL certificates
- [ ] Configure rate limiting appropriate for your use case
- [ ] Set strong firewall rules
- [ ] Use environment variables for sensitive configuration
- [ ] Regularly update Docker images
- [ ] Monitor logs for suspicious activity
- [ ] Implement authentication (future feature)
- [ ] Use network isolation in Docker
- [ ] Limit container resources (CPU, memory)

### Rate Limiting

The nginx configuration includes rate limiting:

- **Rate**: 10 requests per second
- **Burst**: 20 requests
- **Zone**: `mcp_limit` (10MB memory)

Adjust in `nginx/nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=10r/s;

location /mcp {
    limit_req zone=mcp_limit burst=20 nodelay;
    # ...
}
```

### Security Headers

The following security headers are automatically added:

- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)

### Network Security

In production, the MCP server is not exposed directly to the host. Only nginx is accessible:

```yaml
ros-mcp-server:
  expose:
    - "9000"  # Only exposed to Docker network, not host

nginx:
  ports:
    - "80:80"  # Exposed to host
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if containers are running: `docker-compose ps`
   - Verify environment variables are set correctly
   - Check logs: `docker-compose logs`

2. **Rate Limiting Errors**
   - Adjust rate limit in nginx.conf
   - Check nginx logs for rate limit messages

3. **SSL Certificate Issues**
   - Verify certificate files exist in `nginx/ssl/`
   - Check certificate validity: `openssl x509 -in nginx/ssl/cert.pem -text`
   - Ensure volume mounts are correct

4. **ROS Bridge Connection Issues**
   - Verify `ROSBRIDGE_IP` and `ROSBRIDGE_PORT` are correct
   - Ensure rosbridge is running on the target robot
   - Check network connectivity: `docker-compose exec ros-mcp-server ping <ROSBRIDGE_IP>`

### Debug Mode

Enable debug mode in production (temporary):

```bash
# Edit .env.production
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
docker-compose -f docker-compose.production.yml restart
```

## Additional Resources

- [Main README](../README.md)
- [Installation Guide](installation.md)
- [Contributing Guidelines](contributing.md)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
