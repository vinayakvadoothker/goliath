# Contracts

**Single source of truth for all data structures and API contracts.**

## Files

- **`types.ts`** - Shared TypeScript types (WorkItem, Human, Decision, etc.)
- **`openapi.yaml`** - OpenAPI specification (to be created)
- **`llm_prompts.md`** - LLM prompt patterns documentation (to be created)

## Usage

**TypeScript/JavaScript:**
```typescript
import { WorkItem, Human, Decision } from '../contracts/types';
```

**Python:**
- Use Pydantic models that match these types
- Reference this file when creating models

## Rules

1. **Never break existing contracts** - Use versioning if needed
2. **All changes must be approved** - This affects all services
3. **Document all changes** - Update this README

