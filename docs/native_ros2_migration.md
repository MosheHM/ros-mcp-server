# Native ROS 2 Migration Guide

## Overview

This document outlines the plan to remove the dependency on `rosapi` (from `rosbridge_suite`) and implement native ROS 2 APIs for graph and parameter management.

## Current Architecture

```
┌─────────────┐         WebSocket         ┌──────────────┐
│  MCP Server │ ◄────────────────────────► │  rosbridge   │
│  (Python)   │                            │  (WebSocket) │
└─────────────┘                            └──────┬───────┘
                                                   │
                                                   ▼
                                           ┌──────────────┐
                                           │   rosapi     │
                                           │  (Services)  │
                                           └──────┬───────┘
                                                   │
                                                   ▼
                                           ┌──────────────┐
                                           │  ROS 2 Graph │
                                           │  & Params    │
                                           └──────────────┘
```

## Target Architecture (Option B - Direct rclpy)

```
┌─────────────────────────────┐
│  MCP Server + ROS 2 Node    │
│  (Python with rclpy)        │
│                             │
│  ┌────────────┐             │
│  │ MCP Tools  │             │
│  └─────┬──────┘             │
│        │                    │
│        ▼                    │
│  ┌────────────┐             │
│  │ rclpy APIs │             │
│  └─────┬──────┘             │
│        │                    │
└────────┼────────────────────┘
         │
         ▼
┌──────────────────────┐
│  ROS 2 DDS Layer     │
│  (Discovery, Graph)  │
└──────────────────────┘
```

## Implementation Approach

### Option A: Hybrid Approach (Recommended for Initial Phase)
Keep rosbridge for pub/sub operations but replace rosapi for introspection.

**Pros:**
- Incremental migration
- Lower risk
- Maintains existing pub/sub functionality

**Cons:**
- Still depends on rosbridge
- More complex codebase during transition

### Option B: Pure rclpy (Recommended for Final Implementation)
Replace rosbridge entirely with rclpy in the MCP server.

**Pros:**
- Complete removal of rosbridge dependency
- Simpler final architecture
- Native ROS 2 integration
- Better performance

**Cons:**
- Requires ROS 2 installation on MCP server machine
- More complex initial implementation
- Drops ROS 1 support

### Option C: Separate ROS Node with IPC
Create a separate ROS 2 node that communicates with MCP server via IPC.

**Pros:**
- Separation of concerns
- Could support both ROS 1 and ROS 2 with different nodes

**Cons:**
- Most complex architecture
- Additional communication layer overhead
- More deployment complexity

## Detailed Implementation Plan

### Phase 1: Setup and Infrastructure

#### 1.1. Add rclpy Dependency

**File:** `pyproject.toml`

```python
dependencies = [
    "fastmcp>=2.11.3",
    "jsonschema>=4.25.1",
    "mcp[cli]>=1.13.0",
    "opencv-python>=4.11.0.86",
    "pillow>=11.3.0",
    # Add ROS 2 Python dependencies
    "rclpy>=3.0.0",  # Core ROS 2 Python client library
    "rosidl-runtime-py>=0.11.0",  # For message type introspection
]
```

#### 1.2. Create ROS 2 Node Wrapper

**File:** `utils/ros2_manager.py`

