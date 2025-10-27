# Design: Gemini Vision AI Integration

## Architecture Overview

This design extends vision-mcp with AI-powered screen analysis while maintaining the existing simple, focused architecture. The system adds three new abstraction layers (Provider, Quota, Config) that work alongside existing vision tools.

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                    │
│              (Claude Code ↔ Vision MCP)                  │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                  Vision MCP Server                       │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │  Existing Tools      │  │  New AI Tools            │ │
│  │  - capture_screen    │  │  - analyze_screen        │ │
│  │  - capture_region    │  │  - find_element_ai       │ │
│  │  - extract_text      │  │  - interpret_content     │ │
│  │  - find_element      │  │  - compare_screens       │ │
│  │  - wait_for_element  │  │  - analyze_sequence      │ │
│  │  - get_screen_info   │  │  - get_quota_status      │ │
│  └──────────────────────┘  └──────────────────────────┘ │
│                            ↕                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Provider Abstraction Layer                 │ │
│  │  ┌──────────────┐  ┌──────────────┐               │ │
│  │  │ Router       │→ │ Provider     │               │ │
│  │  │ - Select     │  │ Registry     │               │ │
│  │  │ - Fallback   │  │              │               │ │
│  │  │ - Load Bal.  │  └──────────────┘               │ │
│  │  └──────────────┘                                  │ │
│  └────────────────────────────────────────────────────┘ │
│                            ↕                              │
│  ┌─────────────┬──────────────┬─────────────┬────────┐ │
│  │ Gemini      │ Ollama       │ Future      │ Future │ │
│  │ Provider    │ Provider     │ Claude      │ GPT-4V │ │
│  └─────────────┴──────────────┴─────────────┴────────┘ │
│                            ↕                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Quota Manager                              │ │
│  │  - Track usage (persistent SQLite)                 │ │
│  │  - Predict exhaustion                              │ │
│  │  - Trigger fallback                                │ │
│  └────────────────────────────────────────────────────┘ │
│                            ↕                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Configuration Manager                      │ │
│  │  - Load YAML + env vars                            │ │
│  │  - Validate schema                                 │ │
│  │  - Hot reload                                      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────┬──────────────┬─────────────────────────┐
│ Gemini API  │ Ollama Local │ ~/.claude-vision/       │
│ (Cloud)     │ (localhost)  │ - ai_config.yaml        │
│             │              │ - quota.db              │
└─────────────┴──────────────┴─────────────────────────┘
```

## Design Decisions

### 1. Provider Abstraction Pattern

**Decision:** Use abstract base class with concrete provider implementations rather than duck typing.

**Rationale:**
- Enforces consistent interface across all providers
- Enables IDE autocomplete and type checking
- Makes testing easier with mock implementations
- Clear contract for community contributions

**Trade-offs:**
- Slightly more boilerplate code
- Less flexible than duck typing
- **Accepted:** Benefits of type safety and clear interfaces outweigh flexibility needs

**Alternatives Considered:**
- **Plugin-based with duck typing:** Too loose, hard to validate implementations
- **Protocol/structural typing (PEP 544):** Less explicit, harder for contributors to understand

**Implementation:**
```python
# ai_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AnalysisResponse:
    """Standardized response from all providers"""
    analysis: str
    elements: List[Dict[str, Any]]
    confidence: float
    provider: str
    tokens_used: Optional[int] = None
    cached: bool = False

@dataclass
class ProviderCapabilities:
    """What this provider can do"""
    multimodal: bool
    streaming: bool
    batch: bool
    max_image_size: int
    max_tokens: int
    supports_video: bool = False

