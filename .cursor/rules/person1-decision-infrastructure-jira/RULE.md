---
description: "Standards for Decision Engine, Infrastructure, and Jira Simulator. Focus on determinism, auditability, performance, and reliability."
alwaysApply: false
globs:
  - "services/decision/**"
  - "services/jira-simulator/**"
  - "infra/**"
  - "contracts/**"
  - "scripts/setup.sh"
  - "scripts/seed_jira_data.py"
---

# Cursor Rules for Person 1: Decision Engine + Infrastructure + Jira Simulator

## Core Principles

**You are building the brain of the system. Every decision must be deterministic, auditable, and explainable.**

### Decision Engine Standards

1. **Determinism is non-negotiable**
   - Same inputs → same outputs (except time-varying load)
   - All random operations must be seeded or deterministic
   - LLM calls use `temperature=0` for reproducibility
   - All time-dependent operations must be mockable

2. **Audit trail completeness**
   - Log every candidate considered (even filtered ones)
   - Log every constraint check with reason
   - Log every score calculation with breakdown
   - Store full decision reasoning chain in database
   - Correlation IDs must flow through all service calls

3. **Performance requirements**
   - Decision endpoint must respond in <2 seconds
   - Vector similarity search must be optimized (limit results, use indexes)
   - Cache LLM responses when possible (same input = same output)
   - Database queries must be indexed and optimized
   - Use connection pooling, never create new connections per request

4. **Error handling**
   - Never fail silently - all errors must be logged with context
   - Graceful degradation: if Learner is down, use cached profiles
   - If Weaviate is down, skip vector similarity (log warning)
   - If LLM API fails, retry with exponential backoff (max 3 retries)
   - Return meaningful error messages (not stack traces) to API consumers

5. **Scoring algorithm rigor**
   - All weights must be documented with rationale
   - Score calculations must be unit tested with edge cases
   - Handle division by zero, null values, missing data
   - Validate all inputs before processing
   - Score breakdown must be stored for audit trail

### Infrastructure Standards

1. **Docker & Containerization**
   - All services must have production-ready Dockerfiles
   - Use multi-stage builds to minimize image size
   - Never run as root user in containers
   - Health checks must be implemented (`/healthz` endpoint)
   - Environment variables must be validated on startup

2. **Database design**
   - All tables must have primary keys
   - Foreign keys must be properly indexed
   - Use transactions for multi-step operations
   - Connection pooling (min 5, max 20 connections)
   - Query timeouts (30 seconds max)
   - Never use `SELECT *` - always specify columns

3. **API contracts**
   - All endpoints must have OpenAPI documentation
   - Request/response schemas must be validated
   - Use Pydantic models for validation (FastAPI)
   - Version APIs (`/v1/` prefix for future-proofing)
   - Return consistent error response format

4. **Observability**
   - Log all service-to-service calls with correlation IDs
   - Log request duration, status code, error messages
   - Structured logging (JSON format)
   - Include context: user_id, work_item_id, decision_id in logs
   - Never log sensitive data (API keys, tokens, passwords)

5. **Security**
   - Never commit secrets to git (use .env files, .gitignore)
   - Validate all inputs (prevent injection attacks)
   - Rate limiting on all public endpoints
   - CORS must be properly configured
   - API keys must be rotated regularly

### Jira Simulator Standards

1. **API compatibility**
   - Must match Jira REST API v3 exactly
   - All endpoints must return same format as real Jira
   - JQL parser must handle all required query types
   - Error responses must match Jira's format

2. **Data consistency**
   - Foreign key constraints must be enforced
   - Cascade deletes must be handled properly
   - Transaction integrity for multi-step operations
   - Data validation before insertion

3. **Performance**
   - JQL queries must be optimized (use indexes)
   - Pagination must work correctly (startAt, maxResults)
   - Large result sets must be handled efficiently
   - Database queries must be optimized

### Code Quality Standards

1. **Type safety**
   - Use TypeScript for all contracts (`/contracts/types.ts`)
   - Use Python type hints for all functions
   - Validate types at runtime (Pydantic, TypeScript interfaces)
   - Never use `any` type in TypeScript

2. **Testing**
   - Unit tests for all algorithms (scoring, constraints, confidence)
   - Integration tests for all endpoints
   - Test edge cases: empty candidates, all filtered, zero confidence
   - Test error scenarios: service down, invalid input, timeout
   - Test determinism: same input → same output

