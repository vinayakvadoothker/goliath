---
description: "Standards for Executor and Explain Services. Focus on bounded actions, evidence quality, and fallback strategies."
alwaysApply: false
globs:
  - "services/executor/**"
  - "services/explain/**"
---

# Cursor Rules for Person 4: Executor Service + Explain Service

## Core Principles

**You are building the execution and explanation layer. Decisions are useless without execution. Trust requires explanation. Both must be reliable, fast, and clear.**

### Executor Service Standards

1. **Bounded actions only**
   - Only create Jira issues (no free-form text generation)
   - All actions must be structured and reversible
   - Never execute actions that can't be undone
   - Validate all inputs before execution

2. **Jira integration reliability**
   - Handle Jira API failures gracefully (retry with exponential backoff)
   - Fallback to database storage if Jira fails
   - Never lose an execution (if Jira fails, store in DB)
   - Use idempotent operations (same decision = same Jira issue)

3. **Mapping accuracy**
   - Service → Jira project mapping must be correct
   - Severity → Jira priority mapping must be correct
   - Human ID → Jira accountId mapping must be correct
   - Validate all mappings before execution

4. **Error handling**
   - All errors must be logged with context
   - Return meaningful error messages
   - Never fail silently
   - Handle all edge cases (missing mappings, invalid data)

5. **Fallback strategy**
   - If Jira API fails, store rendered message in database
   - UI can display fallback message
   - Retry Jira creation in background (optional)
   - Never lose an execution

### Explain Service Standards

1. **LLM-based evidence generation**
   - Use LLM for all evidence generation (not templates)
   - Temperature=0 for deterministic outputs
   - Validate all LLM responses before using
   - Handle malformed JSON gracefully

2. **Evidence quality**
   - All evidence must be factual and time-bounded
   - No global claims ("best engineer") - only contextual
   - No hallucinations - only use provided stats
   - Be specific: "Resolved 3 similar incidents" not "experienced"

3. **Contextual explanations**
   - Evidence must be specific to the decision
   - Include time windows ("last 7 days", "last 30 days")
   - Include sources ("Learner stats", "Vector similarity")
   - Explain why, not just what

4. **"Why not next best" logic**
   - Compare primary candidate to next best
   - Highlight specific differences
   - Be factual and specific
   - Never make global claims

### Code Quality Standards

1. **Type safety**
   - Use Python type hints for all functions
   - Use Pydantic models for validation
   - Validate all inputs before processing
   - Never use untyped dictionaries

2. **Testing**
   - Unit tests for all mapping functions
   - Unit tests for evidence generation
   - Integration tests for all endpoints
   - Test edge cases: missing mappings, invalid data, LLM failures
   - Test fallback scenarios: Jira down, LLM down

3. **Error handling**
   - All errors must be logged with context
   - Return meaningful error messages
   - Never fail silently
   - Handle all edge cases

### API Standards

1. **Input validation**
   - Validate all inputs before processing
   - Use Pydantic models for validation
   - Return meaningful error messages
   - Never process invalid data

2. **Response format**
   - Consistent response format across all endpoints
   - Include correlation IDs in responses
   - Return meaningful error messages
   - Include request/response examples in docs

### LLM Integration Standards

1. **Prompt engineering**
   - All prompts must be version-controlled
   - Prompts must be deterministic (temperature=0)
   - Use structured outputs (JSON schema)
   - Test prompts with edge cases

2. **Response handling**
   - Always validate LLM responses
   - Handle malformed JSON gracefully
   - Retry on transient failures
   - Cache responses when appropriate
   - Log all LLM calls with context

3. **Cost optimization**
   - Use appropriate models (GPT-4 for complex, GPT-3.5 for simple)
   - Cache responses (same input = same output)
   - Batch requests when possible
   - Monitor token usage

### Performance Standards

1. **Response time**
   - `POST /executeDecision` must respond in <2 seconds
   - `POST /explainDecision` must respond in <3 seconds (LLM call)
   - Handle timeouts gracefully
   - Use async operations for LLM calls

2. **Caching strategy**
   - Cache LLM responses (same input = same output)
   - Cache Jira project mappings
   - Invalidate cache on updates
   - Use Redis or in-memory cache

### Observability Standards

1. **Logging**
   - Log all executions (decision_id, jira_issue_key, result)
   - Log all evidence generation (decision_id, evidence_count, latency)
   - Log all LLM calls (prompt, response, latency, cost)
   - Use structured logging (JSON format)
   - Include correlation IDs in all logs

2. **Metrics**
   - Track execution success rate
   - Track evidence generation latency
   - Track LLM call latency and cost
   - Track error rate
   - Track cache hit rate

3. **Monitoring**
   - Alert on high error rate
   - Alert on slow response times
   - Alert on Jira API failures
   - Alert on LLM API failures

### Security Standards

1. **Input validation**
   - Validate all inputs before processing
   - Prevent injection attacks
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

### Executor Service Specific Standards

1. **Jira issue creation**
   - Format Jira issue correctly
   - Include all required fields
   - Include evidence in description
   - Link back to WorkItem

2. **Mapping validation**
   - Validate all mappings before execution
   - Handle missing mappings gracefully
   - Log mapping errors with context
   - Never execute with invalid mappings

3. **Fallback handling**
   - Store fallback message in database
   - Format fallback message clearly
   - Include all relevant information
   - Make it actionable

### Explain Service Specific Standards

1. **Evidence generation**
   - Generate 5-7 evidence bullets
   - All evidence must be factual
   - All evidence must be time-bounded
   - Include sources

2. **"Why not next best" logic**
   - Compare primary to next best
   - Highlight specific differences
   - Be factual and specific
   - Never make global claims

3. **Constraints summary**
   - List all constraints checked
   - Show pass/fail status
   - Include reasons
   - Format clearly

### Testing Checklist

- [ ] Unit tests for mapping functions
- [ ] Unit tests for evidence generation
- [ ] Integration tests for all endpoints
- [ ] Test edge cases: missing mappings, invalid data, LLM failures
- [ ] Test fallback scenarios: Jira down, LLM down
- [ ] Test evidence quality (factual, time-bounded, specific)
- [ ] Test "why not next best" logic
- [ ] Test performance (response time <2 seconds)

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
- [ ] Evidence is factual and time-bounded
- [ ] Fallback strategy is implemented

---

**Remember: Decisions are useless without execution. Trust requires explanation. Both must be reliable, fast, and clear. Never lose an execution, never generate false evidence, never fail silently.**

