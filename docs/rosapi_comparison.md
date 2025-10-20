# rosapi vs Native ROS 2 API Comparison

This document provides a side-by-side comparison of the current rosapi-based implementation and the proposed native ROS 2 API implementation.

## Architecture Comparison

### Current (rosapi-based)

```
MCP Server (Python)
    ↓ WebSocket
rosbridge_server
    ↓ Service Calls
rosapi (ROS Package)
    ↓ ROS 2 APIs
ROS 2 Graph/Parameters
```

**Dependencies:**
- rosbridge_server (must be running on robot)
- rosapi package
- WebSocket communication
- Service call overhead

### Proposed (Native ROS 2)

```
MCP Server (Python with rclpy)
    ↓ Direct API calls
ROS 2 Graph/Parameters
```

**Dependencies:**
- rclpy (ROS 2 Python client library)
- rosidl_runtime_py (for type introspection)
- Direct DDS communication

## API Comparison

### 1. Get Topics

#### Current (rosapi)
```python
# Service call via WebSocket
message = {
    "op": "call_service",
    "service": "/rosapi/topics",
    "type": "rosapi/Topics",
    "id": "get_topics_request_1",
}

with ws_manager:
    response = ws_manager.request(message)
    
if response and "values" in response:
    topics = response["values"]["topics"]
    types = response["values"]["types"]
```

#### Proposed (Native ROS 2)
```python
# Direct API call
with ros2_manager:
    result = ros2_manager.get_topics()
    topics = result["topics"]
    types = result["types"]

# Under the hood:
# topic_tuples = node.get_topic_names_and_types()
```

**Benefits:**
- No WebSocket overhead
- No service call delay
- Direct access to DDS discovery

---

### 2. Get Topic Type

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/topic_type",
    "type": "rosapi/TopicType",
    "args": {"topic": "/cmd_vel"},
    "id": "get_topic_type_request",
}

with ws_manager:
    response = ws_manager.request(message)
    topic_type = response["values"]["type"]
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    topic_type = ros2_manager.get_topic_type("/cmd_vel")

# Under the hood:
# Queries node.get_topic_names_and_types() and filters
```

**Benefits:**
- Simpler API
- Faster lookup (no service call)
- Type-safe

---

### 3. Get Publishers for Topic

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/publishers",
    "type": "rosapi/Publishers",
    "args": {"topic": "/cmd_vel"},
    "id": "get_publishers_request",
}

with ws_manager:
    response = ws_manager.request(message)
    publishers = response["values"]["publishers"]
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    publishers = ros2_manager.get_publishers_for_topic("/cmd_vel")

# Under the hood:
# publishers_info = node.get_publishers_info_by_topic(topic)
# Returns list of PublisherInfo objects
```

**Benefits:**
- More detailed information available (QoS, etc.)
- Real-time discovery
- No intermediate service

---

### 4. Get Message Details

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/message_details",
    "type": "rosapi/MessageDetails",
    "args": {"type": "geometry_msgs/Twist"},
    "id": "get_message_details_request",
}

with ws_manager:
    response = ws_manager.request(message)
    typedefs = response["values"]["typedefs"]
    # Parse typedefs into structure
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    details = ros2_manager.get_message_details("geometry_msgs/msg/Twist")
    fields = details["fields"]

# Under the hood:
# from rosidl_runtime_py.utilities import get_message
# msg_class = get_message(message_type)
# fields = msg_class.get_fields_and_field_types()
```

**Benefits:**
- Direct access to Python message classes
- Built-in type introspection
- Cleaner API

---

### 5. Get Services

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/services",
    "type": "rosapi/Services",
    "args": {},
    "id": "get_services_request",
}

with ws_manager:
    response = ws_manager.request(message)
    services = response["values"]["services"]
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    services = ros2_manager.get_services()

# Under the hood:
# service_tuples = node.get_service_names_and_types()
```

**Benefits:**
- Faster
- More reliable
- No dependency on rosapi

---

### 6. Get Nodes

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/nodes",
    "type": "rosapi/Nodes",
    "args": {},
    "id": "get_nodes_request",
}

with ws_manager:
    response = ws_manager.request(message)
    nodes = response["values"]["nodes"]
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    nodes = ros2_manager.get_nodes()

# Under the hood:
# node_names = node.get_node_names()
```

**Benefits:**
- One line of code
- Real-time node discovery
- Direct DDS query

---

### 7. Get Node Details

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/node_details",
    "type": "rosapi/NodeDetails",
    "args": {"node": "/turtlesim"},
    "id": "get_node_details_request",
}

with ws_manager:
    response = ws_manager.request(message)
    publishers = response["values"]["publishing"]
    subscribers = response["values"]["subscribing"]
    services = response["values"]["services"]
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    details = ros2_manager.get_node_details("/turtlesim")
    publishers = details["publishing"]
    subscribers = details["subscribing"]
    services = details["services"]

# Under the hood:
# Aggregates multiple ROS 2 API calls:
# - get_publishers_info_by_topic() for each topic
# - get_subscriptions_info_by_topic() for each topic
```

**Note:** 
- rosapi provides a convenient single service call
- Native ROS 2 requires aggregating multiple queries
- Trade-off: More overhead in code, but no external dependency

---

### 8. Get Parameter

#### Current (rosapi)
```python
message = {
    "op": "call_service",
    "service": "/rosapi/get_param",
    "args": {"name": "/rosdistro"},
    "id": "get_param_request",
}

with ws_manager:
    response = ws_manager.request(message)
    value = response["values"]["value"]
```

