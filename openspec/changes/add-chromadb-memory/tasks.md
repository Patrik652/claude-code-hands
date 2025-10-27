# Tasks: ChromaDB Vector Memory Implementation

## Phase 1: Foundation & Core Storage (Days 1-2)

### 1.1 Environment Setup
- [ ] Add ChromaDB to requirements: `chromadb>=0.4.22`
- [ ] Add sentence-transformers: `sentence-transformers>=2.2.2`
- [ ] Create `mcp-servers/memory/` module directory structure
- [ ] Add `__init__.py` files for Python package structure
- [ ] Create `config/memory_config.yaml` with default configuration

**Success Criteria**: Dependencies install cleanly, directory structure created

**Dependencies**: None (first task)

---

### 1.2 Configuration Schema
- [ ] Create `memory/config.py` with Pydantic models for configuration
- [ ] Implement `MemoryConfig` class with validation
- [ ] Support environment variable overrides (MEMORY_STORAGE_PATH, etc.)
- [ ] Add config loading function with fallback to defaults
- [ ] Write unit tests for config validation

**Success Criteria**: Config loads correctly, validates invalid values, env vars override works

**Dependencies**: 1.1 complete

---

### 1.3 ChromaDB Client Initialization
- [ ] Create `memory/storage.py` with `ChromaDBStorage` class
- [ ] Implement lazy initialization of ChromaDB persistent client
- [ ] Create three collections: `screen_memories`, `action_memories`, `workflow_memories`
- [ ] Configure HNSW index parameters for performance
- [ ] Add error handling for initialization failures (permissions, corruption)
- [ ] Write unit tests with in-memory ChromaDB for speed

**Success Criteria**: ChromaDB initializes on first use, creates collections, handles errors gracefully

**Dependencies**: 1.2 complete

---

### 1.4 Embedding Engine
- [ ] Create `memory/embeddings.py` with `EmbeddingEngine` class
- [ ] Integrate sentence-transformers `all-MiniLM-L6-v2` model
- [ ] Implement embedding generation for text content
- [ ] Add LRU cache for embedding reuse (1000 item cache)
- [ ] Support CPU and GPU inference (auto-detect)
- [ ] Handle model download with progress logging
- [ ] Write tests for embedding generation and caching

**Success Criteria**: Embeddings generated in <100ms (CPU), cache hit rate >70% in tests

**Dependencies**: 1.1 complete (parallel with 1.3)

---

### 1.5 Memory Data Models
- [ ] Create `memory/models.py` with Pydantic data models
- [ ] Define `Memory` base class with common fields (id, timestamp, type, metadata)
- [ ] Define `ScreenMemory`, `ActionMemory`, `WorkflowMemory` subclasses
- [ ] Implement `to_dict()` and `from_dict()` serialization methods
- [ ] Add `generate_id()` helper for unique memory IDs
- [ ] Write tests for model validation and serialization

**Success Criteria**: Models serialize/deserialize correctly, ID generation is unique

**Dependencies**: 1.2 complete

---

### 1.6 Core Storage Operations
- [ ] Implement `MemoryStorage.store_memory(content, type, metadata)` method
- [ ] Implement `MemoryStorage.get_memory(memory_id)` retrieval
- [ ] Implement `MemoryStorage.delete_memory(memory_id)` deletion
- [ ] Implement `MemoryStorage.get_stats()` for usage statistics
- [ ] Add async wrappers for non-blocking operations
- [ ] Write integration tests with real ChromaDB (test database)

**Success Criteria**: Store/retrieve/delete work correctly, stats report accurate counts

**Dependencies**: 1.3, 1.4, 1.5 complete

---

## Phase 2: Semantic Search (Days 3-4)

### 2.1 Basic Vector Search
- [ ] Implement `MemoryStorage.search_memories(query, limit)` method
- [ ] Generate query embedding using embedding engine
- [ ] Perform cosine similarity search via ChromaDB
- [ ] Return results with similarity scores ranked by relevance
- [ ] Write tests for search accuracy and performance (<50ms target)

**Success Criteria**: Search finds semantically similar memories, returns in <50ms for 1000 items

**Dependencies**: Phase 1 complete

---

### 2.2 Metadata Filtering
- [ ] Extend search to support metadata filters (date range, type, success status)
- [ ] Implement filter translation to ChromaDB where clause
- [ ] Support AND logic for multiple filters
- [ ] Test complex filter combinations
- [ ] Validate filter performance impact

**Success Criteria**: Filtered searches return correct subset, filters combine properly

