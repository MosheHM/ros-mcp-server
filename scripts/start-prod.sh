#!/bin/bash
# ROS MCP Server - Production Environment Startup Script

set -e

echo "======================================"
echo "ROS MCP Server - Production Mode"
echo "======================================"
echo ""

# Set environment
export ENVIRONMENT=production

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "Error: .env.production not found."
    echo "Please create it from .env.example and configure for production."
    exit 1
fi

# Load environment variables
echo "Loading configuration from .env.production"
export $(grep -v '^#' .env.production | xargs)

echo ""
echo "Configuration:"
echo "  Environment: ${ENVIRONMENT}"
echo "  MCP Transport: ${MCP_TRANSPORT}"
echo "  MCP Host: ${MCP_HOST}"
echo "  MCP Port: ${MCP_PORT}"
echo "  ROS Bridge IP: ${ROSBRIDGE_IP}"
echo "  ROS Bridge Port: ${ROSBRIDGE_PORT}"
echo "  Log Level: ${LOG_LEVEL}"
echo "  Debug Mode: ${DEBUG}"
echo ""

# Deployment method
echo "Choose deployment method:"
echo "  1) Docker Compose (recommended)"
echo "  2) Direct Python (not recommended for production)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Starting with Docker Compose..."
        
        # Check if docker-compose is available
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="docker-compose"
        elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
            COMPOSE_CMD="docker compose"
        else
            echo "Error: Docker Compose not found."
            exit 1
        fi
        
        echo "Building and starting containers..."
        $COMPOSE_CMD -f docker-compose.production.yml up -d --build
        
        echo ""
        echo "Services started successfully!"
        echo ""
        echo "Access the server at:"
        echo "  http://localhost/mcp"
        echo ""
        echo "Check status:"
        echo "  $COMPOSE_CMD -f docker-compose.production.yml ps"
        echo ""
        echo "View logs:"
        echo "  $COMPOSE_CMD -f docker-compose.production.yml logs -f"
        echo ""
        echo "Stop services:"
        echo "  $COMPOSE_CMD -f docker-compose.production.yml down"
        ;;
        
    2)
        echo ""
        echo "Warning: Direct Python deployment is not recommended for production."
        echo "Consider using Docker Compose for better isolation and security."
        echo ""
        read -p "Continue anyway? [y/N]: " confirm
        
        if [[ $confirm != [yY] ]]; then
            echo "Aborted."
            exit 0
        fi
        
        # Check for uv
        if ! command -v uv &> /dev/null; then
            echo "Error: uv not found. Please install it first:"
            echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
            exit 1
        fi
        
        echo "Starting ROS MCP Server..."
        uv run server.py --transport "${MCP_TRANSPORT}" --host "${MCP_HOST}" --port "${MCP_PORT}"
        ;;
        
    *)
        echo "Invalid choice. Aborted."
        exit 1
        ;;
esac