#### Proposed (Native ROS 2)
```python
with ros2_manager:
    value = ros2_manager.get_parameter("/my_node", "param_name")

# Under the hood:
# Uses native parameter services:
# client = node.create_client(GetParameters, '/my_node/get_parameters')
# Makes service call directly via DDS
```

**Benefits:**
- Standard ROS 2 parameter API
- Can subscribe to /parameter_events for real-time updates
- Type-safe parameter handling

---

## Performance Comparison

### Latency

| Operation | Current (rosapi) | Proposed (Native) | Improvement |
|-----------|------------------|-------------------|-------------|
| Get Topics | ~50-100ms | ~5-10ms | 5-10x faster |
| Get Topic Type | ~50-100ms | ~5-10ms | 5-10x faster |
| Get Publishers | ~50-100ms | ~10-20ms | 3-5x faster |
| Get Message Details | ~100-200ms | ~20-30ms | 5-7x faster |
| Get Services | ~50-100ms | ~5-10ms | 5-10x faster |
| Get Nodes | ~50-100ms | ~5-10ms | 5-10x faster |

*Note: Times are estimates based on typical WebSocket vs direct API overhead*

### Resource Usage

| Resource | Current (rosapi) | Proposed (Native) |
|----------|------------------|-------------------|
| CPU | Moderate (WebSocket + rosapi node) | Low (direct DDS) |
| Memory | ~50-100MB (rosbridge + rosapi) | ~20-30MB (just rclpy) |
| Network | WebSocket connection required | DDS only |
| Dependencies | rosbridge_server, rosapi | rclpy, rosidl_runtime_py |

---

## Code Complexity

### Lines of Code for get_topics()

**Current:**
```python
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
    else:
        return {"warning": "No topics found"}
```
**Lines:** ~12

**Proposed:**
```python
def get_topics() -> dict:
    try:
        with ros2_manager:
            return ros2_manager.get_topics()
    except Exception as e:
        return {"error": f"Failed to get topics: {e}"}
```
**Lines:** ~6

**Reduction:** 50% less code

---

## Deployment Comparison

### Current Deployment

1. **On Robot:**
   - Install ROS 2
   - Install rosbridge_server: `apt install ros-humble-rosbridge-server`
   - Launch rosbridge: `ros2 launch rosbridge_server rosbridge_websocket_launch.xml`
   - Ensure network connectivity

2. **On MCP Server Machine:**
   - Install Python dependencies (no ROS needed)
   - Configure WebSocket connection
   - Connect via network

### Proposed Deployment

1. **On Robot:**
   - Install ROS 2
   - Run ROS nodes (no rosbridge needed)

2. **On MCP Server Machine:**
   - Install ROS 2 (or just rclpy)
   - Install Python dependencies
   - Connect via DDS (automatic discovery on same network)

**Benefits:**
- One less package to install (rosbridge_server)
- One less node to run
- Simpler configuration
- More reliable (no WebSocket connection to maintain)

---

## Feature Parity

| Feature | Current (rosapi) | Proposed (Native) | Status |
|---------|------------------|-------------------|--------|
| List Topics | ✅ | ✅ | Full parity |
| Get Topic Type | ✅ | ✅ | Full parity |
| Get Publishers | ✅ | ✅ | Full parity |
| Get Subscribers | ✅ | ✅ | Full parity |
| List Services | ✅ | ✅ | Full parity |
| Get Service Type | ✅ | ✅ | Full parity |
| Get Service Providers | ✅ | ⚠️ | Limited* |
| List Nodes | ✅ | ✅ | Full parity |
| Get Node Details | ✅ | ⚠️ | Limited* |
| Message Details | ✅ | ✅ | Full parity |
| Service Details | ✅ | ✅ | Full parity |
| Get Parameters | ✅ | ✅ | Full parity |
| Set Parameters | ✅ | ✅ | Full parity |
| ROS Version Detection | ✅ | ✅ | Full parity |
| Publish/Subscribe | ✅ | ✅** | Full parity |
| Call Services | ✅ | ✅** | Full parity |

\* ROS 2 native APIs don't provide direct "services by node" information. Need to aggregate from multiple sources.

\** Can use rclpy for pub/sub and service calls, or keep rosbridge for these operations in hybrid approach.

---

## Migration Strategy

### Phase 1: Parallel Implementation (Weeks 1-2)
- Implement ROS2Manager alongside existing code
- Add feature flag to switch between rosapi and native
- Test with sample ROS 2 systems

### Phase 2: Gradual Migration (Weeks 3-4)
- Migrate introspection functions one by one
- Keep rosbridge for pub/sub initially
- Extensive testing

### Phase 3: Full Native Implementation (Weeks 5-6)
- Implement native pub/sub with rclpy
- Remove rosapi dependency
- Update documentation

### Phase 4: Release (Week 7)
- Final testing
- Release as major version (3.0.0)
- Provide migration guide

---

## Recommendation

**Recommended Approach: Hybrid → Full Native**

1. **Phase 1 (Hybrid):** Use native ROS 2 for introspection, keep rosbridge for pub/sub
   - Low risk
   - Immediate benefits for introspection
   - Maintains compatibility

2. **Phase 2 (Full Native):** Replace rosbridge entirely with rclpy
   - Complete architecture simplification
   - Maximum performance
   - Removes all external dependencies

This approach balances risk and benefits, allowing incremental migration with fallback options.