**Dependencies**: 2.1 complete

---

### 2.3 Multi-Collection Search
- [ ] Implement parallel search across multiple collections
- [ ] Merge results from different memory types
- [ ] Maintain ranking consistency across collections
- [ ] Add `memory_types` parameter to filter collections
- [ ] Test search performance with 3 collections in parallel

**Success Criteria**: Multi-collection search works, latency ≈ single collection (parallel execution)

**Dependencies**: 2.1 complete (parallel with 2.2)

---

### 2.4 Pagination Support
- [ ] Add `offset` and `limit` parameters to search
- [ ] Return total result count with paginated results
- [ ] Ensure consistent ordering across pages
- [ ] Handle edge cases (offset > total, negative values)
- [ ] Write tests for pagination edge cases

**Success Criteria**: Pagination works correctly, edge cases handled gracefully

**Dependencies**: 2.1 complete

---

### 2.5 Fuzzy Fallback Search
- [ ] Implement keyword-based text search as fallback
- [ ] Detect when embeddings unavailable (model load failure)
- [ ] Automatically fall back to text matching
- [ ] Log warning when using degraded search
- [ ] Test fallback behavior

**Success Criteria**: System works without embeddings (degraded mode), clear warnings logged

**Dependencies**: 2.1 complete

---

### 2.6 Search Performance Optimization
- [ ] Implement query result caching (5 minute TTL)
- [ ] Add embedding cache for frequent queries
- [ ] Benchmark search latency with 10,000 memories
- [ ] Tune HNSW parameters if needed (M, ef_search)
- [ ] Document performance characteristics

**Success Criteria**: 10,000 memory search completes in <100ms, cache hit rate >50%

**Dependencies**: 2.1 complete

---

## Phase 3: Context Persistence & Auto-Capture (Days 5-6)

### 3.1 Memory Manager Orchestrator
- [ ] Create `memory/manager.py` with `MemoryManager` class
- [ ] Combine storage, embeddings, and search into unified interface
- [ ] Implement session tracking (generate session IDs)
- [ ] Add memory manager initialization in integration-mcp
- [ ] Write tests for manager orchestration

**Success Criteria**: Manager provides clean API for all memory operations

**Dependencies**: Phase 1 & 2 complete

---

### 3.2 Auto-Capture Configuration
- [ ] Extend `memory_config.yaml` with auto_capture settings
- [ ] Implement trigger configuration (ai_analysis, successful_actions, etc.)
- [ ] Add filters (min_interval, ignore_mouse_moves, etc.)
- [ ] Implement privacy exclusion patterns
- [ ] Test configuration loading and validation

**Success Criteria**: Auto-capture config loads, privacy exclusions work

**Dependencies**: 1.2 complete, 3.1 complete

---

### 3.3 Vision MCP Integration
- [ ] Add memory manager instance to vision-mcp server
- [ ] Hook `analyze_screen_ai()` to auto-store memories
- [ ] Include AI provider, prompt, result, screen text in metadata
- [ ] Implement async storage (non-blocking)
- [ ] Test auto-capture doesn't slow down AI analysis

**Success Criteria**: Screen analyses auto-captured, no performance impact (<5ms overhead)

**Dependencies**: 3.1, 3.2 complete

---

