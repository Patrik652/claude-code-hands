# Design: ChromaDB Vector Memory Integration

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Servers Layer                        │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │ Vision MCP │  │ Hands MCP  │  │   Browser MCP       │   │
│  └──────┬─────┘  └──────┬─────┘  └──────────┬──────────┘   │
│         │                │                    │               │
│         └────────────────┴────────────────────┘               │
│                          │                                    │
│                ┌─────────▼──────────┐                        │
│                │   Memory Manager    │                        │
│                │  (New Component)    │                        │
│                └─────────┬──────────┘                        │
│                          │                                    │
│         ┌────────────────┼────────────────┐                  │
│         │                │                │                  │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐         │
│  │ Context     │  │  Vector     │  │  Retention  │         │
│  │ Capture     │  │  Storage    │  │  Policy     │         │
│  └─────────────┘  └──────┬──────┘  └─────────────┘         │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │    ChromaDB     │
                   │  (Vector Store)  │
                   └─────────────────┘
```

## Core Design Decisions

### 1. ChromaDB Choice

**Decision**: Use ChromaDB as the vector database

**Rationale**:
- **Simplicity**: Single Python package, no external server required
- **Performance**: In-memory + persistent storage, <50ms queries
- **Features**: Built-in embeddings, similarity search, metadata filtering
- **Cost**: Free, open-source (Apache 2.0 license)
- **Maintenance**: Active development, good documentation

**Alternatives Considered**:
- **Pinecone**: Cloud-only, paid service → Conflicts with local-first principle
- **Weaviate**: Requires separate server, more complex → Overkill for single-user
- **FAISS**: Low-level library, no persistence → Would need custom wrapper
- **Qdrant**: Separate server, more features → Too heavyweight for this use case

### 2. Embedding Model

**Decision**: Use `sentence-transformers/all-MiniLM-L6-v2` for embeddings

**Rationale**:
- **Size**: Only 80MB download, fits in memory easily
- **Speed**: ~1000 sentences/second on CPU
- **Quality**: 384-dimensional embeddings, good semantic similarity
- **Cost**: Free, runs locally, no API calls
- **Compatibility**: Well-supported by ChromaDB

**Alternatives**:
- **OpenAI embeddings**: API costs, requires internet → Not local-first
- **Larger models (e.g., mpnet)**: Better quality but 420MB+ → Too heavy
- **Custom fine-tuned**: Better domain-specific results → Premature optimization

**Trade-off**: Slightly lower quality than GPT-3.5 embeddings, but free and local

### 3. Memory Schema

**Decision**: Use three collection types with distinct schemas

**Collections**:

1. **`screen_memories`** - Screen captures and AI analyses
   ```python
   {
     "id": "screen_20231026_123456",
     "embedding": [0.1, 0.2, ...],  # 384-dim vector
     "metadata": {
       "timestamp": "2023-10-26T12:34:56Z",
       "type": "screen_analysis",
       "ai_provider": "gemini",
       "screen_text": "Login form with username, password...",
       "ai_analysis": "UI contains authentication form...",
       "screenshot_path": "/path/to/screenshot.png",
       "session_id": "session_abc123"
     },
     "document": "Screen analyzed at 2023-10-26: Login form..."
   }
   ```

2. **`action_memories`** - Automation actions and outcomes
   ```python
   {
     "id": "action_20231026_123457",
     "embedding": [0.3, 0.4, ...],
     "metadata": {
       "timestamp": "2023-10-26T12:34:57Z",
       "type": "automation_action",
       "action": "click",
       "target": {"x": 500, "y": 300, "element": "login_button"},
       "success": true,
       "mcp_server": "hands",
       "session_id": "session_abc123"
     },
     "document": "Clicked login button at (500, 300) - success"
   }
   ```

3. **`workflow_memories`** - Multi-step workflows and patterns
   ```python
   {
     "id": "workflow_20231026_123500",
     "embedding": [0.5, 0.6, ...],
     "metadata": {
       "timestamp": "2023-10-26T12:35:00Z",
       "type": "workflow",
       "name": "google_search_automation",
       "steps": 5,
       "success_rate": 0.95,
       "avg_duration": 12.3,
       "session_id": "session_abc123"
     },
     "document": "Google search workflow: navigate, type query, click search..."
   }
   ```

**Rationale for 3 Collections**:
- **Separation of concerns**: Different query patterns for different memory types
- **Optimized metadata**: Each type has relevant fields for filtering
- **Storage efficiency**: Can apply different retention policies per type
- **Query performance**: Smaller collections = faster searches

**Alternative Considered**: Single unified collection
- ❌ Harder to filter by memory type
- ❌ Metadata schema conflicts
- ❌ Slower queries on large dataset

### 4. Storage Location

**Decision**: Store ChromaDB data in `~/.claude-vision-hands/memory/`

**Rationale**:
- **User directory**: Persists across project updates
- **Hidden folder**: Doesn't clutter workspace
- **Configurable**: Can override via `MEMORY_PATH` env var
- **Separate from logs**: Logs in `~/.claude-hands-logs/`, memory in separate location

**Directory Structure**:
```
~/.claude-vision-hands/
├── memory/
│   ├── chromadb/              # ChromaDB persistence
│   │   ├── screen_memories/
│   │   ├── action_memories/
│   │   └── workflow_memories/
│   ├── screenshots/           # Referenced screenshot files
│   └── memory.db              # SQLite metadata (retention policies)
└── config/
    └── memory_config.yaml     # Memory configuration
