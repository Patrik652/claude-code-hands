# Spec: Semantic Search

## ADDED Requirements

### Requirement: Natural Language Memory Search
The system SHALL enable semantic search across all memories using natural language queries.

#### Scenario: Search for similar screen memories
- **GIVEN** system has memories of "Login form", "Sign-in page", "Authentication screen"
- **WHEN** user searches with query "user login interface"
- **THEN** system returns all three memories ranked by semantic similarity
- **AND** most relevant memory ("Login form") has highest similarity score (>0.8)
- **AND** search completes within 50ms

#### Scenario: Search across multiple memory types
- **GIVEN** memories exist in screen, action, and workflow collections
- **WHEN** user searches "Google search automation" without type filter
- **THEN** system searches all three collections in parallel
- **AND** returns mixed results from different types
- **AND** clearly indicates memory type for each result

#### Scenario: Filter search by memory type
- **GIVEN** user only wants workflow memories
- **WHEN** user searches with `memory_types=["workflow"]`
- **THEN** system searches only `workflow_memories` collection
- **AND** ignores screen and action memories
- **AND** returns faster results due to smaller search space

---

### Requirement: Similarity Scoring and Ranking
The system SHALL rank search results by cosine similarity between query and memory embeddings.

#### Scenario: Return results ordered by relevance
- **GIVEN** query "login button automation"
- **AND** memories: "Click login button" (0.92), "Homepage navigation" (0.45), "Login form fill" (0.85)
- **WHEN** user performs search
- **THEN** results are ordered: "Click login button" (1st), "Login form fill" (2nd), "Homepage navigation" (3rd)
- **AND** each result includes similarity score
- **AND** scores range from 0.0 (unrelated) to 1.0 (identical)

#### Scenario: Filter by minimum similarity threshold
- **GIVEN** user sets `min_similarity=0.7`
- **WHEN** search returns results with scores [0.92, 0.68, 0.85, 0.55]
- **THEN** system filters out results below 0.7
- **AND** returns only [0.92, 0.85]
- **AND** improves result quality by removing weak matches

---

### Requirement: Metadata Filtering
The system SHALL support filtering search results by metadata criteria in addition to semantic similarity.

#### Scenario: Filter by date range
- **GIVEN** user wants memories from last week only
- **WHEN** user searches with `filters={"after": "2023-10-20", "before": "2023-10-27"}`
- **THEN** system returns only memories within date range
- **AND** combines semantic similarity with temporal filtering

#### Scenario: Filter by success status
- **GIVEN** user wants only successful automations
- **WHEN** user searches actions with `filters={"success": true}`
- **THEN** system returns only action memories where automation succeeded
- **AND** excludes failed attempts from results

#### Scenario: Filter by AI provider
- **GIVEN** user wants only Gemini-analyzed screens
- **WHEN** user searches screens with `filters={"ai_provider": "gemini"}`
- **THEN** system returns only screen memories analyzed by Gemini
- **AND** excludes OCR-only or other provider analyses

#### Scenario: Combine multiple filters
- **GIVEN** user applies filters: `{success: true, type: "workflow", after: "2023-10-01"}`
- **WHEN** search executes
- **THEN** system applies AND logic to all filters
- **AND** returns only successful workflows from October onwards

---

### Requirement: Search Result Pagination
The system SHALL support paginated search results for large result sets.

#### Scenario: Limit result count
- **GIVEN** search matches 150 memories
- **WHEN** user sets `limit=10`
- **THEN** system returns top 10 most relevant results
- **AND** response includes total count (150) for pagination UI

#### Scenario: Fetch subsequent pages
- **GIVEN** user has viewed first 10 results
- **WHEN** user requests `offset=10, limit=10`
- **THEN** system returns results 11-20
- **AND** maintains consistent ordering across pages
- **AND** page fetch completes within 50ms

#### Scenario: Handle offset beyond result set
- **GIVEN** search has 25 total results
- **WHEN** user requests `offset=100, limit=10`
- **THEN** system returns empty results array
- **AND** total_count still shows 25
- **AND** no error is raised (graceful handling)

---

### Requirement: Fuzzy Text Search Fallback
The system SHALL provide keyword-based search when embeddings are unavailable.

#### Scenario: Fallback when embedding model fails
- **GIVEN** embedding model failed to load
- **WHEN** user performs memory search
- **THEN** system falls back to simple text matching (LIKE query)
- **AND** logs warning about degraded search quality
- **AND** returns results based on keyword overlap