### 3.4 Hands MCP Integration
- [ ] Add memory manager to hands-mcp server
- [ ] Hook `mouse_click()`, `mouse_move()`, `keyboard_type()` for auto-capture
- [ ] Store action type, parameters, success/failure in metadata
- [ ] Respect interval filters (don't capture repetitive actions)
- [ ] Test action capture with real automation

**Success Criteria**: Actions auto-captured with proper filtering, no duplicate noise

**Dependencies**: 3.1, 3.2 complete (parallel with 3.3)

---

### 3.5 Browser MCP Integration
- [ ] Add memory manager to browser-mcp
- [ ] Hook workflow execution for auto-capture
- [ ] Store workflow name, steps, duration, ARIA tree context
- [ ] Capture both successful and failed workflows
- [ ] Test workflow memory creation

**Success Criteria**: Workflows auto-captured with full execution context

**Dependencies**: 3.1, 3.2 complete (parallel with 3.3, 3.4)

---

### 3.6 Manual Memory Tools
- [ ] Implement `memory_store()` MCP tool in integration-mcp
- [ ] Add support for custom metadata and bookmarking
- [ ] Implement screenshot attachment handling
- [ ] Write usage examples for documentation
- [ ] Test manual storage with various metadata

**Success Criteria**: Users can manually store important memories with rich metadata

**Dependencies**: 3.1 complete

---

## Phase 4: MCP Tools & User Interface (Day 7)

### 4.1 Search MCP Tool
- [ ] Implement `memory_search()` MCP tool
- [ ] Support all search parameters (query, types, filters, limit, offset)
- [ ] Format results for user-friendly display
- [ ] Add similarity score threshold parameter
- [ ] Test with various search scenarios

**Success Criteria**: Search tool works from Claude Code, results are actionable

**Dependencies**: Phase 2 complete, 3.1 complete

---

### 4.2 Retrieval & Deletion Tools
- [ ] Implement `memory_get(memory_id)` tool for retrieval by ID
- [ ] Implement `memory_delete(memory_id)` tool for deletion
- [ ] Add confirmation for sensitive deletions
- [ ] Return helpful errors for missing memories
- [ ] Test edge cases

**Success Criteria**: Retrieval and deletion work reliably, good error messages

**Dependencies**: 3.1 complete

---

### 4.3 Statistics & Insights Tool
- [ ] Implement `memory_stats()` MCP tool
- [ ] Report counts by memory type, storage usage, performance metrics
- [ ] Add top frequent actions/screens
- [ ] Calculate and display cache hit rates
- [ ] Test stats calculation performance

**Success Criteria**: Stats provide comprehensive overview, calculate in <100ms

**Dependencies**: 3.1 complete

---

### 4.4 Session Management Tools
- [ ] Implement `memory_list_sessions()` to show all sessions
- [ ] Implement `memory_resume_session(session_id)` for context switching
- [ ] Implement `memory_delete_session(session_id)` for session cleanup
- [ ] Add session metadata (start/end time, memory count, summary)
- [ ] Test session isolation and switching

**Success Criteria**: Session tools enable workflow continuity across restarts

**Dependencies**: 3.1 complete

---

### 4.5 Backup & Recovery Tools
- [ ] Implement `memory_backup(name)` for manual backups
- [ ] Implement `memory_restore(backup_path)` for restoration
- [ ] Add automatic backup before dangerous operations
- [ ] Implement backup rotation (keep last 5)
- [ ] Test backup/restore integrity

**Success Criteria**: Backups work reliably, restoration recovers all data

**Dependencies**: 3.1 complete (parallel with 4.1-4.4)

---

## Phase 5: Retention & Cleanup (Day 8)

### 5.1 Retention Policy Engine
- [ ] Create `memory/retention.py` with `RetentionPolicy` class
- [ ] Implement age-based retention (delete older than N days)
- [ ] Implement size-based retention (max items per collection)
- [ ] Respect bookmarked/flagged memories (never delete)
- [ ] Write tests for retention logic

**Success Criteria**: Retention policies enforce limits correctly, protect important memories

**Dependencies**: 3.1 complete

---

### 5.2 Deduplication Algorithm
- [ ] Implement duplicate detection (>95% similarity)
- [ ] Create clusters of near-duplicate memories
- [ ] Keep one representative per cluster, delete rest
- [ ] Add `find_duplicates()` method for user inspection
- [ ] Test deduplication accuracy

**Success Criteria**: Duplicates detected accurately, deduplication saves storage

**Dependencies**: Phase 2 complete, 5.1 complete

---

### 5.3 Automated Cleanup Scheduler
- [ ] Implement cleanup scheduler (daily at 3 AM default)
- [ ] Run retention policies automatically
- [ ] Run deduplication automatically
- [ ] Log cleanup statistics (items deleted, space freed)
- [ ] Add manual trigger via `memory_cleanup()` tool

**Success Criteria**: Auto-cleanup runs on schedule, reports results, can be triggered manually

**Dependencies**: 5.1, 5.2 complete

---

### 5.4 Storage Quota Enforcement
- [ ] Check storage quota before adding new memories
- [ ] Trigger cleanup when approaching limit (>90%)
- [ ] Rank memories by importance (bookmarked > manual > auto)
- [ ] Delete least important when at quota
- [ ] Test quota enforcement logic

**Success Criteria**: Storage stays within quota, important memories preserved

**Dependencies**: 5.1 complete

---

## Phase 6: Testing & Documentation (Day 9)

### 6.1 Integration Test Suite
- [ ] Write E2E test for full memory workflow (store → search → retrieve → delete)
- [ ] Test auto-capture from all three MCP servers
- [ ] Test multi-session scenarios
- [ ] Test retention and cleanup workflows
- [ ] Test backup and restore

**Success Criteria**: All integration tests pass, >80% code coverage

**Dependencies**: All phases complete

---

### 6.2 Performance Benchmarks
- [ ] Benchmark storage latency (target <10ms)
- [ ] Benchmark search latency (target <50ms for 1000 items, <100ms for 10K)
- [ ] Benchmark embedding generation (target <100ms CPU)
- [ ] Benchmark cleanup operations (target <5s for 10K items)
- [ ] Document performance characteristics

**Success Criteria**: All performance targets met, benchmarks documented

**Dependencies**: All phases complete

---

### 6.3 User Documentation
- [ ] Write memory system overview in README
- [ ] Document all MCP tools with examples
- [ ] Create configuration reference guide
- [ ] Write troubleshooting guide
- [ ] Add privacy and security considerations

**Success Criteria**: Complete documentation enables users to use memory features effectively

**Dependencies**: All phases complete

---

### 6.4 Example Workflows
- [ ] Create example: "Resume automation from yesterday"
- [ ] Create example: "Find all successful login automations"
- [ ] Create example: "Analyze automation success patterns"
- [ ] Create example: "Clean up old test session memories"
- [ ] Add examples to documentation

**Success Criteria**: Examples demonstrate real-world usage, run successfully

**Dependencies**: 6.3 in progress

---

## Phase 7: Polish & Production Readiness (Day 10)

### 7.1 Error Handling Review
- [ ] Review all error paths for user-friendly messages
- [ ] Add fallback behavior for common failures
- [ ] Ensure no exceptions crash MCP servers
- [ ] Test error scenarios (disk full, permissions, corruption)
- [ ] Document error codes and recovery steps

**Success Criteria**: All errors handled gracefully, clear messages, no crashes

**Dependencies**: All core functionality complete

---

### 7.2 Privacy & Security Audit
- [ ] Review data stored in memories for PII concerns
- [ ] Implement screenshot redaction if configured
- [ ] Test privacy exclusion patterns
- [ ] Ensure local-only storage (no cloud leaks)
- [ ] Document privacy controls

**Success Criteria**: Privacy features work, no unintended data leaks

**Dependencies**: All core functionality complete

---

### 7.3 Migration Guide
- [ ] Document how to enable memory on existing installation
- [ ] Create migration script if needed
- [ ] Test upgrade path from memory-disabled to enabled
- [ ] Document rollback procedure
- [ ] Test backward compatibility

**Success Criteria**: Users can enable memory without breaking existing setup

**Dependencies**: 7.1 complete

---

### 7.4 Final Validation
- [ ] Run full test suite (unit + integration + E2E)
- [ ] Validate OpenSpec with `openspec validate add-chromadb-memory --strict`
- [ ] Test on fresh installation (clean environment)
- [ ] Test on existing installation (upgrade scenario)
- [ ] Performance regression check

**Success Criteria**: All tests pass, OpenSpec validates, no regressions

**Dependencies**: All previous tasks complete

---

## Summary

**Total Tasks**: 52 tasks across 7 phases
**Estimated Duration**: 10 days (5-7 days with focused effort)
**Parallelizable Work**:
- Phase 1: Tasks 1.3 and 1.4 can run in parallel
- Phase 2: Tasks 2.2 and 2.3 can run in parallel
- Phase 3: Tasks 3.3, 3.4, 3.5 can run in parallel
- Phase 4: Tasks 4.1-4.5 can run in parallel

**Critical Path**:
1. Foundation (1.1 → 1.2 → 1.3 → 1.6) - 2 days
2. Search (2.1 → 2.6) - 2 days
3. Auto-Capture (3.1 → 3.2 → 3.3/3.4/3.5) - 2 days
4. MCP Tools (4.1-4.5) - 1 day
5. Retention (5.1 → 5.4) - 1 day
6. Testing & Docs (6.1 → 6.4) - 1 day
7. Polish (7.1 → 7.4) - 1 day

**Deliverables**:
- Working ChromaDB vector memory system
- 5+ MCP tools for memory operations
- Auto-capture from vision/hands/browser MCPs
- Comprehensive test suite (unit + integration + E2E)
- Complete documentation and examples
- Performance benchmarks and optimization

**Success Metrics**:
- ✅ All 52 tasks completed
- ✅ Test coverage >80%
- ✅ All performance targets met (<10ms store, <50ms search)
- ✅ OpenSpec validation passes
- ✅ Zero backward compatibility breaks
- ✅ User documentation complete
