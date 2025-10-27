# Quota Management and Fallback

## ADDED Requirements

### Requirement: Quota Tracking
The system SHALL track API usage against provider quotas in real-time.

#### Scenario: Track request count
- **GIVEN** Gemini free tier with 250 requests/day limit
- **WHEN** AI analysis request completes
- **THEN** system increments request counter for current day
- **AND** counter persists across server restarts
- **AND** counter resets at quota renewal time (midnight UTC or provider-specific)

#### Scenario: Track token usage
- **GIVEN** provider with token-based quota (input + output tokens)
- **WHEN** API request completes
- **THEN** system records token usage from provider response
- **AND** maintains running total for current quota period
- **AND** calculates remaining quota capacity

#### Scenario: Monitor quota status
- **GIVEN** any provider with quota limits
- **WHEN** administrator calls `get_quota_status()` tool
- **THEN** system returns current usage, limit, remaining quota, and reset time
- **AND** includes usage trend (requests per hour) for capacity planning
- **AND** warns if approaching limit (e.g., >80% used)

### Requirement: Quota Prediction
The system SHALL predict quota exhaustion and proactively adjust behavior.

#### Scenario: Predict quota depletion
- **GIVEN** quota usage history and current rate
- **WHEN** system analyzes usage patterns
- **THEN** system estimates time until quota exhausted
- **AND** warns users if quota will likely run out before reset
- **AND** suggests switching to fallback provider preemptively

#### Scenario: Adjust request routing
- **GIVEN** primary provider predicted to exhaust quota in <2 hours
- **WHEN** new non-urgent requests arrive
- **THEN** system routes lower-priority requests to fallback providers
- **AND** reserves remaining quota for high-priority or primary-only features
- **AND** logs routing decisions for transparency

### Requirement: Intelligent Fallback
The system SHALL automatically fall back to alternative providers when quota exceeded or errors occur.

#### Scenario: Fallback on quota exhaustion
- **GIVEN** Gemini quota exhausted (250/250 requests used)
- **WHEN** new AI analysis request arrives
- **THEN** system automatically routes to fallback provider (Ollama)
- **AND** request succeeds without user intervention
- **AND** response metadata indicates fallback provider was used

#### Scenario: Fallback chain execution
- **GIVEN** provider priority: Gemini (primary) → Claude (secondary) → Ollama (tertiary)
- **WHEN** Gemini quota exceeded AND Claude has authentication error
- **THEN** system attempts providers in order until success
- **AND** stops at first successful provider
- **AND** logs all attempts and failures for debugging

#### Scenario: Fallback on temporary errors
- **GIVEN** primary provider returns temporary error (5xx, network timeout)
- **WHEN** error is retriable
- **THEN** system attempts retry with exponential backoff (1s, 2s, 4s)
- **AND** falls back to next provider after max retries (default 3)
- **AND** returns to primary provider when it recovers

### Requirement: Local Model Fallback
The system SHALL support falling back to local models (Ollama, LM Studio) when cloud quotas exceeded.

#### Scenario: Initialize local model
- **GIVEN** Ollama installed with llama-vision model
- **WHEN** system starts with local fallback enabled
- **THEN** system verifies Ollama connectivity and model availability
- **AND** local provider registered with lowest priority
- **AND** warns if local model unavailable

#### Scenario: Route to local model
- **GIVEN** all cloud provider quotas exhausted
- **WHEN** AI analysis request arrives
- **THEN** system routes to Ollama with appropriate prompt formatting
- **AND** adjusts expectations for response quality/format
- **AND** clearly indicates local model usage in response metadata

#### Scenario: Local model performance optimization
- **GIVEN** request routed to local Ollama model
- **WHEN** processing analysis
- **THEN** system uses GPU acceleration if available
- **AND** implements request queuing to avoid overloading local resources
- **AND** respects configured concurrency limits (default 2)

### Requirement: Quota Reset Handling
The system SHALL properly handle quota resets and provider recovery.

#### Scenario: Detect quota reset
- **GIVEN** quota period ends (e.g., midnight UTC for daily quota)
- **WHEN** new period begins
- **THEN** system resets quota counters to zero
- **AND** re-enables providers that were disabled due to quota exhaustion
- **AND** logs quota reset event

#### Scenario: Automatic provider restoration
- **GIVEN** primary provider previously disabled due to quota exhaustion
- **WHEN** quota resets or provider health check succeeds
- **THEN** system automatically re-enables provider
- **AND** new requests route according to normal priority
- **AND** notifies administrators of restoration

### Requirement: Graceful Degradation
The system SHALL provide degraded service rather than complete failure when all AI providers unavailable.

#### Scenario: All providers unavailable
- **GIVEN** all AI providers exhausted or offline
- **WHEN** AI analysis requested
- **THEN** system returns error indicating AI unavailable
- **AND** suggests falling back to basic vision tools (OCR, template matching)
- **AND** optionally provides rule-based heuristics as poor substitute
- **AND** queues request for retry when providers recover

#### Scenario: Partial capability degradation
- **GIVEN** only local model available (limited capabilities)
- **WHEN** request requires advanced feature unsupported by local model
- **THEN** system attempts best-effort analysis with local model
- **AND** clearly indicates limitations in response
- **AND** suggests retrying later when cloud providers available

### Requirement: Usage Reporting
The system SHALL provide detailed usage analytics and reporting for quota management.

#### Scenario: Generate usage report
- **GIVEN** 7 days of historical usage data
- **WHEN** administrator requests `generate_usage_report(period="7d")`
- **THEN** system returns report with: total requests, by-provider breakdown, quota utilization %, peak usage times, fallback frequency
- **AND** includes cost estimates if provider has pricing tiers
- **AND** recommends optimization strategies

#### Scenario: Real-time usage dashboard
- **GIVEN** vision-mcp server running
- **WHEN** monitoring dashboard queries usage metrics
- **THEN** system exposes real-time metrics: current quota %, requests/minute, provider health, active fallbacks
- **AND** metrics available via MCP tool or dedicated endpoint
- **AND** historical data retained for trend analysis (configurable retention, default 30 days)

### Requirement: Configuration Flexibility
The system SHALL allow fine-grained control over quota limits and fallback behavior.

#### Scenario: Configure custom quotas
- **GIVEN** user wants to self-impose lower quota limits
- **WHEN** configuration specifies `max_requests_per_day: 100` for Gemini
- **THEN** system enforces custom limit even if API allows 250
- **AND** falls back when custom limit reached
- **AND** custom limits help control costs or ensure availability

#### Scenario: Configure fallback strategy
- **GIVEN** configuration file with fallback settings
- **WHEN** specifying `fallback_strategy: "aggressive"` vs `"conservative"`
- **THEN** aggressive mode falls back immediately on quota warnings
- **AND** conservative mode exhausts quota before fallback
- **AND** strategy is configurable per-provider

#### Scenario: Disable fallback
- **GIVEN** user wants hard failure when primary provider unavailable
- **WHEN** configuration sets `enable_fallback: false`
- **THEN** system returns error instead of falling back
- **AND** helps identify dependency on specific provider
- **AND** useful for testing primary provider reliability