#### Scenario: Combine semantic and keyword search
- **GIVEN** semantic search enabled
- **WHEN** user searches for specific ID or exact phrase
- **THEN** system uses hybrid search (semantic + keyword)
- **AND** exact matches rank highest regardless of embedding similarity

---

### Requirement: Search Performance Optimization
The system SHALL maintain fast search performance even with large memory collections.

#### Scenario: Fast search on 10,000 memories
- **GIVEN** collection contains 10,000 memories
- **WHEN** user performs semantic search
- **THEN** search completes within 100ms
- **AND** uses HNSW index for approximate nearest neighbor search
- **AND** quality remains high (>95% recall compared to brute force)

#### Scenario: Parallel search across collections
- **GIVEN** user searches across all three collections
- **WHEN** search executes
- **THEN** system queries collections in parallel using asyncio
- **AND** total time equals slowest collection (not sum)
- **AND** overall latency stays under 150ms

#### Scenario: Cache frequent queries
- **GIVEN** user repeats same search "login form" multiple times
- **WHEN** second search executes
- **THEN** system retrieves results from cache
- **AND** cached result returns in <5ms
- **AND** cache expires after 5 minutes for freshness

---

### Requirement: Search Result Context
The system SHALL provide rich context with each search result for better understanding.

#### Scenario: Include memory metadata in results
- **GIVEN** search returns screen memory
- **WHEN** result is formatted
- **THEN** result includes:
  - Memory ID
  - Similarity score
  - Timestamp
  - Memory type
  - Content preview (first 200 chars)
  - Full metadata object
- **AND** enables user to make informed decisions without fetching full memory

#### Scenario: Highlight matching context
- **GIVEN** query "click submit button"
- **WHEN** search returns relevant memory
- **THEN** result highlights matching portions of content
- **AND** shows context around match (20 words before/after)
- **AND** makes it clear why result was returned

---

### Requirement: Semantic Clustering
The system SHALL identify and group semantically similar memories.

#### Scenario: Find duplicate or near-duplicate memories
- **GIVEN** system has multiple memories of same screen state
- **WHEN** user calls `memory_find_duplicates(similarity_threshold=0.95)`
- **THEN** system returns groups of highly similar memories
- **AND** each group represents potential duplicates
- **AND** enables cleanup of redundant memories

#### Scenario: Discover memory patterns
- **GIVEN** user performs similar automation repeatedly
- **WHEN** user calls `memory_cluster(memory_type="action", n_clusters=5)`
- **THEN** system groups actions into 5 semantic clusters
- **AND** identifies common automation patterns
- **AND** enables workflow optimization suggestions

---

### Requirement: Cross-Session Search
The system SHALL search across multiple user sessions and time periods.

#### Scenario: Search across all historical sessions
- **GIVEN** memories span 30 days across 50 sessions
- **WHEN** user searches without session filter
- **THEN** system searches entire memory history
- **AND** returns results from any session
- **AND** result metadata includes session_id for traceability

#### Scenario: Filter by specific session
- **GIVEN** user wants to review specific work session
- **WHEN** user searches with `filters={"session_id": "session_abc123"}`
- **THEN** system returns only memories from that session
- **AND** enables session-specific debugging or review

---

### Requirement: MCP Tool Integration
The system SHALL expose semantic search through well-designed MCP tools.

#### Scenario: Simple search with minimal parameters
- **GIVEN** user wants quick search
- **WHEN** user calls `memory_search("login automation")`
- **THEN** system uses sensible defaults (all types, limit 10, no filters)
- **AND** returns results immediately
- **AND** provides concise, actionable results

#### Scenario: Advanced search with all parameters
- **GIVEN** user needs precise filtering
- **WHEN** user calls `memory_search(query="login", memory_types=["screen", "action"], limit=20, filters={"success": true, "after": "2023-10-01"}, min_similarity=0.7)`
- **THEN** system applies all filters correctly
- **AND** returns exactly matching results
- **AND** provides detailed result metadata

#### Scenario: Handle empty search results gracefully
- **GIVEN** search query matches no memories
- **WHEN** user searches for very specific/rare term
- **THEN** system returns empty results with helpful message
- **AND** suggests broadening search criteria
- **AND** provides similar query suggestions based on available memories
