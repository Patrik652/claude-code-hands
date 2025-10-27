# Project Context

## Purpose

Claude Vision & Hands is an open-source system that gives Claude Code the ability to see the screen and control the computer through MCP (Model Context Protocol) servers. The project aims to provide computer vision and automation capabilities while maintaining simplicity, reliability, and accessibility.

**Core Goals:**
- Enable Claude Code to perceive and interact with any desktop environment
- Maintain 100% open source with MIT license
- Provide production-ready reliability with safety features
- Keep architecture simple and extensible

## Tech Stack

### Core Technologies
- **Python 3.8+** - Primary language for MCP servers
- **FastMCP** - MCP protocol implementation
- **OpenCV** - Computer vision operations
- **PaddleOCR** - Text extraction from screenshots
- **mss** - High-performance screen capture (70-150 FPS)
- **PyAutoGUI** - Mouse and keyboard automation
- **Pydantic** - Data validation and settings management

### Infrastructure
- **Docker** - Containerized deployment with VNC support
- **SQLite** - Lightweight persistent storage (for quota tracking, etc.)
- **YAML** - Human-readable configuration files

### Optional/Future
- **Google Gemini API** - AI-powered vision analysis
- **Ollama** - Local AI model serving
- **Redis** - Distributed caching (future)

## Project Conventions

### Code Style
- **Python:** Follow PEP 8 with Black formatter
- **Line length:** 100 characters max
- **Imports:** Standard library, third-party, local (separated by blank lines)
- **Type hints:** Required for all public functions and class methods
- **Docstrings:** Google-style docstrings for all public APIs

### Naming Conventions
- **Files:** `snake_case.py` (e.g., `quota_manager.py`)
- **Classes:** `PascalCase` (e.g., `GeminiProvider`)
- **Functions/methods:** `snake_case` (e.g., `analyze_screen()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **MCP tools:** `snake_case` matching function names

### Architecture Patterns

**MCP Server Pattern:**
- Each server is a single Python file with `@app.tool()` decorated functions
- Tools are stateless when possible; shared state via module-level singletons
- Lazy initialization for expensive resources (OCR engine, AI models)
- Graceful degradation when optional features unavailable

**Abstraction Layers:**
- Use abstract base classes for provider/plugin interfaces
- Keep abstractions thin - only what's truly needed
- Prefer composition over inheritance
- Design for testability with dependency injection

**Error Handling:**
- Raise exceptions for errors, don't return error codes
- Use custom exception hierarchy for domain errors
- Log all errors with context for debugging
- Return user-friendly error messages via MCP responses

### Testing Strategy

**Unit Tests:**
- Test business logic in isolation with mocks
- 80%+ coverage for core functionality
- Focus on edge cases and error paths

**Integration Tests:**
- Test with real dependencies where practical (Ollama, SQLite)
- Use test API keys for external services (separate quota)
- Mock external APIs for CI/CD reliability

**Manual Testing:**
- Test actual screen capture and automation on target platforms
- Verify cross-platform behavior (Linux/X11, Windows, macOS)
- Test Docker deployment scenarios

### Git Workflow

**Branch Strategy:**
- `main` - Production-ready code, always deployable
- Feature branches from main: `feature/short-description` or `add-feature-name`
- No direct commits to main

**Commit Conventions:**
- Conventional Commits format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Examples:
  - `feat(vision): add AI-powered screen analysis`
  - `fix(quota): handle quota reset timing edge case`
  - `docs(readme): update Gemini API setup instructions`

## Domain Context

### MCP (Model Context Protocol)
- Protocol for AI assistants to interact with external tools/services
- Tools are async Python functions decorated with `@app.tool()`
- Input/output via JSON-compatible types (Pydantic models recommended)
- Claude Code discovers and calls tools automatically

### Computer Vision Concepts
- **Screen capture:** Grabbing pixels from display (mss library)
- **OCR (Optical Character Recognition):** Extracting text from images
- **Template matching:** Finding UI elements by comparing image patches
- **Perceptual hashing:** Detecting visually similar images despite minor differences

### AI Vision Analysis
- **Multimodal models:** AI models that understand both images and text
- **Semantic understanding:** Interpreting meaning, not just pixels
- **Zero-shot detection:** Finding elements without pre-training on specific UI

### Quota Management
- **Free tier limits:** API providers offer limited free usage (e.g., 250 req/day)
- **Rate limiting:** Restricting request frequency to avoid overload
- **Fallback chains:** Automatic switching to backup providers when primary unavailable

## Important Constraints

### Performance Requirements
- Screen capture: 70-150 FPS (existing capability)
- OCR extraction: 50-200ms per region
- AI analysis: <3s for cloud APIs, <10s for local models
- Mouse/keyboard actions: <50ms latency

### Safety Requirements
- Failsafe mechanism (move mouse to corner to abort)
- Rate limiting (100 actions/minute for automation)
- Boundary checks on all coordinate inputs
- Audit logging for all actions
- Protection for sensitive UI areas (configurable forbidden zones)

### Platform Support
- **Primary:** Linux with X11
- **Secondary:** Windows, macOS
- **Experimental:** Wayland support
- Docker deployment for consistent environment

### Backward Compatibility
- Existing MCP tools must never break
- Configuration changes are additive only
- Deprecation warnings before removing features
- Migration guides for major changes

### Cost Constraints
- Prefer free/open-source solutions
- When using paid APIs, provide free tier options
- Always offer local fallback alternatives
- Cost-conscious defaults (image compression, caching)

## External Dependencies

### APIs
- **Google Gemini API** (optional): AI vision analysis
  - Free tier: 250 requests/day
  - Requires API key from Google AI Studio
  - Rate limits: 60 requests/minute

### Local Services
- **Ollama** (optional): Local AI model serving
  - Runs on localhost:11434
  - Models: llama-vision, bakllava
  - No API key required

### System Dependencies
- **X11** (Linux): Required for screen capture and automation
- **GPU** (optional): CUDA for accelerated OCR and local AI
- **VNC** (Docker): Remote desktop access in containerized deployment

## Development Guidelines

### Adding New MCP Tools
1. Define tool function with type hints and docstring
2. Decorate with `@app.tool()`
3. Implement error handling and logging
4. Add unit tests with mocks
5. Update README with usage examples
6. Ensure backward compatibility

### Adding New AI Providers
1. Extend `AbstractProvider` base class
2. Implement required interface methods
3. Add error translation for provider-specific errors
4. Register in provider registry
5. Add configuration schema
6. Document setup instructions and limitations

### Configuration Changes
1. Update Pydantic models first
2. Add default values for new fields
3. Update example config files
4. Document in configuration reference
5. Ensure hot reload support

### Performance Optimization
1. Profile before optimizing (don't guess)
2. Add benchmarks for critical paths
3. Document trade-offs in design.md
4. Make optimization configurable when possible
5. Measure impact and update performance targets
