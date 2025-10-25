# Nginx Gateway Configuration

This directory contains nginx configuration files for the ROS MCP Server production gateway.

## Files

- **nginx.conf** - HTTP configuration (default)
- **nginx-ssl.conf** - HTTPS configuration with SSL/TLS
- **ssl/** - Directory for SSL certificates (create this for HTTPS)

## HTTP Configuration (Default)

The default `nginx.conf` provides:

- Reverse proxy to ROS MCP Server
- Rate limiting (10 req/s with burst of 20)
- Security headers
- Health check endpoint
- Request/error logging

### Usage

This configuration is used automatically when running:

```bash
docker-compose -f docker-compose.production.yml up -d
```

Access: `http://localhost/mcp`

## HTTPS Configuration

The `nginx-ssl.conf` adds:

- SSL/TLS termination
- HTTP to HTTPS redirect
- TLS 1.2 and 1.3 support
- Enhanced security headers (HSTS)

### Setup HTTPS

1. **Generate SSL certificates**:

   For testing (self-signed):
   ```bash
   mkdir -p ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem \
     -out ssl/cert.pem
   ```

   For production (Let's Encrypt):
   ```bash
   # Use certbot or your preferred ACME client
   certbot certonly --standalone -d your-domain.com
   
   # Copy certificates
   mkdir -p ssl
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
   ```

2. **Update docker-compose.production.yml**:

   Change the nginx volume to use `nginx-ssl.conf`:
   ```yaml
   nginx:
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - ./nginx/nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
       - ./nginx/ssl:/etc/nginx/ssl:ro
   ```

3. **Restart services**:
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

Access: `https://localhost/mcp`

## Configuration Options

### Rate Limiting

Adjust in both configuration files:

```nginx
limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=10r/s;

location /mcp {
    limit_req zone=mcp_limit burst=20 nodelay;
}
```

Parameters:
- `rate`: Requests per second (e.g., `10r/s`)
- `burst`: Maximum burst size (e.g., `20`)
- `nodelay`: Process burst requests immediately

### Timeouts

Adjust proxy timeouts:

```nginx
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

### Client Body Size

For larger payloads:

```nginx
client_max_body_size 10M;  # Increase as needed
```

### Security Headers

Customize security headers:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Endpoints

### `/mcp`

Main MCP server endpoint with:
- Rate limiting
- Proxy to backend
- WebSocket support
- No buffering (streaming)

### `/health`

Health check endpoint:
- Returns 200 OK with "healthy"
- No logging
- For monitoring/load balancers

### `/` (Root)

Simple status page:
- Returns server identification
- Useful for basic connectivity checks

## Monitoring

### Access Logs

View access logs:
```bash
docker-compose -f docker-compose.production.yml logs nginx
# or
docker exec ros-mcp-gateway tail -f /var/log/nginx/ros-mcp-access.log
```

### Error Logs

View error logs:
```bash
docker exec ros-mcp-gateway tail -f /var/log/nginx/ros-mcp-error.log
```

### Log Format

Default combined log format includes:
- Client IP
- Request timestamp
- HTTP method and path
- Status code
- Response size
- User agent
- Response time

## Troubleshooting

### Connection Issues

Test nginx directly:
```bash
curl -v http://localhost/health
```

Test backend connection:
```bash
docker-compose exec nginx curl -v http://ros-mcp-server:9000/health
```

### SSL Certificate Issues

Verify certificate:
```bash
openssl x509 -in ssl/cert.pem -text -noout
```

Test SSL connection:
```bash
openssl s_client -connect localhost:443
```

### Rate Limit Testing

Test rate limits:
```bash
# Send multiple requests quickly
for i in {1..30}; do curl http://localhost/mcp; done
```

### Configuration Validation

Validate nginx configuration:
```bash
docker-compose exec nginx nginx -t
```

Reload nginx configuration:
```bash
docker-compose exec nginx nginx -s reload
```

## Advanced Configuration

### Load Balancing

Add multiple backend servers:

```nginx
upstream ros_mcp_backend {
    server ros-mcp-server-1:9000;
    server ros-mcp-server-2:9000;
    server ros-mcp-server-3:9000;
    
    # Load balancing method
    # least_conn;  # Least connections
    # ip_hash;     # IP hash for session persistence
}
```

### IP Whitelisting

Restrict access by IP:

```nginx
location /mcp {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    # ... rest of configuration
}
```

### Custom Headers

Add custom headers:

```nginx
location /mcp {
    add_header X-Server-Name "ROS-MCP-Gateway" always;
    add_header X-Request-ID $request_id always;
    
    # ... rest of configuration
}
```

## References

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Rate Limiting](https://www.nginx.com/blog/rate-limiting-nginx/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Let's Encrypt](https://letsencrypt.org/)