```

### 5. Memory Manager Pattern

**Decision**: Create centralized `MemoryManager` class

**Interface**:
```python
class MemoryManager:
    """Central coordinator for all memory operations"""

    def __init__(self, config: MemoryConfig):
        self.chroma_client = chromadb.PersistentClient(path=config.storage_path)
        self.embedder = SentenceTransformer(config.embedding_model)
        self.collections = self._init_collections()
        self.retention = RetentionPolicy(config.retention)

    async def store_memory(
        self,
        content: str,
        memory_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store new memory with automatic embedding"""
        pass

    async def search_memories(
        self,
        query: str,
        memory_types: List[str] = None,
        limit: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Memory]:
        """Semantic search across memories"""
        pass

    async def get_memory(self, memory_id: str) -> Memory:
        """Retrieve specific memory by ID"""
        pass

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete specific memory"""
        pass

    async def cleanup_old_memories(self) -> CleanupStats:
        """Apply retention policies"""
        pass

    async def get_stats(self) -> MemoryStats:
        """Get memory usage statistics"""
        pass
```

**Rationale**:
- **Single responsibility**: Manages all memory operations
- **Lazy initialization**: ChromaDB loaded only when first used
- **Thread-safe**: Uses asyncio locks for concurrent access
- **Testable**: Clear interface for mocking

**Alternative**: Scatter memory logic across MCP servers
- ❌ Code duplication
- ❌ Hard to maintain consistency
- ❌ No centralized quota/retention management

### 6. Auto-Capture Strategy

**Decision**: Opt-in automatic capture with configurable triggers

**Configuration**:
```yaml
memory:
  auto_capture:
    enabled: true
    triggers:
      # Capture AI analyses automatically
      ai_analysis: true
      # Capture successful automations
      successful_actions: true
      # Capture failed actions (for debugging)
      failed_actions: true
      # Capture workflow completions
      workflow_completion: true
      # Capture manual saves via MCP tool
      manual_save: true

    filters:
      # Don't capture repetitive actions
      min_interval_seconds: 5
      # Ignore trivial mouse moves
      ignore_mouse_moves: true
      # Ignore temporary/test sessions
      ignore_sessions: ["test_*"]
```

**Implementation**:
```python
# In Vision MCP server.py
@app.tool()
async def analyze_screen_ai(prompt: str, auto_capture: bool = True):
    result = analyzer.analyze(screenshot, prompt)

    # Auto-capture if enabled
    if auto_capture and memory_config.auto_capture.ai_analysis:
        await memory_manager.store_memory(
            content=f"{prompt} -> {result['analysis']}",
            memory_type="screen",
            metadata={
                "provider": result["provider"],
                "screen_text": result.get("text", ""),
                "ai_analysis": result["analysis"]
            }
        )

    return result
```

**Rationale**:
- **Opt-in**: Users enable explicitly → No surprise storage
- **Configurable**: Fine-grained control over what's captured
- **Performance**: Async storage doesn't block MCP responses
- **Privacy**: Can disable for sensitive sessions

**Alternative**: Always capture everything
- ❌ Privacy concerns
- ❌ Storage bloat
- ❌ User has no control

### 7. Retention Policy

**Decision**: Multi-tier retention with automatic cleanup

**Policy Configuration**:
```yaml
memory:
  retention:
    # Keep everything for 30 days
    default_retention_days: 30

    # Tier-based retention
    tiers:
      # Recent: Keep everything
      recent:
        max_age_days: 7
        max_items: null  # unlimited

      # Medium-term: Keep important items
      medium:
        max_age_days: 30
        max_items: 1000
        keep_successful: true  # Keep successful workflows
        discard_repetitive: true  # Remove duplicates

      # Long-term: Keep only significant items
      long_term:
        max_age_days: 365
        max_items: 500
        keep_criteria:
          - successful_workflows: true
          - manual_bookmarks: true
          - unique_screens: true

    # Automatic cleanup schedule
    cleanup:
      enabled: true
      schedule: "daily"  # or "weekly", "manual"
      time: "03:00"  # Run at 3 AM
```

**Cleanup Algorithm**:
```python
async def cleanup_old_memories(self):
    stats = CleanupStats()

    # Tier 1: Delete anything older than 365 days (except bookmarks)
    old_memories = await self.query_memories(
        max_age_days=365,
        exclude_bookmarked=True
    )
    stats.deleted += await self.bulk_delete(old_memories)

    # Tier 2: Deduplicate repetitive actions (30-365 days)
    duplicates = await self.find_duplicates(
        age_range=(30, 365),
        similarity_threshold=0.95
    )
    stats.deduplicated += await self.keep_one_per_cluster(duplicates)

    # Tier 3: Enforce quota limits per collection
    for collection in self.collections.values():
        if collection.count() > self.config.max_items:
            # Keep most important, delete least important
            to_delete = await self.rank_by_importance(
                collection,
                keep_count=self.config.max_items
            )
            stats.deleted += await collection.delete(to_delete)

    return stats
```

**Rationale**:
- **Automatic**: No manual intervention needed
- **Intelligent**: Keeps important, removes noise
- **Configurable**: Users can adjust policies
- **Safe**: Always keeps bookmarked/flagged items

**Alternative**: Manual deletion only
- ❌ Storage grows unbounded
- ❌ User has to maintain manually
- ❌ Performance degrades over time

### 8. MCP Integration Pattern

**Decision**: Add `memory_` prefixed tools to Integration MCP

**New MCP Tools** (5 tools):

1. `memory_store(content, type, metadata)` - Manual memory storage
2. `memory_search(query, types, limit, filters)` - Semantic search
3. `memory_get(memory_id)` - Retrieve by ID
4. `memory_delete(memory_id)` - Delete specific memory
5. `memory_stats()` - Usage statistics

**Tool Implementation**:
```python
# In integration-mcp/server.py

from memory.manager import MemoryManager

# Lazy initialization
memory_manager = None

def get_memory_manager():
    global memory_manager
    if memory_manager is None:
        memory_manager = MemoryManager(load_config())
    return memory_manager

@app.tool()
async def memory_search(
    query: str,
    memory_types: List[str] = None,
    limit: int = 10,
    filters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Search memories using natural language query

    Args:
        query: Natural language search query
        memory_types: Filter by types (screen, action, workflow)
        limit: Maximum results to return
        filters: Additional metadata filters

    Returns:
        List of matching memories with similarity scores

    Example:
        results = await memory_search(
            "login form automation",
            memory_types=["screen", "workflow"],
            limit=5
        )
    """
    try:
        manager = get_memory_manager()
        memories = await manager.search_memories(
            query=query,
            memory_types=memory_types,
            limit=limit,
            filters=filters
        )

        return {
            "success": True,
            "query": query,
            "count": len(memories),
            "memories": [m.to_dict() for m in memories]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

**Rationale**:
- **Integration MCP**: Coordinates across all servers → Natural home for memory
- **Prefix convention**: `memory_` makes tools easy to discover
- **Familiar patterns**: Matches existing tool design (async, error handling)
- **Backward compatible**: New tools, no changes to existing ones

**Alternative**: Separate memory-mcp server
- ❌ Another process to manage
- ❌ More complex deployment
- ❌ Harder to coordinate with other MCPs

### 9. Error Handling & Graceful Degradation

**Decision**: Memory is optional feature with full fallback

**Error Scenarios**:

1. **ChromaDB unavailable** (dependency not installed)
   ```python
   try:
       import chromadb
   except ImportError:
       MEMORY_AVAILABLE = False
       logger.warning("ChromaDB not installed, memory features disabled")
   ```

2. **Storage path issues** (permissions, disk full)
   ```python
   try:
       memory_manager = MemoryManager(config)
   except StorageError as e:
       MEMORY_AVAILABLE = False
       logger.error(f"Memory storage unavailable: {e}")
   ```

3. **Embedding model download failure**
   ```python
   try:
       embedder = SentenceTransformer(model_name)
   except Exception as e:
       # Fallback to simple text search (no embeddings)
       embedder = FallbackSearcher()
       logger.warning("Using fallback text search")
   ```

4. **Search/store failures** (corruption, errors)
   ```python
   @app.tool()
   async def memory_search(query: str):
       if not MEMORY_AVAILABLE:
           return {
               "success": False,
               "error": "Memory features are disabled",
               "fallback": "Check logs for configuration issues"
           }

       try:
           results = await manager.search(query)
           return {"success": True, "memories": results}
       except Exception as e:
           logger.exception("Memory search failed")
           return {
               "success": False,
               "error": str(e),
               "query": query
           }
   ```

**Rationale**:
- **No breaking changes**: System works without memory
- **Clear feedback**: Error messages explain what's wrong
- **Logging**: All errors logged for debugging
- **Graceful degradation**: Fallback to simpler search if embeddings fail

### 10. Performance Optimization

**Decision**: Multi-level caching + lazy loading

**Optimization Strategies**:

1. **Lazy Loading**:
   ```python
   class MemoryManager:
       def __init__(self, config):
           self._chroma_client = None  # Not loaded yet
           self._embedder = None
           self.config = config

       @property
       def chroma_client(self):
           if self._chroma_client is None:
               self._chroma_client = chromadb.PersistentClient(...)
           return self._chroma_client
   ```

2. **Embedding Cache** (avoid re-embedding same text):
   ```python
   class EmbeddingCache:
       def __init__(self, max_size=1000):
           self.cache = LRUCache(max_size)

       def get_embedding(self, text: str):
           cache_key = hash(text)
           if cache_key in self.cache:
               return self.cache[cache_key]

           embedding = self.embedder.encode(text)
           self.cache[cache_key] = embedding
           return embedding
   ```

3. **Batch Operations** (store multiple memories at once):
   ```python
   async def store_batch(self, memories: List[MemoryData]):
       # Generate all embeddings in parallel
       embeddings = await asyncio.gather(*[
           self.generate_embedding(m.content) for m in memories
       ])

       # Single ChromaDB transaction
       collection.add(
           ids=[m.id for m in memories],
           embeddings=embeddings,
           metadatas=[m.metadata for m in memories],
           documents=[m.content for m in memories]
       )
   ```

4. **Index Optimization**:
   ```yaml
   chromadb:
     index_type: "hnsw"  # Hierarchical Navigable Small World
     hnsw:
       M: 16              # Number of connections
       ef_construction: 200
       ef_search: 100
   ```

**Performance Targets**:
- Memory storage: <10ms (async, non-blocking)
- Embedding generation: <50ms (CPU) or <10ms (GPU)
- Vector search: <50ms for collections up to 10,000 items
- Cleanup operation: <5 seconds for 10,000 items

**Monitoring**:
```python
@app.tool()
async def memory_stats():
    return {
        "collections": {
            "screen_memories": {
                "count": 1234,
                "size_mb": 45.2,
                "avg_query_ms": 23.5
            },
            # ...
        },
        "performance": {
            "embedding_cache_hit_rate": 0.73,
            "avg_store_time_ms": 8.2,
            "avg_search_time_ms": 31.4
        },
        "storage": {
            "total_size_mb": 156.8,
            "quota_limit_mb": 500,
            "usage_percent": 31.4
        }
    }
```

### 11. Privacy & Security

**Decision**: Local-only storage with configurable data retention

**Privacy Features**:

1. **Local Storage Only** - No cloud sync
2. **Opt-in Capture** - Disabled by default
3. **Configurable Retention** - Auto-delete old memories
4. **Screenshot Redaction** - Optional blur/mask sensitive areas
5. **Session Isolation** - Separate test vs production sessions

**Configuration**:
```yaml
memory:
  privacy:
    # Redact sensitive data
    redact_screenshots: true
    redact_patterns:
      - regex: "\\b\\d{16}\\b"  # Credit card numbers
        replacement: "[CARD_REDACTED]"
      - regex: "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"
        replacement: "[EMAIL_REDACTED]"

    # Exclude sensitive sessions
    exclude_sessions:
      - "banking_*"
      - "password_manager_*"

    # Data retention
    auto_delete_days: 30
    delete_on_exit: false  # Set true for ultra-private mode
```

**Implementation**:
```python
async def store_memory(self, content: str, metadata: Dict):
    # Apply redaction
    if self.config.privacy.redact_screenshots:
        content = self.redact_sensitive_data(content)
        if "screenshot_path" in metadata:
            await self.redact_screenshot(metadata["screenshot_path"])

    # Check exclusion patterns
    session_id = metadata.get("session_id", "")
    for pattern in self.config.privacy.exclude_sessions:
        if fnmatch.fnmatch(session_id, pattern):
            logger.info(f"Skipping memory storage for excluded session: {session_id}")
            return None

    # Store with expiration metadata
    metadata["expires_at"] = datetime.now() + timedelta(
        days=self.config.privacy.auto_delete_days
    )

    return await self._store_to_chromadb(content, metadata)
```

### 12. Testing Strategy

**Decision**: 3-tier testing (unit, integration, E2E)

**Unit Tests** (memory/tests/test_manager.py):
```python
@pytest.mark.asyncio
async def test_store_and_retrieve_memory():
    manager = MemoryManager(test_config)

    # Store memory
    memory_id = await manager.store_memory(
        content="Test screen analysis",
        memory_type="screen",
        metadata={"test": true}
    )

    # Retrieve memory
    memory = await manager.get_memory(memory_id)
    assert memory.content == "Test screen analysis"
    assert memory.metadata["test"] == true
```

**Integration Tests** (test with real ChromaDB):
```python
@pytest.mark.integration
async def test_semantic_search():
    manager = MemoryManager(real_chromadb_path)

    # Store multiple memories
    await manager.store_memory("Login form automation", "screen", {})
    await manager.store_memory("User authentication workflow", "workflow", {})
    await manager.store_memory("Homepage screenshot", "screen", {})

    # Search with semantic query
    results = await manager.search_memories("login process", limit=5)

    # Should find related memories
    assert len(results) >= 2
    assert any("login" in r.content.lower() for r in results)
    assert any("authentication" in r.content.lower() for r in results)
```

**E2E Tests** (test through MCP tools):
```python
@pytest.mark.e2e
async def test_memory_workflow():
    # Store via MCP tool
    store_result = await memory_store(
        content="Automated Google search",
        type="workflow",
        metadata={"steps": 3}
    )
    assert store_result["success"]

    # Search via MCP tool
    search_result = await memory_search("Google automation")
    assert search_result["count"] > 0
    assert store_result["memory_id"] in [m["id"] for m in search_result["memories"]]
```

## Configuration Schema

**File**: `config/memory_config.yaml`

```yaml
memory:
  # Enable/disable memory system
  enabled: true

  # Storage configuration
  storage:
    path: "~/.claude-vision-hands/memory"
    max_size_mb: 500
    chromadb:
      index_type: "hnsw"
      hnsw:
        M: 16
        ef_construction: 200
        ef_search: 100

  # Embedding configuration
  embeddings:
    model: "sentence-transformers/all-MiniLM-L6-v2"
    device: "cpu"  # or "cuda" for GPU
    cache_size: 1000

  # Auto-capture settings
  auto_capture:
    enabled: true
    triggers:
      ai_analysis: true
      successful_actions: true
      failed_actions: true
      workflow_completion: true
    filters:
      min_interval_seconds: 5
      ignore_mouse_moves: true

  # Retention policy
  retention:
    default_retention_days: 30
    max_items_per_collection: 10000
    cleanup:
      enabled: true
      schedule: "daily"
      time: "03:00"

  # Privacy settings
  privacy:
    redact_screenshots: false
    redact_patterns: []
    exclude_sessions: []
    auto_delete_days: 30
    delete_on_exit: false

  # Performance tuning
  performance:
    batch_size: 100
    embedding_batch_size: 32
    search_timeout_ms: 5000
```

## Migration Strategy

**Phase 1**: Add memory as optional feature
- Install ChromaDB as optional dependency
- Add memory_config.yaml with disabled default
- Implement MemoryManager with feature flag

**Phase 2**: Integrate with existing MCP servers
- Add auto-capture hooks to vision/hands/browser MCPs
- Add memory_* tools to integration MCP
- Update documentation

**Phase 3**: Enable by default (opt-out)
- Change default config to enabled: true
- Add setup wizard for first-time users
- Migration guide for existing users

## Open Questions

1. **Embedding model size trade-off**: Should we support multiple models (small/medium/large)?
   - **Decision needed**: Single default model vs configurable options

2. **Multi-user support**: Should we plan for shared memory across users?
   - **Current**: Single-user only
   - **Future**: Consider collection-level access control

3. **Cloud sync**: Should we support syncing memory to cloud storage?
   - **Current**: Local-only
   - **Future**: Optional S3/GCS backup

4. **Memory compression**: Should old memories be compressed to save space?
   - **Current**: Simple deletion based on retention
   - **Future**: Compress old memories to reduce storage

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Database Comparison](https://benchmark.vectorview.ai/vectordbs.html)
- [Semantic Search Best Practices](https://www.pinecone.io/learn/semantic-search/)
