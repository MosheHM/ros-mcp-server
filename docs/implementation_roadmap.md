# Implementation Roadmap: Remove rosapi Dependency

This document provides a detailed, actionable roadmap for implementing native ROS 2 APIs to replace the rosapi dependency.

## Executive Summary

**Goal:** Remove dependency on rosbridge_suite/rosapi and use native ROS 2 APIs

**Timeline:** 6-8 weeks

**Effort:** ~80-120 hours

**Risk Level:** Medium (requires careful testing)

**Impact:** Major version release (3.0.0)

---

## Prerequisites

Before starting implementation, ensure:

- [ ] ROS 2 development environment (Humble or newer recommended)
- [ ] Understanding of rclpy and ROS 2 Python APIs
- [ ] Test robot/simulation environment for validation
- [ ] Backup of current working implementation

---

## Phase 1: Setup and Infrastructure (Week 1)

### Task 1.1: Development Environment Setup
**Effort:** 2 hours

- [ ] Install ROS 2 (Humble or Jazzy recommended)
- [ ] Install rclpy: `sudo apt install ros-${ROS_DISTRO}-rclpy`
- [ ] Install rosidl_runtime_py: `sudo apt install ros-${ROS_DISTRO}-rosidl-runtime-py`
- [ ] Set up test environment (turtlesim or simple robot)
- [ ] Verify ROS 2 APIs work in Python

**Validation:**
```bash
python3 -c "import rclpy; print('rclpy OK')"
python3 -c "from rosidl_runtime_py.utilities import get_message; print('rosidl OK')"
```

### Task 1.2: Update Dependencies
**Effort:** 1 hour

- [ ] Add rclpy to `pyproject.toml`
- [ ] Add rosidl_runtime_py to `pyproject.toml`
- [ ] Update README with new requirements
- [ ] Test installation with `uv sync`

**Files to modify:**
- `pyproject.toml`
- `README.md`
- `docs/installation.md`

### Task 1.3: Create ROS2Manager Module
**Effort:** 4 hours

- [ ] Copy prototype `utils/ros2_manager.py` to project
- [ ] Add proper error handling
- [ ] Add logging
- [ ] Write docstrings
- [ ] Add type hints

**Deliverable:** `utils/ros2_manager.py` with basic structure

### Task 1.4: Add Configuration Flag
**Effort:** 2 hours

- [ ] Add `USE_NATIVE_ROS2` environment variable
- [ ] Add configuration to `server.py`
- [ ] Support toggling between rosapi and native
- [ ] Default to rosapi for backward compatibility

**Files to modify:**
- `server.py`

**Example:**
```python
USE_NATIVE_ROS2 = os.getenv("USE_NATIVE_ROS2", "false").lower() == "true"

if USE_NATIVE_ROS2:
    ros2_manager = ROS2Manager()
else:
    ws_manager = WebSocketManager(...)
```

---

## Phase 2: Implement Topic Introspection (Week 2)

### Task 2.1: Implement get_topics()
**Effort:** 3 hours

- [ ] Implement `ROS2Manager.get_topics()`
- [ ] Update `server.py` `get_topics()` to use ROS2Manager
- [ ] Add error handling
- [ ] Test with turtlesim

**Test:**
```bash
export USE_NATIVE_ROS2=true
ros2 run turtlesim turtlesim_node  # Terminal 1
python server.py  # Terminal 2
# Test get_topics() tool
```

### Task 2.2: Implement get_topic_type()
**Effort:** 2 hours

- [ ] Implement `ROS2Manager.get_topic_type()`
- [ ] Update `server.py` `get_topic_type()`
- [ ] Test with various topics

### Task 2.3: Implement get_publishers_for_topic()
**Effort:** 2 hours

- [ ] Implement `ROS2Manager.get_publishers_for_topic()`
- [ ] Update `server.py` `get_publishers_for_topic()`
- [ ] Test with multiple publishers