```python
"""
ROS 2 node manager for native graph and parameter introspection.
Replaces rosapi dependency.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from typing import List, Dict, Tuple, Optional
import threading


class ROS2Manager:
    """
    Manages ROS 2 node lifecycle and provides native graph introspection APIs.
    This class replaces the rosapi-based functionality.
    """
    
    def __init__(self, node_name: str = "mcp_ros2_node"):
        """
        Initialize ROS 2 manager.
        
        Args:
            node_name: Name for the ROS 2 node
        """
        self._initialized = False
        self._node: Optional[Node] = None
        self._node_name = node_name
        self._spin_thread: Optional[threading.Thread] = None
        
    def initialize(self):
        """Initialize ROS 2 node."""
        if self._initialized:
            return
            
        try:
            # Initialize ROS 2 context
            if not rclpy.ok():
                rclpy.init()
            
            # Create node
            self._node = Node(self._node_name)
            
            # Start spinning in background thread
            self._spin_thread = threading.Thread(target=self._spin, daemon=True)
            self._spin_thread.start()
            
            self._initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ROS 2 node: {e}")
    
    def _spin(self):
        """Spin the node in a background thread."""
        if self._node:
            rclpy.spin(self._node)
    
    def shutdown(self):
        """Shutdown ROS 2 node and cleanup."""
        if self._node:
            self._node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        self._initialized = False
    
    # ==================== Topic Introspection ====================
    
    def get_topics(self) -> Dict[str, List[str]]:
        """
        Get all topics and their types.
        Replaces: /rosapi/topics
        
        Returns:
            dict: {'topics': [...], 'types': [...]}
        """
        if not self._initialized:
            self.initialize()
        
        topic_tuples = self._node.get_topic_names_and_types()
        
        topics = []
        types = []
        
        for topic_name, type_list in topic_tuples:
            topics.append(topic_name)
            # Topics can have multiple types, take the first one
            types.append(type_list[0] if type_list else "unknown")
        
        return {
            "topics": topics,
            "types": types
        }
    
    def get_topic_type(self, topic: str) -> Optional[str]:
        """
        Get the message type for a specific topic.
        Replaces: /rosapi/topic_type
        
        Args:
            topic: Topic name
            
        Returns:
            Message type string or None
        """
        if not self._initialized:
            self.initialize()
        
        topic_tuples = self._node.get_topic_names_and_types()
        
        for topic_name, type_list in topic_tuples:
            if topic_name == topic:
                return type_list[0] if type_list else None
        
        return None
    
    def get_publishers_for_topic(self, topic: str) -> List[str]:
        """
        Get list of nodes publishing to a topic.
        Replaces: /rosapi/publishers
        
        Args:
            topic: Topic name
            
        Returns:
            List of node names
        """
        if not self._initialized:
            self.initialize()
        
        publishers_info = self._node.get_publishers_info_by_topic(topic)
        
        # Extract unique node names
        node_names = list(set([pub.node_name for pub in publishers_info]))
        
        return node_names
    
    def get_subscribers_for_topic(self, topic: str) -> List[str]:
        """
        Get list of nodes subscribed to a topic.
        Replaces: /rosapi/subscribers
        
        Args:
            topic: Topic name
            
        Returns:
            List of node names
        """
        if not self._initialized:
            self.initialize()
        
        subscribers_info = self._node.get_subscriptions_info_by_topic(topic)
        
        # Extract unique node names
        node_names = list(set([sub.node_name for sub in subscribers_info]))
        
        return node_names
    
    # ==================== Service Introspection ====================
    
    def get_services(self) -> List[str]:
        """
        Get all service names.
        Replaces: /rosapi/services
        
        Returns:
            List of service names
        """
        if not self._initialized:
            self.initialize()
        
        service_tuples = self._node.get_service_names_and_types()
        
        services = [name for name, _ in service_tuples]
        
        return services
    
    def get_service_type(self, service: str) -> Optional[str]:
        """
        Get the service type for a specific service.
        Replaces: /rosapi/service_type
        
        Args:
            service: Service name
            
        Returns:
            Service type string or None
        """
        if not self._initialized:
            self.initialize()
        
        service_tuples = self._node.get_service_names_and_types()
        
        for service_name, type_list in service_tuples:
            if service_name == service:
                return type_list[0] if type_list else None
        
        return None
    
    # Note: ROS 2 doesn't have a direct API to get service providers
    # This would need to be inferred from node information
    
    # ==================== Node Introspection ====================
    
    def get_nodes(self) -> List[str]:
        """
        Get all node names.
        Replaces: /rosapi/nodes
        
        Returns:
            List of node names
        """
        if not self._initialized:
            self.initialize()
        
        node_names = self._node.get_node_names()
        
        return node_names
    
    def get_node_details(self, node_name: str) -> Dict:
        """
        Get details about a specific node.
        Replaces: /rosapi/node_details
        
        This requires aggregating information from multiple APIs.
        
        Args:
            node_name: Node name
            
        Returns:
            Dictionary with publishers, subscribers, and services
        """
        if not self._initialized:
            self.initialize()
        
        # Get all topics and check which ones this node publishes/subscribes to
        publishers = []
        subscribers = []
        
        topic_tuples = self._node.get_topic_names_and_types()
        
        for topic_name, _ in topic_tuples:
            # Check publishers
            pub_info = self._node.get_publishers_info_by_topic(topic_name)
            for pub in pub_info:
                if pub.node_name == node_name and topic_name not in publishers:
                    publishers.append(topic_name)
            
            # Check subscribers
            sub_info = self._node.get_subscriptions_info_by_topic(topic_name)
            for sub in sub_info:
                if sub.node_name == node_name and topic_name not in subscribers:
                    subscribers.append(topic_name)
        
        # Get services provided by this node
        # ROS 2 doesn't have a direct "get services by node" API
        # We'll need to check all services and match node names
        services = []
        # This is a limitation - we can't easily get services per node in ROS 2
        # May need to be left empty or use alternative approach
        
        return {
            "publishing": publishers,
            "subscribing": subscribers,
            "services": services
        }
    
    # ==================== Message/Service Type Details ====================
    
    def get_message_details(self, message_type: str) -> Dict:
        """
        Get message structure details.
        Replaces: /rosapi/message_details
        
        Uses rosidl_runtime_py for introspection.
        
        Args:
            message_type: Message type (e.g., 'geometry_msgs/msg/Twist')
            
        Returns:
            Dictionary with message structure
        """
        try:
            from rosidl_runtime_py import get_message_typesupport
            from rosidl_runtime_py.utilities import get_message
            
            # Parse type string (e.g., 'geometry_msgs/msg/Twist')
            msg_class = get_message(message_type)
            
            # Get field names and types
            fields = {}
            if hasattr(msg_class, 'get_fields_and_field_types'):
                fields = msg_class.get_fields_and_field_types()
            
            return {
                "type": message_type,
                "fields": fields,
                "field_count": len(fields)
            }
            
        except Exception as e:
            return {"error": f"Failed to get message details: {e}"}
    
    def get_service_details(self, service_type: str) -> Dict:
        """
        Get service request and response structure.
        Replaces: /rosapi/service_request_details and /rosapi/service_response_details
        
        Args:
            service_type: Service type
            
        Returns:
            Dictionary with request and response structures
        """
        try:
            from rosidl_runtime_py.utilities import get_service
            
            # Get service class
            srv_class = get_service(service_type)
            
            # Get request and response fields
            request_fields = {}
            response_fields = {}
            
            if hasattr(srv_class, 'Request'):
                req_class = srv_class.Request
                if hasattr(req_class, 'get_fields_and_field_types'):
                    request_fields = req_class.get_fields_and_field_types()
            
            if hasattr(srv_class, 'Response'):
                resp_class = srv_class.Response
                if hasattr(resp_class, 'get_fields_and_field_types'):
                    response_fields = resp_class.get_fields_and_field_types()
            
            return {
                "service_type": service_type,
                "request": {
                    "fields": request_fields,
                    "field_count": len(request_fields)
                },
                "response": {
                    "fields": response_fields,
                    "field_count": len(response_fields)
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get service details: {e}"}
    
    # ==================== ROS Version Detection ====================
    
    def get_ros_version(self) -> Dict[str, str]:
        """
        Get ROS version and distribution.
        Replaces: /rosapi/get_ros_version
        
        Returns:
            Dictionary with version and distro
        """
        import os
        
        # ROS 2 version is always "2"
        version = "2"
        
        # Get distro from environment variable
        distro = os.environ.get('ROS_DISTRO', 'unknown')
        
        return {
            "version": version,
            "distro": distro
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
```