class AbstractProvider(ABC):
    """Base class all providers must implement"""

    @abstractmethod
    async def analyze_image(
        self,
        image: bytes,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisResponse:
        """Analyze image with AI model"""
        pass

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is operational"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier"""
        pass
```

### 2. Quota Storage Mechanism

**Decision:** Use SQLite for persistent quota tracking instead of in-memory or file-based.

**Rationale:**
- Atomic operations prevent race conditions
- ACID guarantees for concurrent requests
- Efficient queries for trend analysis
- Standard Python sqlite3 module (no external deps)
- Small file size for quota data
- Easy to inspect/debug with sqlite3 CLI

**Trade-offs:**
- Slightly more complex than JSON file
- Requires database initialization
- **Accepted:** Benefits of reliability and performance worth it

**Alternatives Considered:**
- **JSON file with file locking:** Prone to corruption, slow for concurrent access
- **Redis/external DB:** Overkill, adds deployment complexity
- **In-memory only:** Loses quota tracking on restart

**Schema:**
```sql
CREATE TABLE quota_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    requests INTEGER DEFAULT 1,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    quota_period TEXT NOT NULL -- "2025-10-25" for daily
);

CREATE INDEX idx_provider_period ON quota_usage(provider, quota_period);

CREATE TABLE quota_config (
    provider TEXT PRIMARY KEY,
    max_requests INTEGER,
    max_tokens INTEGER,
    period_type TEXT, -- "daily", "hourly", "monthly"
    reset_time TEXT -- "00:00 UTC"
);
```

### 3. Fallback Strategy

**Decision:** Implement configurable fallback chain with automatic retry and provider health tracking.

**Rationale:**
- Maximizes availability - system keeps working even when providers fail
- Respects user preferences via priority configuration
- Automatic recovery when providers restore
- Transparent to end users (metadata indicates which provider used)

**Trade-offs:**
- More complex routing logic
- Potential for inconsistent results across providers
- **Accepted:** Availability more important than perfect consistency

**Fallback Algorithm:**
```python
async def route_request(request: AnalysisRequest) -> AnalysisResponse:
    """Route request through fallback chain"""
    providers = get_available_providers_by_priority()

    for provider in providers:
        # Check quota
        if not quota_manager.has_quota(provider.name):
            log_skip(provider.name, reason="quota_exhausted")
            continue

        # Check health
        if not provider_health.is_healthy(provider.name):
            log_skip(provider.name, reason="unhealthy")
            continue

        # Try this provider with retries
        for attempt in range(MAX_RETRIES):
            try:
                response = await provider.analyze_image(
                    request.image, request.prompt
                )
                quota_manager.record_usage(provider.name, response.tokens_used)
                return response

            except QuotaExceededError:
                quota_manager.mark_exhausted(provider.name)
                break  # Try next provider

            except TemporaryError as e:
                if attempt < MAX_RETRIES - 1:
                    await exponential_backoff(attempt)
                else:
                    provider_health.mark_unhealthy(provider.name)
                    break

            except PermanentError as e:
                provider_health.mark_unhealthy(provider.name)
                break

    # All providers failed
    raise AllProvidersUnavailableError()
```

### 4. Configuration Management

**Decision:** YAML file with environment variable override and Pydantic validation.

**Rationale:**
- YAML is human-readable and supports comments
- Environment variables for secrets (API keys) prevent committing credentials
- Pydantic provides automatic validation with clear error messages
- Single source of truth with clear precedence order
- Supports hot reload for operational flexibility

**Configuration Precedence (highest to lowest):**
1. Environment variables (`GEMINI_API_KEY`)
2. Config file (`~/.claude-vision/ai_config.yaml`)
3. Default values in code

**Example Configuration:**
```yaml
# ~/.claude-vision/ai_config.yaml
providers:
  gemini:
    enabled: true
    api_key: ${GEMINI_API_KEY}  # Loaded from environment
    model: gemini-2.5-flash
    priority: 1  # Higher = preferred
    quota:
      max_requests: 250
      period: daily
      reset_time: "00:00 UTC"

  ollama:
    enabled: true
    url: http://localhost:11434
    model: llama-vision
    priority: 10  # Lower = fallback
    concurrency_limit: 2

  # Future providers
  # claude:
  #   enabled: false
  #   api_key: ${CLAUDE_API_KEY}
  #   priority: 2

