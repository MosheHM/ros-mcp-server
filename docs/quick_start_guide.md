# Quick Start Guide: Implementing Native ROS 2 APIs

This is a condensed guide for developers who want to start implementing the native ROS 2 migration immediately.

## TL;DR

Replace rosapi WebSocket calls with native rclpy APIs. Full docs in `docs/native_ros2_migration.md`.

---

## Step 1: Setup (30 minutes)

### Install ROS 2
```bash
# Ubuntu 22.04 - ROS 2 Humble
sudo apt update
sudo apt install ros-humble-ros-base
sudo apt install ros-humble-rclpy
sudo apt install ros-humble-rosidl-runtime-py

# Source ROS 2
source /opt/ros/humble/setup.bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### Update Dependencies
Edit `pyproject.toml`:
```toml
dependencies = [
    # ... existing ...
    "rclpy>=3.0.0",
    "rosidl-runtime-py>=0.11.0",
]
```

Install:
```bash
uv sync
```

---

## Step 2: Test Prototype (15 minutes)

The prototype `utils/ros2_manager.py` is ready to test:

```bash
# Terminal 1: Start ROS 2 node
ros2 run turtlesim turtlesim_node

# Terminal 2: Test ROS2Manager
python3 << 'EOF'
import rclpy
from utils.ros2_manager import ROS2Manager

rclpy.init()
manager = ROS2Manager()
manager.initialize()

# Test topic introspection
print("Topics:", manager.get_topics())
print("Topic type:", manager.get_topic_type("/turtle1/cmd_vel"))
print("Nodes:", manager.get_nodes())

manager.shutdown()
rclpy.shutdown()
EOF
```

---

## Step 3: Update server.py (example)

### Before (using rosapi):
```python
@mcp.tool(description="Fetch available topics")
def get_topics() -> dict:
    message = {
        "op": "call_service",
        "service": "/rosapi/topics",
        "type": "rosapi/Topics",
        "id": "get_topics_request_1",
    }
    with ws_manager:
        response = ws_manager.request(message)
    if response and "values" in response:
        return response["values"]
    return {"warning": "No topics found"}
```

### After (using native ROS 2):
```python
@mcp.tool(description="Fetch available topics")
def get_topics() -> dict:
    try:
        return ros2_manager.get_topics()
    except Exception as e:
        return {"error": f"Failed to get topics: {e}"}
```

---

## Step 4: Initialize ROS2Manager

At the top of `server.py`, add:

```python
from utils.ros2_manager import ROS2Manager
import rclpy

# Initialize ROS 2
rclpy.init()

# Create manager
ros2_manager = ROS2Manager()
ros2_manager.initialize()

# ... rest of server code ...

# Clean shutdown (add at end of main())
def cleanup():
    ros2_manager.shutdown()
    rclpy.shutdown()

import atexit
atexit.register(cleanup)
```

---

## API Mapping Cheat Sheet

| rosapi Service | ROS2Manager Method | Native ROS 2 API |
|----------------|-------------------|------------------|
| `/rosapi/topics` | `get_topics()` | `node.get_topic_names_and_types()` |
| `/rosapi/topic_type` | `get_topic_type(topic)` | `node.get_topic_names_and_types()` (filter) |
| `/rosapi/publishers` | `get_publishers_for_topic(topic)` | `node.get_publishers_info_by_topic(topic)` |
| `/rosapi/subscribers` | `get_subscribers_for_topic(topic)` | `node.get_subscriptions_info_by_topic(topic)` |
| `/rosapi/services` | `get_services()` | `node.get_service_names_and_types()` |
| `/rosapi/service_type` | `get_service_type(service)` | `node.get_service_names_and_types()` (filter) |
| `/rosapi/nodes` | `get_nodes()` | `node.get_node_names()` |
| `/rosapi/node_details` | `get_node_details(node)` | Aggregate multiple calls |
| `/rosapi/message_details` | `get_message_details(type)` | `rosidl_runtime_py.utilities.get_message()` |
| `/rosapi/service_*_details` | `get_service_details(type)` | `rosidl_runtime_py.utilities.get_service()` |

---

## Common Patterns

### Pattern 1: Simple API replacement
```python
# Before
message = {"op": "call_service", "service": "/rosapi/nodes", ...}
response = ws_manager.request(message)
nodes = response["values"]["nodes"]

# After
nodes = ros2_manager.get_nodes()
```

### Pattern 2: With error handling
```python
# Before
with ws_manager:
    response = ws_manager.request(message)
    if response and "values" in response:
        return response["values"]
    return {"error": "Failed"}

# After
try:
    return ros2_manager.get_topics()
except Exception as e:
    return {"error": f"Failed: {e}"}