### Phase 2: Update server.py Functions

For each function in `server.py` that uses rosapi, update to use ROS2Manager:

#### Example: `get_topics()` function

**Before (using rosapi):**
```python
@mcp.tool(description=("Fetch available topics from the ROS bridge.\nExample:\nget_topics()"))
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

**After (using native ROS 2):**
```python
@mcp.tool(description=("Fetch available topics from ROS 2.\nExample:\nget_topics()"))
def get_topics() -> dict:
    try:
        with ros2_manager:
            result = ros2_manager.get_topics()
            return result
    except Exception as e:
        return {"error": f"Failed to get topics: {e}"}
```

### Phase 3: Handle Pub/Sub Operations

For pub/sub, you have two options:

#### Option 3A: Keep rosbridge for pub/sub
Keep using WebSocketManager for publish/subscribe operations while using ROS2Manager for introspection.

#### Option 3B: Use native rclpy pub/sub
Implement publishers and subscribers using rclpy.

**Example implementation in ROS2Manager:**

```python
def create_publisher(self, topic: str, msg_type: str):
    """Create a publisher for a topic."""
    from rosidl_runtime_py.utilities import get_message
    
    msg_class = get_message(msg_type)
    publisher = self._node.create_publisher(msg_class, topic, 10)
    return publisher

