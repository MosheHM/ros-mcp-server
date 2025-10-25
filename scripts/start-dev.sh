#!/bin/bash
# ROS MCP Server - Development Environment Startup Script

set -e

echo "======================================"
echo "ROS MCP Server - Development Mode"
echo "======================================"
echo ""

# Set environment
export ENVIRONMENT=development

# Check if .env.development exists
if [ ! -f .env.development ]; then
    echo "Warning: .env.development not found. Using defaults."
    echo "Creating from .env.example..."
    cp .env.example .env.development
fi

# Load environment variables
if [ -f .env.development ]; then
    echo "Loading configuration from .env.development"
    export $(grep -v '^#' .env.development | xargs)
fi

echo ""
echo "Configuration:"
echo "  Environment: ${ENVIRONMENT}"
echo "  MCP Transport: ${MCP_TRANSPORT:-stdio}"
echo "  MCP Host: ${MCP_HOST:-127.0.0.1}"
echo "  MCP Port: ${MCP_PORT:-9000}"
echo "  ROS Bridge IP: ${ROSBRIDGE_IP:-127.0.0.1}"
echo "  ROS Bridge Port: ${ROSBRIDGE_PORT:-9090}"
echo "  Log Level: ${LOG_LEVEL:-DEBUG}"
echo "  Debug Mode: ${DEBUG:-true}"
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Starting ROS MCP Server in development mode..."
echo ""

# Start the server
if [ "${MCP_TRANSPORT}" = "stdio" ]; then
    uv run server.py
else
    uv run server.py --transport "${MCP_TRANSPORT}" --host "${MCP_HOST}" --port "${MCP_PORT}"
fi