### Task 2.4: Implement get_subscribers_for_topic()
**Effort:** 2 hours

- [ ] Implement `ROS2Manager.get_subscribers_for_topic()`
- [ ] Update `server.py` `get_subscribers_for_topic()`
- [ ] Test with multiple subscribers

### Task 2.5: Update inspect_all_topics()
**Effort:** 3 hours

- [ ] Update `inspect_all_topics()` to use ROS2Manager
- [ ] Optimize for performance
- [ ] Test with large topic lists

---

## Phase 3: Implement Service Introspection (Week 3)

### Task 3.1: Implement get_services()
**Effort:** 2 hours

- [ ] Implement `ROS2Manager.get_services()`
- [ ] Update `server.py` `get_services()`
- [ ] Test with various services

### Task 3.2: Implement get_service_type()
**Effort:** 2 hours

- [ ] Implement `ROS2Manager.get_service_type()`
- [ ] Update `server.py` `get_service_type()`
- [ ] Test with different service types

### Task 3.3: Implement get_service_providers()
**Effort:** 3 hours

- [ ] Research ROS 2 service provider discovery
- [ ] Implement workaround (may be limited)
- [ ] Update `server.py` `get_service_providers()`
- [ ] Document limitations

### Task 3.4: Implement get_service_details()
**Effort:** 4 hours

- [ ] Use rosidl_runtime_py for introspection
- [ ] Implement request/response structure parsing
- [ ] Update `server.py` `get_service_details()`
- [ ] Test with various service types

### Task 3.5: Update inspect_all_services()
**Effort:** 3 hours

- [ ] Update `inspect_all_services()` to use ROS2Manager
- [ ] Optimize for performance
- [ ] Test with many services

---

## Phase 4: Implement Node Introspection (Week 4)

### Task 4.1: Implement get_nodes()
**Effort:** 2 hours

- [ ] Implement `ROS2Manager.get_nodes()`
- [ ] Update `server.py` `get_nodes()`
- [ ] Test with multiple nodes

### Task 4.2: Implement get_node_details()
**Effort:** 6 hours

- [ ] Implement topic aggregation logic
- [ ] Handle service discovery limitation
- [ ] Update `server.py` `get_node_details()`
- [ ] Test with various nodes
- [ ] Document limitations

### Task 4.3: Update inspect_all_nodes()
**Effort:** 3 hours

- [ ] Update `inspect_all_nodes()` to use ROS2Manager
- [ ] Optimize for performance
- [ ] Test with many nodes

---

## Phase 5: Implement Type Introspection (Week 5)

### Task 5.1: Implement get_message_details()
**Effort:** 4 hours

- [ ] Use rosidl_runtime_py.utilities.get_message
- [ ] Parse field types recursively
- [ ] Update `server.py` `get_message_details()`
- [ ] Test with standard and custom messages

### Task 5.2: Implement get_service_details()
**Effort:** 4 hours

- [ ] Use rosidl_runtime_py.utilities.get_service
- [ ] Parse request and response structures
- [ ] Handle nested types
- [ ] Test thoroughly

### Task 5.3: Implement ROS Version Detection
**Effort:** 1 hour

- [ ] Implement `ROS2Manager.get_ros_version()`
- [ ] Update `server.py` `detect_ros_version()`
- [ ] Test version detection

---

## Phase 6: Parameter Management (Week 6)

### Task 6.1: Implement Parameter Get/Set
**Effort:** 6 hours

- [ ] Implement `ROS2Manager.get_parameter()`
- [ ] Implement `ROS2Manager.set_parameter()`
- [ ] Implement `ROS2Manager.list_parameters()`
- [ ] Handle different parameter types
- [ ] Test with various nodes

### Task 6.2: Implement Parameter Events
**Effort:** 4 hours

- [ ] Subscribe to `/parameter_events`
- [ ] Implement parameter change notifications
- [ ] Add callback mechanism
- [ ] Test parameter updates

