# Spec: Vector Storage

## ADDED Requirements

### Requirement: ChromaDB Initialization
The system SHALL initialize ChromaDB persistent client for vector storage on first memory operation.

#### Scenario: Initialize ChromaDB on first memory storage
- **GIVEN** memory system is enabled in configuration
- **WHEN** user stores first memory via `memory_store()` tool
- **THEN** system creates ChromaDB persistent client at configured storage path
- **AND** creates three collections: `screen_memories`, `action_memories`, `workflow_memories`
- **AND** initialization completes within 2 seconds

#### Scenario: Handle ChromaDB initialization failure
- **GIVEN** storage path is not writable
- **WHEN** system attempts to initialize ChromaDB
- **THEN** system logs error with details
- **AND** returns user-friendly error message explaining permission issue
- **AND** disables memory features gracefully (system continues without memory)

#### Scenario: Lazy load ChromaDB to avoid startup overhead
- **GIVEN** memory system is enabled
- **WHEN** MCP server starts
- **THEN** ChromaDB client is NOT initialized immediately
- **AND** server startup time remains under 1 second
- **AND** ChromaDB initializes only on first memory operation

---

### Requirement: Vector Embedding Generation
The system SHALL generate semantic embeddings for memory content using sentence transformers.

#### Scenario: Generate embedding for screen analysis
- **GIVEN** user stores screen memory with content "Login form with username and password fields"
- **WHEN** system processes memory storage
- **THEN** system generates 384-dimensional embedding vector
- **AND** embedding generation completes within 100ms on CPU
- **AND** embedding captures semantic meaning of the content

#### Scenario: Cache embeddings for repeated content
- **GIVEN** system has previously embedded text "Login form"
- **WHEN** user stores another memory with same text "Login form"
- **THEN** system retrieves embedding from cache
- **AND** avoids re-computation for performance
- **AND** cache hit reduces embedding time to <5ms

#### Scenario: Handle embedding model download on first use
- **GIVEN** embedding model `all-MiniLM-L6-v2` not yet downloaded
- **WHEN** system generates first embedding
- **THEN** system downloads model automatically (~80MB)
- **AND** shows progress indicator during download
- **AND** caches model locally for future use

---

### Requirement: Memory Storage Operations
The system SHALL store memories with embeddings and metadata in appropriate ChromaDB collections.

#### Scenario: Store screen memory with full metadata
- **GIVEN** user analyzes screen with AI
- **WHEN** system stores screen memory
- **THEN** memory is stored in `screen_memories` collection
- **AND** includes 384-dim embedding vector
- **AND** includes metadata: timestamp, type, AI provider, screen text, analysis result
- **AND** includes document text for retrieval
- **AND** storage completes within 10ms (async, non-blocking)

#### Scenario: Store action memory with automation details
- **GIVEN** user performs mouse click automation
- **WHEN** system stores action memory
- **THEN** memory is stored in `action_memories` collection
- **AND** includes metadata: timestamp, action type, target coordinates, success status
- **AND** includes full action context for future reference

#### Scenario: Store workflow memory with execution metrics
- **GIVEN** user completes browser automation workflow
- **WHEN** system stores workflow memory
- **THEN** memory is stored in `workflow_memories` collection
- **AND** includes metadata: workflow name, steps count, success rate, duration
- **AND** enables future workflow optimization based on history

#### Scenario: Generate unique memory IDs
- **GIVEN** system stores multiple memories
- **WHEN** each memory is created
- **THEN** system generates unique ID in format `{type}_{timestamp}_{uuid}`
- **AND** IDs are collision-resistant across millions of memories
- **AND** IDs sort chronologically by timestamp

---

### Requirement: Memory Retrieval Operations
The system SHALL retrieve memories by ID with full metadata and content.

#### Scenario: Retrieve memory by exact ID
- **GIVEN** memory exists with ID "screen_20231026_123456_abc"
- **WHEN** user calls `memory_get("screen_20231026_123456_abc")`
- **THEN** system returns complete memory object
- **AND** includes original content, metadata, and timestamp
- **AND** retrieval completes within 5ms

