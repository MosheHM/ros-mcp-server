# Native ROS 2 Usage Guide

This guide explains how to use the native ROS 2 mode for improved performance.

## Overview

As of version 3.0, the ROS MCP Server supports native ROS 2 APIs for introspection operations, providing:

- **5-10x faster** topic, service, and node queries
- **Direct DDS discovery** (no WebSocket overhead)
- **Automatic fallback** to rosbridge for compatibility
- **Hybrid approach** - native introspection + rosbridge pub/sub

## Quick Start

### Prerequisites

- ROS 2 Humble, Iron, or newer
- Python 3.10+
- The ros-mcp-server installed

### Installation

1. **Install ROS 2** (if not already installed):
   ```bash
   # Ubuntu 22.04 - ROS 2 Humble
   sudo apt update
   sudo apt install ros-humble-ros-base
   sudo apt install ros-humble-rclpy
   ```

2. **Source ROS 2**:
   ```bash
   source /opt/ros/humble/setup.bash
   # Add to your ~/.bashrc for persistence
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   ```

3. **Install the MCP server**:
   ```bash
   git clone https://github.com/robotmcp/ros-mcp-server.git
   cd ros-mcp-server
   pip install -e .
   ```

That's it! The server will automatically detect ROS 2 and use native APIs.

## How It Works

The server uses a **hybrid approach**:

### Introspection Operations (Native ROS 2)

These operations use native `rclpy` APIs when ROS 2 is available:

- `get_topics()` - List all topics
- `get_topic_type()` - Get message type for a topic
- `get_publishers_for_topic()` - List publishers
- `get_subscribers_for_topic()` - List subscribers
- `get_message_details()` - Message structure introspection
- `get_services()` - List all services
- `get_service_type()` - Get service type
- `get_service_details()` - Service request/response introspection
- `get_nodes()` - List all nodes
- `get_node_details()` - Node publishers/subscribers/services
- `inspect_all_topics()` - **Much faster!**
- `inspect_all_services()` - **Much faster!**
- `inspect_all_nodes()` - **Much faster!**

### Pub/Sub Operations (Rosbridge)

These operations still use rosbridge for maximum compatibility:

- `subscribe_once()` - Subscribe to a topic
- `subscribe_for_duration()` - Subscribe for a duration
- `publish_once()` - Publish a message
- `publish_for_durations()` - Publish multiple messages
- `call_service()` - Call a ROS service

This allows the server to work across networks and with robots that don't have ROS 2 installed locally.

## Performance Comparison

| Operation | Rosbridge | Native ROS 2 | Improvement |
|-----------|-----------|--------------|-------------|
| `get_topics()` | 50-100ms | 5-10ms | **5-10x** |
| `get_topic_type()` | 50-100ms | 5-10ms | **5-10x** |
| `get_message_details()` | 100-200ms | 20-30ms | **5-7x** |
| `inspect_all_topics()` (100 topics) | 5-10s | 500ms-1s | **10x** |
| `inspect_all_nodes()` (50 nodes) | 3-5s | 300-500ms | **10x** |

## Deployment Scenarios

### Scenario 1: MCP Server on Same Machine as Robot

**Best Option**: Native ROS 2 Mode
```
Robot (ROS 2) ← same machine → MCP Server (ROS 2 + rosbridge for pub/sub)
                               ↓
                            LLM Client
```

**Benefits**:
- Fastest introspection
- No network latency
- Still supports pub/sub via rosbridge

### Scenario 2: MCP Server on Remote Machine

**Option A**: Native ROS 2 Mode (if same ROS domain)
```
Robot (ROS 2) ←─ DDS network ─→ MCP Server (ROS 2)
                                ↓
                             LLM Client
```

**Requirements**:
- Same `ROS_DOMAIN_ID`
- Network configured for DDS multicast
- Firewall allows DDS ports

**Option B**: Rosbridge Mode (works anywhere)
```
Robot (ROS 2 + rosbridge) ←─ WebSocket ─→ MCP Server
                                           ↓
                                        LLM Client
```

**Benefits**:
- Works across any network
- No special network configuration
- Compatible with ROS 1

### Scenario 3: ROS 1 Robot

**Only Option**: Rosbridge Mode
```
Robot (ROS 1 + rosbridge) ←─ WebSocket ─→ MCP Server
                                           ↓
                                        LLM Client
```

## Configuration

The server automatically detects ROS 2. You can verify which mode is active:

```python
# This will show ROS 2 version if native mode is active
detect_ros_version()
# Returns: {'version': '2', 'distro': 'humble'}
```

No configuration changes are needed - the server automatically:
1. Tries native ROS 2 APIs first
2. Falls back to rosbridge if ROS 2 is unavailable
3. Uses rosbridge for pub/sub operations

## Troubleshooting

### "ROS 2 not detected"

**Cause**: ROS 2 not sourced or not installed

**Solution**:
```bash
# Make sure ROS 2 is sourced
source /opt/ros/humble/setup.bash

# Verify it's available
echo $ROS_DISTRO
# Should output: humble (or your distro)
```

### "Performance not improved"

**Possible causes**:
1. ROS 2 not installed on MCP server machine
2. Server falling back to rosbridge
3. Network latency to robot

**Check**:
```python
# Run detect_ros_version()
# If it shows version: "2", native mode is working
# If it shows version: "1" or takes long, it's using rosbridge
```

### "Topics not showing up"

**Cause**: Different ROS domain or network configuration

**Solution**:
```bash
# Ensure same domain ID on both machines
export ROS_DOMAIN_ID=0

# Check DDS discovery
ros2 topic list
# Should show topics from robot
```

## Migration from Rosbridge-Only

If you're upgrading from an older version that only used rosbridge:

**Good news**: No changes needed!
- All existing code continues to work
- Native mode is automatically enabled when ROS 2 is detected
- Rosbridge fallback ensures compatibility

**Optional optimizations**:
- Install ROS 2 on MCP server machine for better performance
- No code changes required in your application

## FAQ

### Q: Do I still need rosbridge?

**A**: Yes, for pub/sub operations and ROS 1 support. The native mode only replaces introspection operations.

### Q: Will this work with my ROS 1 robot?

**A**: Yes! The server automatically falls back to rosbridge for ROS 1, maintaining full compatibility.

### Q: Can I force using only rosbridge?

**A**: Yes, simply don't install ROS 2 on the MCP server machine. The server will automatically use rosbridge for everything.

### Q: What about parameters?

**A**: Parameter operations currently use rosbridge for both ROS 1 and ROS 2. Native parameter support may be added in the future.

### Q: Does this work with Docker?

**A**: Yes! Make sure to:
1. Install ROS 2 in the Docker image
2. Source ROS 2 in the container startup
3. Configure DDS networking if needed

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/robotmcp/ros-mcp-server/issues)
- See the [migration guide](native_ros2_migration.md) for technical details
- Check the [installation guide](installation.md) for setup help