routing:
  strategy: priority  # priority | round-robin | least-loaded
  enable_fallback: true
  retry_attempts: 3
  retry_backoff: exponential  # exponential | linear | fixed

caching:
  enabled: true
  ttl_seconds: 300  # 5 minutes
  max_size_mb: 100
  similarity_threshold: 0.95  # Image hash similarity

optimization:
  auto_compress_images: true
  target_max_dimension: 2048
  jpeg_quality: 85
  enable_batching: false  # Experimental
```

**Pydantic Models:**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class ProviderQuotaConfig(BaseModel):
    max_requests: int = Field(gt=0)
    period: Literal["hourly", "daily", "monthly"]
    reset_time: str  # "HH:MM UTC"

class ProviderConfig(BaseModel):
    enabled: bool = True
    api_key: Optional[str] = None
    model: str
    priority: int = Field(ge=1, le=100)
    quota: Optional[ProviderQuotaConfig] = None

    @validator('api_key')
    def expand_env_vars(cls, v):
        if v and v.startswith('${') and v.endswith('}'):
            var_name = v[2:-1]
            return os.getenv(var_name)
        return v

class AIConfig(BaseModel):
    providers: Dict[str, ProviderConfig]
    routing: RoutingConfig
    caching: CachingConfig
    optimization: OptimizationConfig
```

### 5. Image Optimization Strategy

**Decision:** Intelligent compression based on content analysis with configurable quality targets.

**Rationale:**
- API costs (for paid tiers) and latency scale with image size
- Most screen analysis doesn't need 4K resolution
- Different content types have different compression needs
- User should control quality/cost trade-off

**Compression Algorithm:**
```python
def optimize_image_for_api(image: Image.Image, config: OptimizationConfig) -> bytes:
    """Intelligently compress image for API submission"""
    width, height = image.size

    # 1. Resize if too large
    if width > config.target_max_dimension or height > config.target_max_dimension:
        ratio = min(
            config.target_max_dimension / width,
            config.target_max_dimension / height
        )
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    # 2. Analyze content complexity
    complexity = analyze_image_complexity(image)

    # 3. Adjust quality based on complexity
    if complexity == "text-heavy":
        # Text needs higher quality to remain readable
        quality = max(config.jpeg_quality, 90)
    elif complexity == "simple-ui":
        # Simple UI can compress more
        quality = config.jpeg_quality
    else:  # "photo-like" or "complex"
        quality = max(config.jpeg_quality - 10, 75)

    # 4. Compress
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)

    return buffer.getvalue()

def analyze_image_complexity(image: Image.Image) -> str:
    """Determine content type for optimization"""
    # Convert to grayscale for analysis
    gray = image.convert('L')
    img_array = np.array(gray)

    # Calculate edge density (high = text/UI, low = photo)
    edges = cv2.Canny(img_array, 100, 200)
    edge_density = np.sum(edges > 0) / edges.size

    # Calculate color variety
    color_array = np.array(image)
    unique_colors = len(np.unique(color_array.reshape(-1, 3), axis=0))

    if edge_density > 0.1 and unique_colors < 50:
        return "text-heavy"
    elif edge_density > 0.05 and unique_colors < 200:
        return "simple-ui"
    else:
        return "photo-like"
```

### 6. Caching Strategy

**Decision:** Perceptual hash-based caching with TTL expiration.

**Rationale:**
- Exact match caching too restrictive (minor pixel differences = cache miss)
- Perceptual hashing detects visually similar images
- TTL prevents serving stale analysis for dynamic content
- Significant cost/latency savings for repeated queries