def publish_message(self, topic: str, msg_type: str, msg_data: dict):
    """Publish a message to a topic."""
    from rosidl_runtime_py.utilities import get_message
    
    msg_class = get_message(msg_type)
    msg = msg_class(**msg_data)
    
    # Create temporary publisher
    publisher = self._node.create_publisher(msg_class, topic, 10)
    publisher.publish(msg)
    
    # Note: May want to cache publishers for efficiency
```

### Phase 4: Parameter Management

Add parameter management functions to ROS2Manager:

```python
def get_parameter(self, node_name: str, param_name: str) -> Optional[any]:
    """
    Get a parameter from a node.
    Uses native parameter service calls.
    """
    from rcl_interfaces.srv import GetParameters
    
    client = self._node.create_client(
        GetParameters,
        f'{node_name}/get_parameters'
    )
    
    if not client.wait_for_service(timeout_sec=2.0):
        return None
    
    request = GetParameters.Request()
    request.names = [param_name]
    
    future = client.call_async(request)
    rclpy.spin_until_future_complete(self._node, future)
    
    if future.result():
        values = future.result().values
        if values:
            return values[0]
    
    return None
```

## Migration Steps

### Step 1: Add ROS2Manager alongside existing code
- Keep all existing rosapi calls working
- Add ROS2Manager with new functions
- Test in parallel

### Step 2: Create feature flag
- Add configuration option to choose between rosapi and native
- Default to rosapi initially

### Step 3: Gradually migrate functions
- Update one function at a time
- Test thoroughly
- Update documentation

### Step 4: Remove rosapi dependency
- Once all functions migrated and tested
- Remove rosbridge from dependencies
- Update installation docs

## Testing Strategy

1. **Unit Tests**: Test each ROS2Manager function
2. **Integration Tests**: Test with real ROS 2 system
3. **Regression Tests**: Ensure existing functionality works
4. **Performance Tests**: Compare performance with rosapi

## Documentation Updates

1. Update `installation.md` to remove rosbridge requirement
2. Add note about ROS 2 requirement
3. Update examples
4. Create migration guide for users

## Breaking Changes

- **ROS 1 Support Dropped**: This implementation only supports ROS 2
- **ROS 2 Required**: MCP server machine must have ROS 2 installed
- **rosbridge No Longer Needed**: Can be removed from robot

## Benefits Realized

1. ✅ No dependency on rosbridge_suite
2. ✅ Native ROS 2 integration
3. ✅ Better performance (no WebSocket overhead for introspection)
4. ✅ Simpler deployment
5. ✅ Direct access to ROS 2 graph
6. ✅ Real-time parameter updates

## Next Steps

1. Review and approve architecture
2. Implement ROS2Manager prototype
3. Test with sample ROS 2 system
4. Gradually migrate functions
5. Update documentation
6. Release as major version (3.0.0)