### Task 6.3: Add Parameter Tools
**Effort:** 2 hours

- [ ] Add MCP tools for parameter operations
- [ ] Update documentation
- [ ] Test parameter management

---

## Phase 7: Pub/Sub Implementation (Optional - Week 7)

**Note:** This phase is optional. Can keep rosbridge for pub/sub initially.

### Task 7.1: Implement Native Publishers
**Effort:** 6 hours

- [ ] Implement `ROS2Manager.create_publisher()`
- [ ] Implement `ROS2Manager.publish_message()`
- [ ] Handle message construction from dict
- [ ] Update `publish_once()` in server.py
- [ ] Test with various message types

### Task 7.2: Implement Native Subscribers
**Effort:** 6 hours

- [ ] Implement `ROS2Manager.create_subscription()`
- [ ] Implement message collection mechanism
- [ ] Update `subscribe_once()` in server.py
- [ ] Update `subscribe_for_duration()` in server.py
- [ ] Test subscription functionality

### Task 7.3: Implement Service Calls
**Effort:** 4 hours

- [ ] Implement `ROS2Manager.call_service()`
- [ ] Handle request/response parsing
- [ ] Update `call_service()` in server.py
- [ ] Test with various services

---

## Phase 8: Testing and Validation (Week 8)

### Task 8.1: Unit Tests
**Effort:** 8 hours

- [ ] Write tests for ROS2Manager methods
- [ ] Test error handling
- [ ] Test edge cases
- [ ] Achieve >80% code coverage

### Task 8.2: Integration Tests
**Effort:** 8 hours

- [ ] Test with turtlesim
- [ ] Test with real robot (if available)
- [ ] Test with simulation (Gazebo/Isaac Sim)
- [ ] Test all MCP tools end-to-end

### Task 8.3: Performance Testing
**Effort:** 4 hours

- [ ] Benchmark native vs rosapi
- [ ] Measure latency improvements
- [ ] Test with large graphs (100+ nodes)
- [ ] Document performance gains

### Task 8.4: Regression Testing
**Effort:** 4 hours

- [ ] Ensure existing functionality works
- [ ] Test backward compatibility mode
- [ ] Verify examples still work
- [ ] Test error scenarios

---

## Phase 9: Documentation (Week 8)

### Task 9.1: Update Installation Guide
**Effort:** 2 hours

- [ ] Remove rosbridge installation steps
- [ ] Add ROS 2 installation requirements
- [ ] Update configuration instructions
- [ ] Add troubleshooting section

**Files to modify:**
- `docs/installation.md`
- `README.md`

### Task 9.2: Write Migration Guide
**Effort:** 3 hours

- [ ] Create migration guide for users
- [ ] Document breaking changes
- [ ] Provide upgrade path
- [ ] Add FAQ section

**New file:** `docs/migration_to_v3.md`

### Task 9.3: Update Examples
**Effort:** 4 hours

- [ ] Update example code
- [ ] Test all examples
- [ ] Update example documentation
- [ ] Add native ROS 2 specific examples

### Task 9.4: Update API Documentation
**Effort:** 2 hours

- [ ] Document new ROS2Manager API
- [ ] Update tool descriptions
- [ ] Add code examples
- [ ] Document limitations

---

## Phase 10: Cleanup and Release (Week 8)

### Task 10.1: Code Cleanup
**Effort:** 4 hours

- [ ] Remove old rosapi code (if fully migrated)
- [ ] Remove WebSocketManager (if not needed)
- [ ] Clean up imports
- [ ] Format code with ruff
- [ ] Remove debug code

### Task 10.2: Dependency Cleanup
**Effort:** 1 hour

- [ ] Remove websocket-client from dependencies
- [ ] Update pyproject.toml
- [ ] Test clean installation

### Task 10.3: Version Update
**Effort:** 1 hour

