"""
ROS 2 node manager for native graph and parameter introspection.
This module replaces rosapi dependency with native ROS 2 APIs.

NOTE: This is a prototype implementation for planning purposes.
It demonstrates how to use native ROS 2 APIs instead of rosapi.
"""

import threading
from typing import Any, Dict, List, Optional


class ROS2Manager:
    """
    Manages ROS 2 node lifecycle and provides native graph introspection APIs.
    This class is designed to replace the rosapi-based functionality.
    
    This implementation uses rclpy (ROS 2 Python client library) to directly
    interact with the ROS 2 graph, eliminating the need for rosbridge and rosapi.
    """

    def __init__(self, node_name: str = "mcp_ros2_node"):
        """
        Initialize ROS 2 manager.

        Args:
            node_name: Name for the ROS 2 node
        """
        self._initialized = False
        self._node = None
        self._node_name = node_name
        self._spin_thread: Optional[threading.Thread] = None

    def initialize(self):
        """
        Initialize ROS 2 node.
        
        This must be called before using any other methods.
        Requires ROS 2 and rclpy to be installed.
        """
        if self._initialized:
            return

        try:
            import rclpy
            from rclpy.node import Node

            # Initialize ROS 2 context
            if not rclpy.ok():
                rclpy.init()

            # Create node
            self._node = Node(self._node_name)

            # Start spinning in background thread
            self._spin_thread = threading.Thread(target=self._spin, daemon=True)
            self._spin_thread.start()

            self._initialized = True

        except ImportError as e:
            raise RuntimeError(
                f"Failed to import rclpy. Ensure ROS 2 is installed: {e}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ROS 2 node: {e}")

    def _spin(self):
        """Spin the node in a background thread."""
        if self._node:
            import rclpy

            rclpy.spin(self._node)

    def shutdown(self):
        """Shutdown ROS 2 node and cleanup."""
        if self._node:
            self._node.destroy_node()

        try:
            import rclpy

            if rclpy.ok():
                rclpy.shutdown()
        except ImportError:
            pass

        self._initialized = False

    # ==================== Topic Introspection ====================

    def get_topics(self) -> Dict[str, List[str]]:
        """
        Get all topics and their types.
        
        Replaces: /rosapi/topics service call

        Returns:
            dict: {'topics': [...], 'types': [...]}
            
        Example:
            {
                'topics': ['/cmd_vel', '/odom', '/scan'],
                'types': ['geometry_msgs/msg/Twist', 'nav_msgs/msg/Odometry', 'sensor_msgs/msg/LaserScan']
            }
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

        return {"topics": topics, "types": types}

    def get_topic_type(self, topic: str) -> Optional[str]:
        """
        Get the message type for a specific topic.
        
        Replaces: /rosapi/topic_type service call

        Args:
            topic: Topic name (e.g., '/cmd_vel')

        Returns:
            Message type string or None if topic doesn't exist
            
        Example:
            get_topic_type('/cmd_vel') -> 'geometry_msgs/msg/Twist'
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
        
        Replaces: /rosapi/publishers service call

        Args:
            topic: Topic name

        Returns:
            List of node names
            
        Example:
            get_publishers_for_topic('/cmd_vel') -> ['/teleop_keyboard', '/nav_node']
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
        
        Replaces: /rosapi/subscribers service call

        Args:
            topic: Topic name

        Returns:
            List of node names
            
        Example:
            get_subscribers_for_topic('/cmd_vel') -> ['/robot_driver']
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
        
        Replaces: /rosapi/services service call

        Returns:
            List of service names
            
        Example:
            get_services() -> ['/set_parameters', '/get_parameters', '/spawn_entity']
        """
        if not self._initialized:
            self.initialize()

        service_tuples = self._node.get_service_names_and_types()

        services = [name for name, _ in service_tuples]

        return services

    def get_service_type(self, service: str) -> Optional[str]:
        """
        Get the service type for a specific service.
        
        Replaces: /rosapi/service_type service call

        Args:
            service: Service name

        Returns:
            Service type string or None if service doesn't exist
            
        Example:
            get_service_type('/spawn_entity') -> 'gazebo_msgs/srv/SpawnEntity'
        """
        if not self._initialized:
            self.initialize()

        service_tuples = self._node.get_service_names_and_types()

        for service_name, type_list in service_tuples:
            if service_name == service:
                return type_list[0] if type_list else None

        return None

    # ==================== Node Introspection ====================

    def get_nodes(self) -> List[str]:
        """
        Get all node names.
        
        Replaces: /rosapi/nodes service call

        Returns:
            List of node names
            
        Example:
            get_nodes() -> ['/turtlesim', '/teleop_keyboard', '/mcp_ros2_node']
        """
        if not self._initialized:
            self.initialize()

        node_names = self._node.get_node_names()

        return node_names

    def get_node_details(self, node_name: str) -> Dict:
        """
        Get details about a specific node.
        
        Replaces: /rosapi/node_details service call
        
        Note: This requires aggregating information from multiple native APIs
        since ROS 2 doesn't have a single "node_details" API.

        Args:
            node_name: Node name

        Returns:
            Dictionary with publishers, subscribers, and services
            
        Example:
            get_node_details('/turtlesim') -> {
                'publishing': ['/turtle1/pose', '/turtle1/color_sensor'],
                'subscribing': ['/turtle1/cmd_vel'],
                'services': []  # Note: Service per node info is limited in ROS 2
            }
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

        # Note: ROS 2 doesn't have a direct "get services by node" API
        # This is a known limitation of the native ROS 2 introspection
        services = []

        return {
            "publishing": publishers,
            "subscribing": subscribers,
            "services": services,
        }

    # ==================== Message/Service Type Details ====================

    def get_message_details(self, message_type: str) -> Dict:
        """
        Get message structure details.
        
        Replaces: /rosapi/message_details service call
        
        Uses rosidl_runtime_py for message type introspection.

        Args:
            message_type: Message type (e.g., 'geometry_msgs/msg/Twist')

        Returns:
            Dictionary with message structure
            
        Example:
            get_message_details('geometry_msgs/msg/Twist') -> {
                'type': 'geometry_msgs/msg/Twist',
                'fields': {
                    'linear': 'geometry_msgs/msg/Vector3',
                    'angular': 'geometry_msgs/msg/Vector3'
                },
                'field_count': 2
            }
        """
        try:
            from rosidl_runtime_py.utilities import get_message

            # Get message class
            msg_class = get_message(message_type)

            # Get field names and types
            fields = {}
            if hasattr(msg_class, "get_fields_and_field_types"):
                fields = msg_class.get_fields_and_field_types()

            return {"type": message_type, "fields": fields, "field_count": len(fields)}

        except ImportError:
            return {"error": "rosidl_runtime_py not available. Install ROS 2 Python packages."}
        except Exception as e:
            return {"error": f"Failed to get message details: {e}"}

    def get_service_details(self, service_type: str) -> Dict:
        """
        Get service request and response structure.
        
        Replaces: /rosapi/service_request_details and /rosapi/service_response_details

        Args:
            service_type: Service type (e.g., 'std_srvs/srv/SetBool')

        Returns:
            Dictionary with request and response structures
            
        Example:
            get_service_details('std_srvs/srv/SetBool') -> {
                'service_type': 'std_srvs/srv/SetBool',
                'request': {
                    'fields': {'data': 'boolean'},
                    'field_count': 1
                },
                'response': {
                    'fields': {'success': 'boolean', 'message': 'string'},
                    'field_count': 2
                }
            }
        """
        try:
            from rosidl_runtime_py.utilities import get_service

            # Get service class
            srv_class = get_service(service_type)

            # Get request and response fields
            request_fields = {}
            response_fields = {}

            if hasattr(srv_class, "Request"):
                req_class = srv_class.Request
                if hasattr(req_class, "get_fields_and_field_types"):
                    request_fields = req_class.get_fields_and_field_types()

            if hasattr(srv_class, "Response"):
                resp_class = srv_class.Response
                if hasattr(resp_class, "get_fields_and_field_types"):
                    response_fields = resp_class.get_fields_and_field_types()

            return {
                "service_type": service_type,
                "request": {"fields": request_fields, "field_count": len(request_fields)},
                "response": {"fields": response_fields, "field_count": len(response_fields)},
            }

        except ImportError:
            return {"error": "rosidl_runtime_py not available. Install ROS 2 Python packages."}
        except Exception as e:
            return {"error": f"Failed to get service details: {e}"}

    # ==================== Parameter Management ====================

    def get_parameter(self, node_name: str, param_name: str) -> Optional[Any]:
        """
        Get a parameter from a node.
        
        Uses native ROS 2 parameter service calls.
        Replaces: /rosapi/get_param

        Args:
            node_name: Name of the node
            param_name: Name of the parameter

        Returns:
            Parameter value or None
            
        Example:
            get_parameter('/my_node', 'max_velocity') -> 1.5
        """
        try:
            import rclpy
            from rcl_interfaces.srv import GetParameters

            if not self._initialized:
                self.initialize()

            # Create service client
            client = self._node.create_client(GetParameters, f"{node_name}/get_parameters")

            if not client.wait_for_service(timeout_sec=2.0):
                return None

            # Prepare request
            request = GetParameters.Request()
            request.names = [param_name]

            # Call service
            future = client.call_async(request)
            rclpy.spin_until_future_complete(self._node, future, timeout_sec=2.0)

            if future.result():
                values = future.result().values
                if values:
                    # Convert parameter value to Python type
                    param_value = values[0]
                    if param_value.type == 1:  # PARAMETER_BOOL
                        return param_value.bool_value
                    elif param_value.type == 2:  # PARAMETER_INTEGER
                        return param_value.integer_value
                    elif param_value.type == 3:  # PARAMETER_DOUBLE
                        return param_value.double_value
                    elif param_value.type == 4:  # PARAMETER_STRING
                        return param_value.string_value
                    # Add more types as needed

            return None

        except ImportError:
            return None
        except Exception:
            return None

    # ==================== ROS Version Detection ====================

    def get_ros_version(self) -> Dict[str, str]:
        """
        Get ROS version and distribution.
        
        Replaces: /rosapi/get_ros_version

        Returns:
            Dictionary with version and distro
            
        Example:
            get_ros_version() -> {'version': '2', 'distro': 'humble'}
        """
        import os

        # ROS 2 version is always "2"
        version = "2"

        # Get distro from environment variable
        distro = os.environ.get("ROS_DISTRO", "unknown")

        return {"version": version, "distro": distro}

    # ==================== Context Manager Support ====================

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
