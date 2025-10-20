# Solution Plan: Remove rosapi Dependency (Issue #145)

## Executive Summary

This document provides a complete solution plan for removing the dependency on `rosapi` (from `rosbridge_suite`) and implementing native ROS 2 APIs for graph and parameter management in the ros-mcp-server project.

**Status:** ✅ Planning Complete - Ready for Implementation

**Issue:** [#145](https://github.com/robotmcp/ros-mcp-server/issues/145)

---

## Problem Statement

Currently, the ros-mcp-server depends on `rosapi` (from `rosbridge_suite`) to retrieve information about ROS topics, services, nodes, and parameters. This introduces:

1. **Unnecessary dependency** on the rosbridge stack
2. **Added complexity** and overhead
3. **Misalignment** with native ROS 2 design principles
4. **Performance overhead** from WebSocket communication layer

---

## Proposed Solution

Replace rosapi with native ROS 2 APIs using `rclpy` (ROS 2 Python client library) directly in the MCP server.

### Architecture Change

**Before:**
```
MCP Server (Python)
    ↓ WebSocket
rosbridge_server
    ↓ Service Calls
rosapi (ROS Package)
    ↓ ROS 2 APIs
ROS 2 Graph/Parameters
```

**After:**
```
MCP Server (Python with rclpy)
    ↓ Direct API calls
ROS 2 Graph/Parameters
```

---

## Benefits

### Performance Improvements
- **5-10x faster** introspection operations (no WebSocket overhead)
- **Lower latency** for all graph queries
- **Real-time updates** via DDS discovery

### Architectural Simplification
- **Removes rosbridge dependency** (~50-100MB)
- **Simpler deployment** (one less package to install)
- **Fewer moving parts** (no WebSocket connection to maintain)

### Better Integration
- **Native ROS 2 design** using official APIs
- **Better error handling** and type safety
- **Direct DDS access** for discovery

---

## Implementation Approach

### Recommended: Pure rclpy Implementation

Use `rclpy` directly in the MCP server to interact with ROS 2.

**Why this approach?**
1. ✅ Simplest final architecture
2. ✅ Best performance
3. ✅ Complete removal of rosbridge
4. ✅ Native ROS 2 integration

**Trade-offs:**
- ⚠️ ROS 2 required on MCP server machine
- ⚠️ ROS 1 support dropped
- ⚠️ Breaking change (major version bump)

---

## Technical Details

### Key Components

#### 1. ROS2Manager Class
New utility class that wraps rclpy functionality:

```python
class ROS2Manager:
    """Manages ROS 2 node and provides native introspection APIs."""
    
    # Topic introspection
    def get_topics() -> Dict[str, List[str]]
    def get_topic_type(topic: str) -> str
    def get_publishers_for_topic(topic: str) -> List[str]
    def get_subscribers_for_topic(topic: str) -> List[str]
    
    # Service introspection
    def get_services() -> List[str]
    def get_service_type(service: str) -> str
    
    # Node introspection
    def get_nodes() -> List[str]
    def get_node_details(node_name: str) -> Dict
    
    # Type introspection
    def get_message_details(message_type: str) -> Dict
    def get_service_details(service_type: str) -> Dict
    
    # Parameters
    def get_parameter(node_name: str, param_name: str) -> Any
    def set_parameter(node_name: str, param_name: str, value: Any)
```

#### 2. Native ROS 2 APIs Used

| Current (rosapi) | Replacement (native ROS 2) |
|------------------|----------------------------|
| `/rosapi/topics` | `node.get_topic_names_and_types()` |
| `/rosapi/publishers` | `node.get_publishers_info_by_topic()` |
| `/rosapi/subscribers` | `node.get_subscriptions_info_by_topic()` |
| `/rosapi/services` | `node.get_service_names_and_types()` |
| `/rosapi/nodes` | `node.get_node_names()` |
| `/rosapi/message_details` | `rosidl_runtime_py.utilities.get_message()` |
| `/rosapi/service_*_details` | `rosidl_runtime_py.utilities.get_service()` |
| `/rosapi/get_param` | Native parameter service calls |

#### 3. Dependencies

**Add to pyproject.toml:**
```toml
dependencies = [
    # ... existing dependencies ...
    "rclpy>=3.0.0",  # ROS 2 Python client library
    "rosidl-runtime-py>=0.11.0",  # Message type introspection
]
```

**Remove:**
- `websocket-client` (if pub/sub also migrated)

---

## Implementation Timeline

### 8-Week Plan

| Week | Phase | Focus | Effort |
|------|-------|-------|--------|
| 1 | Setup | Infrastructure, ROS2Manager skeleton | 9 hours |
| 2 | Topics | Topic introspection APIs | 12 hours |
| 3 | Services | Service introspection APIs | 14 hours |
| 4 | Nodes | Node introspection APIs | 11 hours |
| 5 | Types | Message/service type details | 9 hours |
| 6 | Parameters | Parameter get/set/events | 12 hours |
| 7 | Pub/Sub (Optional) | Native publishers/subscribers | 16 hours |
| 8 | Testing & Release | Tests, docs, release | 20 hours |

**Total Effort:** 80-120 hours

---

## Migration Strategy

### Phase 1: Parallel Implementation
- Implement ROS2Manager alongside existing code
- Add feature flag to toggle between rosapi and native
- Test thoroughly with both implementations

### Phase 2: Gradual Migration
- Migrate one function at a time
- Keep rosbridge for pub/sub initially (hybrid approach)
- Extensive testing at each step

### Phase 3: Full Native (Optional)
- Replace pub/sub with native rclpy
- Remove rosbridge completely
- Final testing and optimization

### Phase 4: Release
- Update documentation
- Release as v3.0.0 (major version)
- Provide migration guide

---

## Risk Assessment

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Limited ROS 2 API functionality | High | Medium | Keep hybrid approach as fallback |
| Performance issues | Medium | Low | Benchmark early, optimize critical paths |
| Breaking changes for users | High | High | Major version bump, migration guide |
| ROS 2 installation complexity | Medium | Medium | Clear docs, Docker images |

---

## Success Criteria

The migration is successful when:

- ✅ All rosapi calls replaced with native ROS 2 APIs
- ✅ All MCP tools work correctly
- ✅ Performance equal or better than rosapi
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Examples work correctly
- ✅ No dependency on rosbridge for introspection

---

## Documentation Deliverables

### Created Documents

1. **`docs/native_ros2_migration.md`**
   - Complete migration guide
   - Architecture diagrams
   - Full ROS2Manager implementation example
   - Testing strategy

2. **`utils/ros2_manager.py`**
   - Prototype implementation
   - Fully documented methods
   - Ready for testing

3. **`docs/rosapi_comparison.md`**
   - Side-by-side API comparison
   - Performance benchmarks
   - Feature parity matrix

4. **`docs/implementation_roadmap.md`**
   - Detailed 8-week plan
   - Task-by-task breakdown
   - Effort estimates
   - Risk mitigation

---

## Getting Started

### For Implementers

1. **Review documents:**
   - Start with this summary
   - Read `docs/native_ros2_migration.md`
   - Review `docs/implementation_roadmap.md`

2. **Set up environment:**
   - Install ROS 2 (Humble or newer)
   - Install rclpy and rosidl_runtime_py
   - Set up test environment

3. **Begin implementation:**
   - Start with Phase 1 (Week 1)
   - Follow roadmap checklist
   - Test incrementally

### For Reviewers

1. **Understand scope:**
   - Review this summary
   - Check `docs/rosapi_comparison.md` for technical details

2. **Evaluate approach:**
   - Is pure rclpy the right choice?
   - Are risks acceptable?
   - Is timeline realistic?

3. **Provide feedback:**
   - Comment on GitHub issue #145
   - Suggest improvements
   - Flag concerns

---

## Alternative Approaches Considered

### Option A: Hybrid Approach
Keep rosbridge for pub/sub, use native for introspection.

**Pros:** Lower risk, incremental migration  
**Cons:** Still depends on rosbridge, more complex

**Verdict:** Good intermediate step, not ideal end state

### Option B: Pure rclpy (Recommended)
Replace everything with native ROS 2.

**Pros:** Cleanest architecture, best performance  
**Cons:** More work, requires ROS 2 on server

**Verdict:** ✅ Recommended for long-term

### Option C: Separate ROS Node with IPC
Create separate node, communicate via IPC.

**Pros:** Separation of concerns  
**Cons:** Most complex, additional overhead

**Verdict:** ❌ Not recommended, adds complexity

---

## Breaking Changes

### For Users

**Required:**
- ROS 2 installation on MCP server machine
- No longer need rosbridge_server

**Impact:**
- ROS 1 users cannot upgrade (stay on v2.x)
- New installation requirements
- Simpler robot-side setup

**Migration Path:**
1. Install ROS 2 on MCP server machine
2. Upgrade ros-mcp-server to v3.0.0
3. Remove rosbridge_server from robot (optional)
4. Update configuration

---

## Performance Expectations

### Expected Improvements

| Operation | Current | After | Improvement |
|-----------|---------|-------|-------------|
| Get Topics | 50-100ms | 5-10ms | **5-10x** |
| Get Topic Type | 50-100ms | 5-10ms | **5-10x** |
| Get Publishers | 50-100ms | 10-20ms | **3-5x** |
| Get Message Details | 100-200ms | 20-30ms | **5-7x** |
| Get Services | 50-100ms | 5-10ms | **5-10x** |
| Get Nodes | 50-100ms | 5-10ms | **5-10x** |

### Resource Savings

- **Memory:** ~50-100MB saved (no rosbridge)
- **CPU:** Lower (no WebSocket processing)
- **Network:** DDS only (no WebSocket connection)

---

## Next Steps

### Immediate Actions

1. **Review & Approve**
   - Team review of this plan
   - Community feedback on GitHub
   - Decision on approach

2. **Prepare Environment**
   - Set up ROS 2 dev environment
   - Install dependencies
   - Prepare test systems

3. **Start Implementation**
   - Begin Phase 1 (Week 1)
   - Create feature branch
   - Regular progress updates

### Future Considerations

- Support for ROS 2 Actions
- Permission controls
- Multiple simultaneous connections
- Advanced parameter management

---

## Questions & Answers

### Q: Can we keep ROS 1 support?
**A:** Not with this approach. Native ROS 2 APIs are fundamentally different. ROS 1 users should stay on v2.x.

### Q: Do we have to migrate pub/sub too?
**A:** No, Phase 7 (pub/sub) is optional. Can keep rosbridge for that initially.

### Q: What if ROS 2 APIs are insufficient?
**A:** Hybrid approach available as fallback. Some features may have limitations.

### Q: When will this be released?
**A:** Target: 8 weeks after implementation starts. Will be v3.0.0 (major version).

### Q: How can I help?
**A:** Test prototype, provide feedback on issue #145, help with implementation!

---

## References

- **Issue:** https://github.com/robotmcp/ros-mcp-server/issues/145
- **ROS 2 Documentation:** https://docs.ros.org/
- **rclpy API:** https://docs.ros2.org/latest/api/rclpy/
- **rosidl_runtime_py:** https://github.com/ros2/rosidl_runtime_py

---

## Contact

For questions or feedback:
- Open discussion on GitHub issue #145
- Contact project maintainers
- Join ROS Discourse

---

**Document Version:** 1.0  
**Created:** 2025-10-20  
**Status:** ✅ Complete and Ready for Implementation  
**Next Review:** After Phase 2 completion