#### Scenario: Handle missing memory gracefully
- **GIVEN** no memory exists with ID "nonexistent_id"
- **WHEN** user calls `memory_get("nonexistent_id")`
- **THEN** system returns error with clear message "Memory not found"
- **AND** suggests using `memory_search()` to find similar memories

---

### Requirement: Memory Deletion Operations
The system SHALL delete specific memories by ID or batch delete by criteria.

#### Scenario: Delete single memory by ID
- **GIVEN** memory exists with ID "action_20231026_123456_xyz"
- **WHEN** user calls `memory_delete("action_20231026_123456_xyz")`
- **THEN** system removes memory from ChromaDB collection
- **AND** returns success confirmation
- **AND** subsequent `memory_get()` returns "not found"

#### Scenario: Batch delete old memories by age
- **GIVEN** 100 memories older than 365 days exist
- **WHEN** retention policy cleanup runs
- **THEN** system deletes all 100 old memories in single batch operation
- **AND** batch deletion completes within 5 seconds
- **AND** returns deletion statistics (count, freed space)

#### Scenario: Prevent deletion of bookmarked memories
- **GIVEN** memory has metadata flag `bookmarked: true`
- **WHEN** retention policy attempts to delete old memories
- **THEN** system skips bookmarked memory
- **AND** logs skip action for audit trail

---

### Requirement: Storage Quota Management
The system SHALL enforce configurable storage quotas and provide usage statistics.

#### Scenario: Enforce maximum collection size
- **GIVEN** `screen_memories` collection has 10,000 items (at quota limit)
- **WHEN** user attempts to store new screen memory
- **THEN** system triggers cleanup to make space
- **AND** deletes least important old memories based on ranking
- **AND** stores new memory successfully

#### Scenario: Report storage usage statistics
- **GIVEN** memory system contains various memories
- **WHEN** user calls `memory_stats()`
- **THEN** system returns storage metrics:
  - Total memories count per collection
  - Total storage size in MB
  - Quota limit and usage percentage
  - Average query/store latency
- **AND** statistics calculation completes within 100ms

#### Scenario: Warn when approaching quota limit
- **GIVEN** storage usage reaches 90% of quota
- **WHEN** user stores new memory
- **THEN** system logs warning about approaching limit
- **AND** suggests enabling auto-cleanup or increasing quota
- **AND** continues to store memory successfully

---

### Requirement: Batch Operations for Performance
The system SHALL support batch memory operations for improved throughput.

#### Scenario: Store multiple memories in single batch
- **GIVEN** user has 50 memories to store (e.g., workflow with many steps)
- **WHEN** user calls `memory_store_batch([memory1, memory2, ..., memory50])`
- **THEN** system generates all embeddings in parallel
- **AND** stores all memories in single ChromaDB transaction
- **AND** batch operation completes faster than 50 individual stores (>50% speedup)

#### Scenario: Retrieve multiple memories by ID list
- **GIVEN** user has list of 20 memory IDs
- **WHEN** user calls `memory_get_batch([id1, id2, ..., id20])`
- **THEN** system retrieves all memories in single query
- **AND** returns results in same order as requested IDs
- **AND** handles missing IDs gracefully (null entries in result)

---

### Requirement: Error Handling and Recovery
The system SHALL handle storage errors gracefully without breaking MCP server operation.

#### Scenario: Handle disk full error
- **GIVEN** storage disk is full
- **WHEN** user attempts to store memory
- **THEN** system catches storage error
- **AND** returns clear error message "Storage full, unable to save memory"
- **AND** suggests enabling cleanup or freeing disk space
- **AND** MCP server continues operating normally

#### Scenario: Handle ChromaDB corruption
- **GIVEN** ChromaDB data files are corrupted
- **WHEN** system attempts to initialize ChromaDB
- **THEN** system detects corruption on startup
- **AND** logs detailed error with recovery instructions
- **AND** offers to reset memory storage (with confirmation)
- **AND** creates backup of corrupted data before reset

#### Scenario: Retry transient errors
- **GIVEN** ChromaDB experiences temporary lock contention
- **WHEN** memory storage operation fails with retryable error
- **THEN** system retries operation up to 3 times with exponential backoff
- **AND** succeeds if lock is released
- **AND** returns error only after all retries exhausted