**Implementation:**
```python
import imagehash
from datetime import datetime, timedelta

class AnalysisCache:
    def __init__(self, config: CachingConfig):
        self.config = config
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size_bytes = config.max_size_mb * 1024 * 1024

    def get(self, image: Image.Image, prompt: str) -> Optional[AnalysisResponse]:
        """Check cache for similar analysis"""
        img_hash = str(imagehash.phash(image))
        cache_key = f"{img_hash}:{hash(prompt)}"

        if cache_key in self.cache:
            entry = self.cache[cache_key]

            # Check TTL
            if datetime.now() - entry.timestamp < timedelta(seconds=self.config.ttl_seconds):
                # Check image similarity
                similarity = imagehash.hex_to_hash(img_hash) - imagehash.hex_to_hash(entry.img_hash)
                if similarity <= (1 - self.config.similarity_threshold) * 64:
                    return entry.response

        return None

    def put(self, image: Image.Image, prompt: str, response: AnalysisResponse):
        """Cache analysis result"""
        img_hash = str(imagehash.phash(image))
        cache_key = f"{img_hash}:{hash(prompt)}"

        # Evict old entries if cache full
        self._evict_if_needed()

        self.cache[cache_key] = CacheEntry(
            img_hash=img_hash,
            timestamp=datetime.now(),
            response=response
        )
```

### 7. Error Handling Philosophy

**Decision:** Translate all provider-specific errors to standard error types with sanitized messages.

**Rationale:**
- Consistent error handling for consumers
- Prevents leaking sensitive information (API keys, internal endpoints)
- Enables smart retry logic based on error category
- Simplifies debugging with clear error taxonomy

**Error Hierarchy:**
```python
class VisionAIError(Exception):
    """Base exception for AI vision errors"""
    def __init__(self, message: str, retryable: bool, provider: Optional[str] = None):
        self.message = message
        self.retryable = retryable
        self.provider = provider
        super().__init__(message)

class QuotaExceededError(VisionAIError):
    """Provider quota exhausted"""
    def __init__(self, provider: str, reset_time: Optional[datetime] = None):
        self.reset_time = reset_time
        super().__init__(
            f"Quota exhausted for {provider}. Resets at {reset_time}",
            retryable=False,
            provider=provider
        )

class TemporaryError(VisionAIError):
    """Temporary failure, retry may succeed"""
    pass

class PermanentError(VisionAIError):
    """Permanent failure, retry will not help"""
    pass

class AuthenticationError(PermanentError):
    """Invalid or missing API credentials"""
    pass

class ContentPolicyError(PermanentError):
    """Content violates provider policy"""
    pass
```

**Error Translation Example:**
```python
def translate_gemini_error(e: Exception) -> VisionAIError:
    """Translate Gemini API errors to standard errors"""
    error_msg = str(e)

    if "quota" in error_msg.lower() or "429" in error_msg:
        # Extract reset time if available
        reset_time = extract_reset_time(error_msg)
        return QuotaExceededError("gemini", reset_time)

    elif "401" in error_msg or "API key" in error_msg:
        return AuthenticationError(
            "Invalid Gemini API key. Check GEMINI_API_KEY environment variable.",
            retryable=False,
            provider="gemini"
        )

    elif "content policy" in error_msg.lower() or "safety" in error_msg.lower():
        return ContentPolicyError(
            "Image content violates Gemini safety policies",
            retryable=False,
            provider="gemini"
        )

    elif "503" in error_msg or "timeout" in error_msg.lower():
        return TemporaryError(
            "Gemini API temporarily unavailable",
            retryable=True,
            provider="gemini"
        )

    else:
        return PermanentError(
            f"Gemini API error: {sanitize_error(error_msg)}",
            retryable=False,
            provider="gemini"
        )
```

## Data Flow Examples

### Example 1: Successful Analysis with Gemini

```
1. User calls analyze_screen("What buttons are visible?")
2. MCP server captures screenshot (or uses provided image)
3. Router checks quota for Gemini (200/250 used ✓)
4. Router checks cache (miss)
5. Image optimized (4K → 2K, 8MB → 500KB)
6. GeminiProvider.analyze_image() called
7. Gemini API request (latency: 1.2s)
8. Response parsed and standardized
9. Quota manager records usage (201/250)
10. Result cached (key: img_hash+prompt_hash)
11. Response returned to user
```

