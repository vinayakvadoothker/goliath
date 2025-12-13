---
description: "Standards for Ingest and Monitoring Services. Focus on normalization, reliability, error handling, and LLM preprocessing."
alwaysApply: false
globs:
  - "services/ingest/**"
  - "services/monitoring/**"
---

# Cursor Rules for Person 3: Ingest Service + Monitoring Service

## Core Principles

**You are building the ingestion layer. All work items flow through here. It must be reliable, fast, and handle all edge cases gracefully.**

### Ingest Service Standards

1. **Normalization is critical**
   - All sources must map to canonical WorkItem format
   - Validate all inputs before creating WorkItem
   - Handle missing fields gracefully (use defaults)
   - Never create WorkItem with invalid data

2. **Single source of truth**
   - All work items must be stored in Ingest database
   - Never duplicate work items (check for duplicates before creating)
   - Use unique constraints on work_item_id
   - Handle race conditions (concurrent creation of same work item)

3. **LLM preprocessing**
   - All descriptions must be preprocessed with LLM
   - Store both raw_log and cleaned description
   - Handle LLM failures gracefully (use raw description if LLM fails)
   - Cache LLM responses (same input = same output)
   - Temperature=0 for deterministic outputs

4. **Embedding generation**
   - Generate embeddings for all work items
   - Store in Weaviate for vector similarity search
   - Cache embeddings (don't regenerate for same text)
   - Handle embedding failures gracefully (log error, continue)

5. **Outcome forwarding**
   - All outcomes must be forwarded to Learner
   - Handle Learner failures gracefully (retry with exponential backoff)
   - Never lose an outcome (if forwarding fails, log and retry)
   - Use idempotent event_id for deduplication

### Monitoring Service Standards

1. **Continuous operation**
   - Monitoring loop must run continuously
   - Handle errors gracefully (don't crash on single error)
   - Log all errors with context
   - Restart monitoring loop on failure

2. **Error detection**
   - Detect errors based on configurable patterns
   - Determine severity correctly (sev1, sev2, sev3, sev4)
   - Handle different error types (burst, gradual, intermittent)
   - Never create duplicate work items for same error

3. **LLM preprocessing**
   - Preprocess all error logs with LLM
   - Clean and normalize log messages
   - Extract key information
   - Handle LLM failures gracefully (use raw log if LLM fails)

4. **WorkItem creation**
   - Create WorkItem via Ingest service
   - Handle Ingest failures gracefully (retry with exponential backoff)
   - Never lose an error (if creation fails, log and retry)
   - Use correlation IDs for tracking

### Database Standards

1. **Schema design**
   - All tables must have primary keys
   - Foreign keys must be properly indexed
   - Use composite indexes for common queries
   - Timestamps must be indexed for time-windowed queries

2. **Query optimization**
   - Never use `SELECT *` - always specify columns
   - Use indexes on all WHERE clause columns
   - Use LIMIT on all queries that could return large result sets
   - Use EXPLAIN to analyze query plans

3. **Transaction management**
   - Use transactions for multi-step operations
   - Keep transactions short
   - Handle deadlocks gracefully
   - Never commit partial updates

### API Standards

1. **Input validation**
   - Validate all inputs before processing
   - Use Pydantic models for validation
   - Return meaningful error messages
   - Never process invalid data

2. **Error handling**
   - All errors must be logged with context
   - Return appropriate HTTP status codes
   - Never expose internal implementation details
   - Handle all edge cases

3. **Response format**
   - Consistent response format across all endpoints
   - Include correlation IDs in responses
   - Return meaningful error messages
   - Include request/response examples in docs

### LLM Integration Standards

1. **Prompt engineering**
   - All prompts must be version-controlled
   - Prompts must be deterministic (temperature=0)
   - Use structured outputs when possible
   - Test prompts with edge cases

2. **Response handling**
   - Always validate LLM responses
   - Handle malformed JSON gracefully
   - Retry on transient failures
   - Cache responses when appropriate
   - Log all LLM calls with context

3. **Cost optimization**
   - Use appropriate models
   - Cache responses (same input = same output)
   - Batch requests when possible
   - Monitor token usage

### Performance Standards

1. **Response time**
   - `POST /ingest/demo` must respond in <1 second
   - `GET /work-items` must respond in <500ms
   - `GET /work-items/:id` must respond in <200ms
   - `POST /work-items/:id/outcome` must respond in <1 second

2. **Database optimization**
   - Use indexes on all query columns
   - Use composite indexes for common queries
   - Avoid full table scans
   - Use connection pooling

3. **Caching strategy**
   - Cache LLM responses
   - Cache embeddings
   - Invalidate cache on updates
   - Use Redis or in-memory cache

### Code Quality Standards

1. **Type safety**
   - Use Python type hints for all functions
   - Use Pydantic models for validation
   - Validate all inputs before processing
   - Never use untyped dictionaries

2. **Testing**
   - Unit tests for all normalization functions
   - Integration tests for all endpoints
   - Test edge cases: invalid input, missing fields, duplicate work items
   - Test error scenarios: service down, timeout, invalid input
   - Test LLM preprocessing with various inputs

3. **Error handling**
   - All errors must be logged with context
   - Return meaningful error messages
   - Never fail silently
   - Handle all edge cases

### Observability Standards

1. **Logging**
   - Log all work item creation (source, service, severity)
   - Log all outcome processing (event_id, type, actor_id)
   - Log all LLM calls (prompt, response, latency, cost)
   - Use structured logging (JSON format)
   - Include correlation IDs in all logs

2. **Metrics**
   - Track work item creation rate
   - Track outcome processing rate
   - Track LLM call latency and cost
   - Track error rate
   - Track cache hit rate

3. **Monitoring**
   - Alert on high error rate
   - Alert on slow response times
   - Alert on LLM API failures
   - Alert on duplicate work items

### Security Standards

1. **Input validation**
   - Validate all inputs before processing
   - Prevent injection attacks (SQL, NoSQL, command)
   - Sanitize all user inputs
   - Use parameterized queries

2. **Data protection**
   - Never log sensitive data
   - Encrypt sensitive data at rest (if required)
   - Use HTTPS for all API calls
   - Rate limiting on all endpoints

### Documentation Standards

1. **Code documentation**
   - All functions must have docstrings
   - Explain complex logic with comments
   - Document all configuration options
   - Include examples in docstrings

2. **API documentation**
   - OpenAPI spec must be complete
   - Include request/response examples
   - Document all error codes
   - Document rate limits

### Monitoring Service Specific Standards

1. **Error patterns**
   - Configurable error patterns (burst, gradual, intermittent)
   - Determine severity correctly
   - Handle different error types
   - Never create duplicate work items

2. **LLM preprocessing**
   - Preprocess all error logs
   - Clean and normalize messages
   - Extract key information
   - Handle failures gracefully

3. **WorkItem creation**
   - Create via Ingest service
   - Handle failures gracefully
   - Never lose an error
   - Use correlation IDs

### Testing Checklist

- [ ] Unit tests for normalization functions
- [ ] Unit tests for LLM preprocessing
- [ ] Integration tests for all endpoints
- [ ] Test edge cases: invalid input, missing fields, duplicate work items
- [ ] Test error scenarios: service down, timeout, invalid input
- [ ] Test LLM preprocessing with various inputs
- [ ] Test monitoring loop (error detection, WorkItem creation)
- [ ] Test outcome forwarding to Learner
- [ ] Test performance (response time <1 second)

### Code Review Checklist

Before submitting code, ensure:
- [ ] All tests pass
- [ ] No linter errors
- [ ] Code is properly typed
- [ ] Error handling is comprehensive
- [ ] Input validation is complete
- [ ] Logging is appropriate
- [ ] Documentation is updated
- [ ] Performance is acceptable
- [ ] Security considerations are addressed
- [ ] No hardcoded values

---

**Remember: You are the ingestion layer. All work items flow through here. It must be reliable, fast, and handle all edge cases gracefully. Never lose a work item, never create duplicates, never fail silently.**

