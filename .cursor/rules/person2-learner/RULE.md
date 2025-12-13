---
description: "Standards for Learner Service. Focus on idempotency, time-windowed calculations, and the learning loop accuracy."
alwaysApply: false
globs:
  - "services/learner/**"
---

# Cursor Rules for Person 2: Learner Service

## Core Principles

**You are building the memory of the system. The learning loop is THE core differentiator. It must be accurate, fast, and reliable.**

### Learning Loop Standards

1. **Idempotency is critical**
   - Same `event_id` must never be processed twice
   - Use database constraints (UNIQUE on event_id)
   - Check for duplicates before processing
   - Return clear status if already processed (409 Conflict)

2. **Time-windowed calculations**
   - Only count outcomes in last 90 days
   - Use efficient date range queries (indexed on timestamp)
   - Handle timezone conversions correctly (store UTC, convert on display)
   - Decay calculations must be deterministic

3. **Stats update accuracy**
   - All updates must be atomic (use transactions)
   - Handle concurrent updates correctly (use row-level locking if needed)
   - Validate all inputs before updating
   - Never update stats with invalid data

4. **Asymmetric learning**
   - Transfers are worse than resolves (penalty is larger: -0.15 vs +0.1)
   - This must be clearly documented and tested
   - Edge cases: what if fit_score goes negative? (clamp to 0.0)
   - Edge cases: what if fit_score exceeds 1.0? (clamp to 1.0)

### Database Standards

1. **Schema design**
   - All tables must have primary keys
   - Foreign keys must be properly indexed
   - Use composite indexes for common queries (human_id + service)
   - Use partial indexes for filtered queries (active humans only)
   - Timestamps must be indexed for time-windowed queries

2. **Query optimization**
   - Never use `SELECT *` - always specify columns
   - Use JOINs instead of N+1 queries
   - Use EXPLAIN to analyze query plans
   - Index all WHERE clause columns
   - Use LIMIT on all queries that could return large result sets