### Example 2: Fallback to Ollama (Quota Exhausted)

```
1. User calls find_element_ai("submit button")
2. Router checks quota for Gemini (250/250 exhausted ✗)
3. Router tries next provider: Ollama
4. OllamaProvider.analyze_image() called
5. Local llama-vision model inference (latency: 8s)
6. Response parsed and standardized (marks provider="ollama")
7. Result returned to user with metadata indicating fallback
```

### Example 3: Cache Hit

```
1. User calls analyze_screen("What buttons are visible?")
2. Same screenshot as 2 minutes ago
3. Router checks cache
4. Perceptual hash match found (similarity: 0.98 > 0.95 threshold)
5. TTL check (2min < 5min TTL ✓)
6. Cached response returned immediately (latency: <10ms)
7. No API call, no quota usage
```

## Security Considerations

### API Key Management
- **Never log API keys** - sanitize all log output
- **Use environment variables** - don't commit keys to git
- **Validate key format** - fail fast on invalid keys
- **Rotation support** - hot reload config when keys change

### Content Safety
- **Respect provider safety filters** - don't retry on policy violations
- **Audit logging** - record all analysis requests for compliance
- **User warnings** - clearly communicate when content may be sensitive

### Rate Limiting
- **Honor provider limits** - never exceed documented rate limits
- **Implement backoff** - exponential backoff on rate limit errors
- **Local enforcement** - track quota locally before API calls

## Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Analysis latency (Gemini) | <3s | Acceptable for interactive use |
| Analysis latency (Ollama) | <10s | Local model trade-off |
| Cache hit ratio | >30% | Common workflows repeat screens |
| Image compression ratio | 5:1 - 10:1 | Balance quality vs API cost |
| Quota prediction accuracy | ±5% | Reliable fallback triggering |
| Provider failover time | <500ms | Fast recovery from failures |

## Testing Strategy

### Unit Tests
- Mock provider implementations for isolation
- Test quota tracking edge cases (concurrent, reset timing)
- Test error translation for all providers
- Test caching eviction policies

### Integration Tests
- Real Gemini API with test quota
- Local Ollama for fallback testing
- Configuration validation scenarios
- Hot reload behavior

### Performance Tests
- Benchmark caching effectiveness
- Measure analysis latency distribution
- Load test quota tracking under concurrency
- Memory usage with large cache

## Migration & Rollback

### Rollback Plan
If issues arise, reverting is simple:
1. Remove new AI tools from MCP server (they're isolated)
2. Existing basic vision tools unaffected
3. Remove AI dependencies from requirements.txt
4. Delete AI configuration files

### Backward Compatibility Guarantees
- All existing MCP tools unchanged
- No breaking changes to APIs
- Configuration is opt-in
- Can run without any AI providers configured (basic vision tools only)

## Future Extensions

This design supports future enhancements:

1. **Additional Providers:** Claude, GPT-4V, Azure Vision easily added via provider interface
2. **Streaming Responses:** Provider interface can support async streaming
3. **Video Analysis:** Extend to multi-frame sequences
4. **Custom Models:** Fine-tuned models via Ollama provider
5. **Distributed Quota:** Share quota across multiple vision-mcp instances
6. **Cost Tracking:** Track actual costs for paid tiers

## Open Questions

1. **Should we support streaming responses?**
   - Pros: Better UX for long analyses
   - Cons: Adds complexity, not all providers support it
   - **Recommendation:** Defer to v2, implement basic batch mode first

2. **Should cache be shared across MCP instances?**
   - Pros: Better hit ratio in multi-user environments
   - Cons: Requires Redis or similar infrastructure
   - **Recommendation:** Start with local cache, add distributed cache in v2 if needed

3. **Should we implement request queuing for rate limit compliance?**
   - Pros: Never exceed rate limits
   - Cons: Adds latency and complexity
   - **Recommendation:** Start with fail-fast on rate limits, add queuing if users request it
