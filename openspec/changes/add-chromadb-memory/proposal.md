# Add ChromaDB Vector Memory for Context Persistence

## Problem Statement

Currently, Claude Vision & Hands operates in a stateless manner - each interaction starts fresh with no memory of previous sessions, screens analyzed, or actions performed. This limits the system's ability to:

1. **Learn from history** - Cannot reference past screen analyses or automation patterns
2. **Provide context** - No persistent context about user's workflows, preferences, or environment
3. **Enable semantic search** - Cannot find similar UI states or automation sequences from history
4. **Track long-term patterns** - No way to identify recurring tasks or optimize frequent operations
5. **Support multi-session workflows** - Cannot resume or reference work across different Claude Code sessions

Users working on complex, multi-step automation tasks need the system to remember:
- Previous screen states and AI analyses
- Successful automation sequences (workflows that worked)
- Failed attempts and error patterns (to avoid repeating mistakes)
- User preferences and custom configurations
- Element locations and UI patterns across applications

## Proposed Changes

Integrate **ChromaDB vector database** to provide persistent, semantically searchable memory for all system interactions:

### Core Components

1. **Vector Storage Layer** - ChromaDB integration for storing embeddings
2. **Context Persistence** - Automatic capture of screen states, actions, and results
3. **Semantic Search** - Natural language queries to find relevant past interactions
4. **Memory Management** - Configurable retention, cleanup, and quota limits

### Integration Points

- **Vision MCP**: Store AI screen analyses with embeddings
- **Hands MCP**: Record automation actions and outcomes
- **Browser MCP**: Persist ARIA trees, navigation patterns, and workflows
- **Integration MCP**: Coordinate memory across all subsystems

### Key Capabilities

- **Session Continuity**: Resume workflows across Claude Code restarts
- **Pattern Recognition**: Identify frequently used UI elements or automation sequences
- **Smart Suggestions**: Recommend actions based on similar past scenarios
- **Audit Trail**: Complete searchable history of all operations
- **Cost Optimization**: Cache AI analyses to reduce API calls

## Impact Analysis

### User Benefits
- ✅ **Persistent context** across sessions
- ✅ **Faster automation** by learning from history
- ✅ **Reduced AI costs** through intelligent caching
- ✅ **Better suggestions** based on past successes
- ✅ **Searchable audit trail** for debugging

### Technical Impact
- **New dependency**: ChromaDB (~50MB, Python package)
- **Storage requirements**: ~10-100MB per 1000 interactions (configurable)
- **Performance**: <50ms for vector search, <10ms for storage
- **Backward compatible**: Memory is optional, system works without it

### Risks & Mitigations
- **Privacy concern**: Storing screen content → Configurable data retention, local-only storage
- **Storage growth**: Unlimited memory accumulation → Auto-cleanup, configurable quotas
- **Performance degradation**: Large collections slow search → Collection partitioning, indices
- **Dependency complexity**: ChromaDB setup → Graceful degradation, optional feature

## Success Criteria

1. ✅ ChromaDB integrated and operational with <100ms query latency
2. ✅ 5+ new MCP tools for memory operations (store, search, retrieve, delete, stats)
3. ✅ Automatic memory capture for screen analyses and automation actions
4. ✅ Natural language semantic search working across all memory types
5. ✅ Configurable retention policies (time-based, size-based)
6. ✅ Zero impact when memory is disabled (backward compatibility)
7. ✅ Documentation and usage examples complete
8. ✅ Integration tests passing (storage, retrieval, search, cleanup)

## Out of Scope

- Distributed/cloud storage (local ChromaDB only in v1)
- Multi-user memory sharing (single-user focus)
- Real-time collaboration features
- Integration with external knowledge bases
- Advanced ML models for memory compression

## Dependencies

- ChromaDB Python library (chromadb>=0.4.0)
- Sentence transformers for embeddings (sentence-transformers>=2.2.0)
- No changes to existing MCP tools (additive only)

## Timeline Estimate

- **Phase 1** (Core): Vector storage + basic persistence (2-3 days)
- **Phase 2** (Search): Semantic search + MCP tools (2 days)
- **Phase 3** (Integration): Auto-capture + retention (1-2 days)
- **Total**: 5-7 days of focused development