3. **Transaction management**
   - Use transactions for multi-step operations
   - Keep transactions short (don't hold locks for long)
   - Handle deadlocks gracefully (retry with exponential backoff)
   - Never commit partial updates

4. **Data integrity**
   - Foreign key constraints must be enforced
   - Check constraints for valid ranges (fit_score: 0.0-1.0)
   - NOT NULL constraints where appropriate
   - Default values must be sensible (fit_score: 0.5)

### Outcome Processing Standards

1. **Input validation**
   - Validate event_id format (must be unique, non-empty)
   - Validate outcome type (must be: resolved, reassigned, escalated)
   - Validate actor_id exists in humans table
   - Validate service exists
   - Validate timestamp format (ISO 8601)

2. **Processing logic**
   - Check for duplicates first (fast path)
   - Get or create stats record (upsert pattern)
   - Calculate deltas correctly (old value → new value)
   - Update all related tables atomically (transaction)
   - Create knowledge graph edges
   - Update embeddings in Weaviate

3. **Error handling**
   - If human doesn't exist, create it (don't fail)
   - If service doesn't exist, log warning but continue
   - If duplicate event_id, return 409 Conflict (don't reprocess)
   - If database error, rollback transaction and return 500
   - Never lose an outcome (if processing fails, log and retry)

### Stats Calculation Standards

1. **Fit score calculation**
   - Must be deterministic (same inputs → same output)
   - Handle edge cases: no resolves, no transfers, old data
   - Time decay must be applied correctly
   - Clamp to valid range (0.0-1.0)
   - Document formula and rationale

2. **Time decay**
   - Expertise decays over time (multiply by 0.99 per day)
   - Must be applied consistently
   - Handle edge cases: very old data (decay to minimum)
   - Document decay formula

3. **Recency boost**
   - Recent activity matters more
   - Calculate days since last resolve correctly
   - Apply boost formula consistently
   - Handle edge cases: no last_resolved_at

### Jira Integration Standards

1. **API reliability**
   - Handle Jira API failures gracefully (retry with exponential backoff)
   - Cache responses when possible (don't re-fetch same data)
   - Use pagination correctly (handle large result sets)
   - Rate limiting: respect Jira API rate limits

2. **Data extraction**
   - Extract all required fields correctly
   - Handle missing fields gracefully (use defaults)
   - Map Jira fields to internal schema correctly
   - Validate extracted data before storing

3. **LLM entity extraction**
   - Use LLM to extract entities from ticket descriptions
   - Temperature=0 for deterministic outputs
   - Validate LLM responses before using
   - Handle malformed JSON gracefully
   - Cache LLM responses (same description = same entities)

4. **Sync strategy**
   - Initial sync: pull last 90 days of closed tickets
   - Incremental sync: poll every 5 minutes for new tickets
   - Track last sync timestamp (don't re-process old tickets)
   - Handle sync failures gracefully (log errors, continue)

### Embedding & Vector Standards

1. **Human embedding updates**
   - Aggregate embeddings from all resolved work items
   - Use weighted average (more recent = higher weight)
   - Normalize embeddings before storage
   - Update Weaviate atomically (don't leave partial updates)

2. **3D coordinate calculation**
   - PCA reduction must be deterministic
   - Cache 3D coordinates in database
   - Recalculate only when embeddings change
   - Handle edge cases: no resolved items (use default embedding)

3. **Weaviate integration**
   - Use connection pooling
   - Handle Weaviate failures gracefully (fallback to database)
   - Batch updates when possible
   - Validate all Weaviate operations

### Performance Standards

1. **Response time**
   - `GET /profiles` must respond in <500ms
   - `POST /outcomes` must respond in <1 second
   - `POST /sync/jira` can be async (return immediately, process in background)

2. **Database optimization**
   - Use indexes on all query columns
   - Use composite indexes for common queries
   - Use partial indexes for filtered queries
   - Avoid full table scans

3. **Caching strategy**
   - Cache human profiles (TTL: 5 minutes)
   - Cache Jira sync results (don't re-sync same data)
   - Invalidate cache on outcome updates
   - Use Redis or in-memory cache

### Code Quality Standards

1. **Type safety**
   - Use Python type hints for all functions
   - Use Pydantic models for validation
   - Validate all inputs before processing
   - Never use untyped dictionaries

2. **Testing**
   - Unit tests for all calculation functions
   - Integration tests for all endpoints
   - Test edge cases: no data, old data, concurrent updates
   - Test idempotency: same event_id processed twice
   - Test time-windowed calculations

3. **Error handling**
   - All errors must be logged with context
   - Return meaningful error messages
   - Never fail silently
   - Handle all edge cases

### Observability Standards

1. **Logging**
   - Log all outcome processing (event_id, type, actor_id, result)
   - Log all stats updates (human_id, service, old_value, new_value)
   - Log all Jira sync operations (tickets synced, errors)
   - Use structured logging (JSON format)
   - Include correlation IDs in all logs

2. **Metrics**
   - Track outcome processing rate
   - Track stats update latency
   - Track Jira sync duration
   - Track cache hit rate
   - Track error rate

3. **Monitoring**
   - Alert on high error rate
   - Alert on slow response times
   - Alert on duplicate event_ids (indicates bug)
   - Alert on Jira sync failures

### Security Standards

1. **Data protection**
   - Never log sensitive data (passwords, tokens)
   - Encrypt sensitive data at rest (if required)
   - Use parameterized queries (prevent SQL injection)
   - Validate all inputs

2. **API security**
   - Rate limiting on all endpoints
   - Input validation on all endpoints
   - Error messages don't leak sensitive info
   - CORS properly configured

### Documentation Standards

1. **Code documentation**
   - All functions must have docstrings
   - Explain complex calculations with comments
   - Document all formulas and rationale
   - Include examples in docstrings

2. **API documentation**
   - OpenAPI spec must be complete
   - Include request/response examples
   - Document all error codes
   - Document rate limits

### Testing Checklist

- [ ] Unit tests for fit_score calculation
- [ ] Unit tests for time decay
- [ ] Unit tests for outcome processing
- [ ] Integration tests for all endpoints
- [ ] Test idempotency (same event_id twice)
- [ ] Test time-windowed calculations
- [ ] Test edge cases (no data, old data, concurrent updates)
- [ ] Test Jira sync (initial and incremental)
- [ ] Test embedding updates
- [ ] Test performance (response time <500ms)

### Code Review Checklist

Before submitting code, ensure:
- [ ] All tests pass
- [ ] No linter errors
- [ ] Code is properly typed
- [ ] Error handling is comprehensive
- [ ] Idempotency is guaranteed
- [ ] Time-windowed calculations are correct
- [ ] Database queries are optimized
- [ ] Logging is appropriate
- [ ] Documentation is updated
- [ ] Performance is acceptable

---

**Remember: The learning loop is THE core differentiator. It must be accurate, fast, and reliable. Every outcome must be processed correctly, every stat must be updated accurately, every edge case must be handled.**

