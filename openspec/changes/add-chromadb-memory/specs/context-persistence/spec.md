# Spec: Context Persistence

## ADDED Requirements

### Requirement: Automatic Context Capture
The system SHALL automatically capture relevant context from MCP tool interactions when auto-capture is enabled.

#### Scenario: Auto-capture AI screen analysis
- **GIVEN** auto-capture is enabled for AI analyses
- **WHEN** user calls `analyze_screen_ai("identify UI elements")`
- **THEN** system stores memory automatically after analysis completes
- **AND** memory includes: AI prompt, result, screen text, timestamp
- **AND** storage happens asynchronously (doesn't block tool response)

#### Scenario: Auto-capture successful automation action
- **GIVEN** auto-capture enabled for successful actions
- **WHEN** user performs `mouse_click(500, 300)` that succeeds
- **THEN** system stores action memory with click coordinates and outcome
- **AND** memory tagged with action type and success status

#### Scenario: Skip repetitive actions based on interval filter
- **GIVEN** min_interval_seconds is 5
- **AND** user clicked at (500, 300) 2 seconds ago
- **WHEN** user clicks at (500, 300) again
- **THEN** system skips storing second memory (too soon/repetitive)
- **AND** logs skip reason for debugging

#### Scenario: Respect privacy exclusions
- **GIVEN** session_id is "banking_session_123"
- **AND** "banking_*" is in exclusion patterns
- **WHEN** user performs action in that session
- **THEN** system does NOT store any memory
- **AND** logs privacy exclusion for audit

---

### Requirement: Manual Memory Storage
The system SHALL provide MCP tools for explicit memory storage with full control.

#### Scenario: Store custom memory with metadata
- **GIVEN** user wants to bookmark important moment
- **WHEN** user calls `memory_store(content="Important workflow completed successfully", type="workflow", metadata={"bookmarked": true, "priority": "high"})`
- **THEN** system stores memory with user-provided metadata
- **AND** returns memory ID for future reference
- **AND** memory is protected from auto-cleanup (bookmarked)

#### Scenario: Store memory with file attachment reference
- **GIVEN** user has screenshot file at `/tmp/screenshot_1234.png`
- **WHEN** user stores memory with `metadata={"screenshot_path": "/tmp/screenshot_1234.png"}`
- **THEN** system stores path reference in metadata
- **AND** optionally copies screenshot to memory storage directory
- **AND** enables retrieval of associated file later

---

### Requirement: Session Context Tracking
The system SHALL maintain session context and associate memories with sessions.

#### Scenario: Auto-generate session ID on MCP server start
- **GIVEN** MCP server starts fresh
- **WHEN** first memory is stored
- **THEN** system generates unique session ID (e.g., "session_20231026_123456")
- **AND** all memories in this run use same session_id
- **AND** session_id persists for entire server lifetime

#### Scenario: Resume previous session context on restart
- **GIVEN** user restarts MCP server
- **WHEN** user calls `memory_resume_session(session_id="session_abc123")`
- **THEN** system loads context from previous session
- **AND** searches return memories from that session with higher relevance
- **AND** enables "continue where I left off" workflow

#### Scenario: List all available sessions
- **GIVEN** user has worked across multiple sessions over time
- **WHEN** user calls `memory_list_sessions()`
- **THEN** system returns all unique session IDs with metadata:
  - Session start/end timestamps
  - Total memories in session
  - Session summary (most common actions/screens)
- **AND** enables session browsing and selection

---

### Requirement: Workflow Pattern Learning
The system SHALL identify and persist recurring automation patterns across sessions.

#### Scenario: Detect repeated action sequence
- **GIVEN** user performs sequence: navigate → fill form → click submit (3 times in past week)
- **WHEN** pattern detection runs
- **THEN** system identifies recurring 3-step workflow
- **AND** stores as workflow memory with pattern confidence score
- **AND** suggests automating this pattern in future

#### Scenario: Build workflow from successful actions
- **GIVEN** user manually completed multi-step task with 10 actions
- **AND** all actions succeeded
- **WHEN** user calls `memory_create_workflow_from_session(session_id, name="google_search_workflow")`
- **THEN** system extracts action sequence from session
- **AND** creates reusable workflow memory
- **AND** workflow can be suggested when similar context detected

---

### Requirement: Context-Aware Suggestions
The system SHALL provide intelligent suggestions based on historical context.

#### Scenario: Suggest similar past actions
- **GIVEN** user is viewing login form (detected by AI)
- **AND** user previously automated login on similar form
- **WHEN** system analyzes current context
- **THEN** system suggests: "I found similar login automation from Oct 20, would you like to replay it?"
- **AND** provides memory ID for reference

#### Scenario: Warn about previously failed actions
- **GIVEN** user is about to click element at (500, 300)
- **AND** previous click at (500, 300) failed 5 times
- **WHEN** user hovers/considers action
- **THEN** system warns: "This action failed 5 times previously, success rate: 0%"
- **AND** suggests alternative approaches from successful memories

---

### Requirement: Retention Policy Management
The system SHALL enforce configurable retention policies to manage storage growth.

#### Scenario: Auto-delete memories older than retention period
- **GIVEN** retention policy is 30 days
- **AND** cleanup schedule is daily at 3 AM
- **WHEN** cleanup cron job runs
- **THEN** system deletes all memories older than 30 days (unless bookmarked)
- **AND** logs deletion count and freed space
- **AND** updates storage statistics

#### Scenario: Keep important memories beyond retention period
- **GIVEN** memory has `bookmarked: true` or `manual_save: true`
- **AND** memory is 100 days old (beyond 30-day policy)
- **WHEN** cleanup runs
- **THEN** system preserves this memory
- **AND** only deletes auto-captured, non-important old memories

#### Scenario: Enforce maximum collection size
- **GIVEN** screen_memories collection has 10,000 items (at limit)
- **AND** user stores new screen memory
- **WHEN** storage executes
- **THEN** system ranks existing memories by importance score
- **AND** deletes lowest-ranked memory to make space
- **AND** stores new memory successfully

#### Scenario: Deduplicate similar memories
- **GIVEN** 50 screen memories are 95%+ similar (same login screen captured repeatedly)
- **WHEN** deduplication policy runs
- **THEN** system keeps only 1 representative memory from cluster
- **AND** deletes 49 near-duplicates
- **AND** records consolidation in metadata

---

### Requirement: Privacy and Data Control
The system SHALL provide user control over stored memories and privacy settings.

#### Scenario: View all stored memories for user session
- **GIVEN** user wants to review captured data
- **WHEN** user calls `memory_list(session_id="current")`
- **THEN** system returns all memories from current session
- **AND** includes content previews and metadata
- **AND** enables informed privacy decisions

#### Scenario: Delete all memories from specific session
- **GIVEN** user performed sensitive work in session_abc123
- **WHEN** user calls `memory_delete_session(session_id="session_abc123")`
- **THEN** system deletes ALL memories associated with that session
- **AND** prompts for confirmation before deletion
- **AND** returns count of deleted items

#### Scenario: Export memories for backup
- **GIVEN** user wants to backup memory data
- **WHEN** user calls `memory_export(format="json", output_path="/tmp/memories.json")`
- **THEN** system exports all memories to JSON file
- **AND** includes embeddings, metadata, and content
- **AND** file can be re-imported later

#### Scenario: Clear all memories (nuclear option)
- **GIVEN** user wants fresh start
- **WHEN** user calls `memory_clear_all(confirm=true)`
- **THEN** system deletes all memories from all collections
- **AND** requires explicit confirmation parameter
- **AND** creates backup before deletion
- **AND** resets to empty state

---

### Requirement: Memory Statistics and Insights
The system SHALL provide analytics on memory usage and patterns.

#### Scenario: View memory usage dashboard
- **GIVEN** user wants overview of memory system
- **WHEN** user calls `memory_stats()`
- **THEN** system returns comprehensive statistics:
  - Total memories by type (screen: 1234, action: 5678, workflow: 89)
  - Storage size and quota usage (156 MB / 500 MB, 31%)
  - Most frequent actions/screens
  - Session count and average session length
  - Performance metrics (avg query time, cache hit rate)

#### Scenario: Analyze automation success patterns
- **GIVEN** user wants to improve automation reliability
- **WHEN** user calls `memory_analyze_patterns(type="action", metric="success_rate")`
- **THEN** system analyzes all action memories
- **AND** identifies high-success patterns (e.g., "form fills succeed 95%")
- **AND** identifies failure-prone patterns (e.g., "clicks on dynamic elements fail 40%")
- **AND** provides actionable insights for optimization

---

### Requirement: Backup and Recovery
The system SHALL enable backup and recovery of memory data.

#### Scenario: Automatic backup before dangerous operations
- **GIVEN** user calls `memory_clear_all()` or `memory_delete_session()`
- **WHEN** operation executes
- **THEN** system creates automatic backup first
- **AND** stores backup at `~/.claude-vision-hands/memory/backups/backup_20231026_123456.tar.gz`
- **AND** keeps last 5 backups, deletes older ones

#### Scenario: Manual backup creation
- **GIVEN** user wants to create backup before experiment
- **WHEN** user calls `memory_backup(name="before_experiment")`
- **THEN** system creates named backup of all memory data
- **AND** returns backup file path
- **AND** backup includes ChromaDB data, config, and metadata

#### Scenario: Restore from backup
- **GIVEN** user has backup file from previous state
- **WHEN** user calls `memory_restore(backup_path="/path/to/backup.tar.gz")`
- **THEN** system prompts for confirmation (will overwrite current data)
- **AND** restores ChromaDB collections from backup
- **AND** validates restored data integrity
- **AND** reports restoration success with item counts

---

### Requirement: Integration with Existing MCP Servers
The system SHALL integrate memory capture with vision, hands, and browser MCP servers.

#### Scenario: Vision MCP auto-captures screen analyses
- **GIVEN** vision-mcp server has memory manager instance
- **WHEN** `analyze_screen_ai()` tool completes
- **THEN** vision-mcp calls `memory_manager.store_memory()` with analysis result
- **AND** memory includes AI provider, prompt, result, screen text
- **AND** storage is async and doesn't slow down tool response

#### Scenario: Hands MCP captures automation actions
- **GIVEN** hands-mcp server has memory manager
- **WHEN** `mouse_click()` or `keyboard_type()` completes
- **THEN** hands-mcp stores action memory with full context
- **AND** memory includes action type, parameters, success/failure, timestamp

#### Scenario: Browser MCP captures navigation and workflows
- **GIVEN** browser-mcp executes workflow
- **WHEN** workflow completes (success or failure)
- **THEN** browser-mcp stores workflow memory
- **AND** memory includes workflow name, steps, duration, ARIA tree context

#### Scenario: Memory disabled falls back gracefully
- **GIVEN** memory config has `enabled: false`
- **WHEN** any MCP server tries to store memory
- **THEN** operation silently skips (no-op)
- **AND** no errors are raised
- **AND** MCP tools continue working normally

---

### Requirement: Configuration Management
The system SHALL load memory configuration from centralized config file.

#### Scenario: Load default configuration
- **GIVEN** no custom memory config exists
- **WHEN** memory manager initializes
- **THEN** system uses built-in defaults:
  - enabled: false (opt-in)
  - storage_path: ~/.claude-vision-hands/memory
  - retention_days: 30
  - max_size_mb: 500
- **AND** logs configuration source for debugging

#### Scenario: Override config with environment variables
- **GIVEN** env var MEMORY_STORAGE_PATH="/custom/path"
- **WHEN** memory manager initializes
- **THEN** system uses environment variable value
- **AND** environment takes precedence over config file
- **AND** logs configuration override

#### Scenario: Validate configuration on load
- **GIVEN** config file has invalid value (e.g., negative retention_days)
- **WHEN** memory manager loads config
- **THEN** system detects validation error
- **AND** raises clear error message explaining issue
- **AND** suggests correct value format
