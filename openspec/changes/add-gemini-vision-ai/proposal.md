# Add Gemini Vision AI Integration

## Why

The current vision-mcp server provides excellent basic computer vision capabilities (screenshot capture, OCR, template matching) but lacks AI-powered semantic understanding of screen content. Users need intelligent screen analysis to understand UI context, identify actionable elements, interpret complex layouts, and make decisions based on visual information - not just extract raw pixels and text.

Additionally, the project currently has no dependencies on paid AI services, making it more accessible. Integrating Gemini 2.5 Flash with its generous free tier (250 requests/day) provides advanced multimodal AI capabilities while maintaining the open-source ethos.

## What Changes

- **Add AI-powered screen analysis**: Integrate Google Gemini 2.5 Flash API for intelligent vision analysis
- **Create model abstraction layer**: Design provider-agnostic interface for easy model switching (Gemini, Claude, Ollama, etc.)
- **Implement quota management**: Smart fallback system when free tier quota exceeded (250 requests/day)
- **Add multimodal analysis tools**: New MCP tools for semantic screen understanding, UI element identification, and content interpretation
- **Maintain backward compatibility**: All existing MCP tools remain unchanged; new AI capabilities are additive

**Breaking Changes:** None - this is a purely additive change.

## Impact

### Affected Specs
- **ai-analysis** (NEW): AI-powered screen analysis capabilities
- **model-abstraction** (NEW): Provider-agnostic model interface
- **quota-fallback** (NEW): Intelligent quota management and fallback mechanisms

### Affected Code
- `mcp-servers/vision-mcp/server.py`: Add new MCP tools for AI analysis
- `mcp-servers/vision-mcp/requirements.txt`: Add google-generativeai SDK
- New files to create:
  - `mcp-servers/vision-mcp/ai_provider.py`: Model abstraction layer
  - `mcp-servers/vision-mcp/quota_manager.py`: Quota tracking and fallback
  - `mcp-servers/vision-mcp/config.py`: Configuration management

### Dependencies
- Add `google-generativeai>=0.3.0` for Gemini API
- Optional: `ollama` for local model fallback
- Configuration file for API keys and quota settings

### User Impact
- **Positive**: Users gain powerful AI analysis without additional cost (free tier)
- **Positive**: Easy to extend with other AI providers (Claude, GPT-4V, Ollama)
- **Neutral**: Optional feature - users can continue using basic vision tools
- **Minimal risk**: Fallback to local models when quota exceeded ensures reliability