- [ ] Update version to 3.0.0
- [ ] Update CHANGELOG
- [ ] Tag release
- [ ] Update package metadata

### Task 10.4: Release
**Effort:** 2 hours

- [ ] Create release branch
- [ ] Run final tests
- [ ] Build package
- [ ] Publish to PyPI
- [ ] Announce release

---

## Success Criteria

The migration is complete when:

- ✅ All rosapi service calls are replaced with native ROS 2 APIs
- ✅ All MCP tools work with native implementation
- ✅ Performance is equal or better than rosapi
- ✅ All tests pass
- ✅ Documentation is updated
- ✅ Examples work correctly
- ✅ No dependency on rosbridge_server (for introspection)

---

## Risk Mitigation

### Risk 1: Limited ROS 2 API Functionality
**Impact:** High  
**Probability:** Medium

**Mitigation:**
- Research ROS 2 APIs thoroughly before starting
- Identify limitations early
- Document workarounds
- Keep hybrid approach as fallback

### Risk 2: Performance Degradation
**Impact:** Medium  
**Probability:** Low

**Mitigation:**
- Benchmark early and often
- Optimize critical paths
- Use caching where appropriate
- Profile code

### Risk 3: Breaking Changes
**Impact:** High  
**Probability:** High

**Mitigation:**
- Major version bump (3.0.0)
- Provide migration guide
- Support backward compatibility mode temporarily
- Communicate changes clearly

### Risk 4: ROS 2 Installation Complexity
**Impact:** Medium  
**Probability:** Medium

**Mitigation:**
- Provide clear installation instructions
- Consider Docker images
- Document common issues
- Provide alternative installation methods

---

## Communication Plan

### Stakeholders
- Users of ros-mcp-server
- Contributors
- ROS community

### Communication Timeline

**Week 1:**
- [ ] Create GitHub issue for tracking
- [ ] Post roadmap to discussions
- [ ] Solicit feedback

**Week 4:**
- [ ] Progress update
- [ ] Beta release for testing
- [ ] Request community testing

**Week 7:**
- [ ] Release candidate
- [ ] Final testing period
- [ ] Documentation review

**Week 8:**
- [ ] Release announcement
- [ ] Update README
- [ ] Post to ROS Discourse

---

## Resources Needed

### Development Tools
- ROS 2 Humble or newer
- Python 3.10+
- Test robot or simulation
- Development machine with ROS 2

### Documentation
- ROS 2 API documentation
- rclpy documentation
- rosidl_runtime_py documentation

### Testing Resources
- Multiple ROS 2 systems for testing
- Various robots/simulations
- CI/CD pipeline

---

## Contingency Plan

If issues arise during implementation:

1. **Plan A:** Continue with hybrid approach
   - Keep rosbridge for problematic areas
   - Use native for what works

2. **Plan B:** Delay full migration
   - Release partial migration as 2.5.0
   - Continue using rosapi where necessary

3. **Plan C:** Revert to rosapi
   - If native approach proves infeasible
   - Keep improvements made
   - Document lessons learned

---

## Next Steps

1. **Review this roadmap** with team/community
2. **Get approval** for approach
3. **Set up development environment**
4. **Start Phase 1** implementation
5. **Track progress** weekly
6. **Adjust timeline** as needed

---

## Progress Tracking

Use GitHub project board or issue tracker:

- [ ] Phase 1: Setup (Week 1)
- [ ] Phase 2: Topics (Week 2)
- [ ] Phase 3: Services (Week 3)
- [ ] Phase 4: Nodes (Week 4)
- [ ] Phase 5: Types (Week 5)
- [ ] Phase 6: Parameters (Week 6)
- [ ] Phase 7: Pub/Sub (Week 7)
- [ ] Phase 8: Testing (Week 8)
- [ ] Phase 9: Documentation (Week 8)
- [ ] Phase 10: Release (Week 8)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-20  
**Owner:** ros-mcp-server maintainers