```

### Pattern 3: Topic details aggregation
```python
# Before (single rosapi call)
message = {
    "op": "call_service",
    "service": "/rosapi/node_details",
    "args": {"node": node_name},
    ...
}
response = ws_manager.request(message)

# After (multiple native calls aggregated in ROS2Manager)
details = ros2_manager.get_node_details(node_name)
# Returns same structure but built from multiple ROS 2 API calls
```

---

## Testing

### Test each function individually:

```python
# test_ros2_manager.py
import rclpy
from utils.ros2_manager import ROS2Manager

def test_get_topics():
    rclpy.init()
    manager = ROS2Manager()
    manager.initialize()
    
    result = manager.get_topics()
    assert "topics" in result
    assert "types" in result
    assert isinstance(result["topics"], list)
    
    manager.shutdown()
    rclpy.shutdown()

if __name__ == "__main__":
    test_get_topics()
    print("✓ Test passed")
```

### Test with turtlesim:

```bash
# Terminal 1
ros2 run turtlesim turtlesim_node

# Terminal 2
python3 -c "
import rclpy
from utils.ros2_manager import ROS2Manager

rclpy.init()
m = ROS2Manager()
m.initialize()
print('Topics:', m.get_topics())
print('Nodes:', m.get_nodes())
print('Topic type:', m.get_topic_type('/turtle1/cmd_vel'))
m.shutdown()
rclpy.shutdown()
"
```

---

## Migration Checklist

For each function in `server.py`:

- [ ] Identify the rosapi service call
- [ ] Find equivalent ROS2Manager method
- [ ] Update function to use ROS2Manager
- [ ] Test with turtlesim
- [ ] Test error cases
- [ ] Update docstring if needed
- [ ] Remove old WebSocket code
- [ ] Commit change

---

## Common Issues

### Issue 1: "No module named 'rclpy'"
**Solution:**
```bash
source /opt/ros/humble/setup.bash
pip install rclpy
```

### Issue 2: "Failed to initialize ROS 2 node"
**Solution:**
```python
# Make sure to init rclpy first
import rclpy
rclpy.init()
# Then create manager
manager = ROS2Manager()
```

### Issue 3: "Context already initialized"
**Solution:**
```python
# Check if already initialized
if not rclpy.ok():
    rclpy.init()
```

### Issue 4: Cannot find message type
**Solution:**
```bash
# Install message packages
sudo apt install ros-humble-<package-name>
# Example:
sudo apt install ros-humble-geometry-msgs
```

---

## Performance Testing

Quick benchmark:

```python
import time
import rclpy
from utils.ros2_manager import ROS2Manager

rclpy.init()
manager = ROS2Manager()
manager.initialize()

# Benchmark get_topics
start = time.time()
for _ in range(100):
    manager.get_topics()
end = time.time()
print(f"Average time: {(end-start)/100*1000:.2f}ms")

manager.shutdown()
rclpy.shutdown()
```

Expected: <10ms per call

---

## Debugging

### Enable ROS 2 logging:
```python
import rclpy
rclpy.init()
rclpy.logging.set_logger_level('ros2_manager', rclpy.logging.LoggingSeverity.DEBUG)
```

### Check DDS discovery:
```bash
ros2 topic list
ros2 node list
ros2 topic info /topic_name -v
```

### Profile performance:
```python
import cProfile
import rclpy
from utils.ros2_manager import ROS2Manager

def profile():
    rclpy.init()
    manager = ROS2Manager()
    manager.initialize()
    manager.get_topics()
    manager.shutdown()
    rclpy.shutdown()

cProfile.run('profile()', sort='cumulative')
```

---

## Next Steps

1. **Start small:** Migrate one function (e.g., `get_topics()`)
2. **Test thoroughly:** Ensure it works with real ROS 2 system
3. **Continue:** Follow the roadmap in `docs/implementation_roadmap.md`
4. **Get help:** Refer to full docs in `docs/native_ros2_migration.md`

---

## Quick Reference

### Key Files
- `utils/ros2_manager.py` - Main implementation
- `server.py` - Update MCP tools here
- `docs/native_ros2_migration.md` - Full guide
- `docs/implementation_roadmap.md` - Detailed plan

### Key Commands
```bash
# Install ROS 2
sudo apt install ros-humble-ros-base

# Test ROS2Manager
python3 -c "from utils.ros2_manager import ROS2Manager; print('OK')"

# Run turtlesim for testing
ros2 run turtlesim turtlesim_node

# Check ROS 2 environment
printenv | grep ROS
```

### Get Help
- Full documentation: `docs/native_ros2_migration.md`
- API comparison: `docs/rosapi_comparison.md`
- Detailed roadmap: `docs/implementation_roadmap.md`
- GitHub issue: #145

---

**Ready to start?** Begin with Phase 1, Task 1.1 in `docs/implementation_roadmap.md`!