3. **Code organization**
   - Single responsibility principle (one function = one job)
   - DRY (Don't Repeat Yourself) - extract common logic
   - Clear function names (verb + noun: `calculate_score`, `filter_candidates`)
   - Functions should be <50 lines (if longer, break it down)
   - Comments explain "why", not "what" (code should be self-documenting)

4. **Error messages**
   - Must be actionable and specific
   - Include context (what failed, why, what to do)
   - Never expose internal implementation details
   - Use structured error codes for programmatic handling

### LLM Integration Standards

1. **Prompt engineering**
   - All prompts must be version-controlled in `/contracts/llm_prompts.md`
   - Prompts must be deterministic (temperature=0)
   - Use structured outputs (JSON schema) when possible
   - Include examples in prompts for few-shot learning
   - Test prompts with edge cases

2. **Response handling**
   - Always validate LLM responses before using
   - Handle malformed JSON gracefully
   - Retry on transient failures (network, rate limits)
   - Cache responses when appropriate (same input = same output)
   - Log all LLM calls with prompt, response, latency, cost

3. **Cost optimization**
   - Use appropriate models (GPT-4 for complex, GPT-3.5 for simple)
   - Cache embeddings (don't regenerate for same text)
   - Batch requests when possible
   - Monitor token usage and costs

### Vector Database Standards

1. **Embedding generation**
   - Use consistent model (`all-mpnet-base-v2`)
   - Normalize embeddings before storage
   - Cache embeddings (don't regenerate for same text)
   - Batch embedding generation when possible

2. **Similarity search**
   - Use appropriate similarity thresholds (0.7 for production)
   - Limit results (max 10 for candidate matching)
   - Filter by service before similarity search (reduce search space)
   - Index vectors properly in Weaviate

3. **3D reduction**
   - PCA reduction must be deterministic (same input → same output)
   - Cache 3D coordinates in database
   - Recalculate only when embeddings change

### Knowledge Graph Standards

1. **Graph integrity**
   - All edges must have valid source and target nodes
   - Timestamps must be accurate (use UTC)
   - Cascade deletes must be handled properly
   - Graph queries must be optimized (use indexes)

2. **Temporal queries**
   - All edges must be timestamped
   - Support time-windowed queries (last 7 days, 30 days, 90 days)
   - Handle timezone conversions correctly
   - Optimize temporal queries with indexes

### Performance Optimization

1. **Database queries**
   - Use indexes on all foreign keys
   - Use indexes on frequently queried columns (service, severity, created_at)
   - Avoid N+1 queries (use JOINs or batch loading)
   - Use EXPLAIN to analyze query plans

2. **Caching strategy**
   - Cache human profiles (TTL: 5 minutes)
   - Cache LLM responses (same input = same output)
   - Cache embeddings (don't regenerate)
   - Invalidate cache on updates

3. **Async operations**
   - Use async/await for all I/O operations
   - Don't block on LLM calls (use async client)
   - Batch database operations when possible
   - Use connection pooling

### Documentation Standards

1. **Code documentation**
   - All public functions must have docstrings
   - Explain complex algorithms with comments
   - Document all configuration options
   - Include examples in docstrings

2. **API documentation**
   - OpenAPI spec must be complete and accurate
   - Include request/response examples
   - Document all error codes
   - Document rate limits and quotas

3. **Architecture documentation**
   - Document all design decisions
   - Explain why, not just what
   - Keep architecture diagrams up to date
   - Document all dependencies and their versions

### Security Checklist

- [ ] No secrets in code (use environment variables)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use parameterized queries)
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] Error messages don't leak sensitive info
- [ ] Authentication/authorization (if needed)
- [ ] HTTPS only (in production)
- [ ] Dependency scanning (check for vulnerabilities)

### Testing Checklist

- [ ] Unit tests for all algorithms
- [ ] Integration tests for all endpoints
- [ ] Test edge cases (empty inputs, null values, large inputs)
- [ ] Test error scenarios (service down, timeout, invalid input)
- [ ] Test determinism (same input → same output)
- [ ] Test performance (response time <2 seconds)
- [ ] Test concurrent requests (load testing)

### Code Review Checklist

Before submitting code, ensure:
- [ ] All tests pass
- [ ] No linter errors
- [ ] Code is properly typed
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate (not too verbose, not too sparse)
- [ ] Documentation is updated
- [ ] Performance is acceptable
- [ ] Security considerations are addressed
- [ ] No hardcoded values (use config/env vars)
- [ ] Code follows style guide

---

**Remember: You're building the brain. It must be reliable, fast, and trustworthy. Every decision must be explainable, every error must be handled, every edge case must be considered.**

