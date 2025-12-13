# Executor Service - Jira Configuration Status

## Current Configuration

### ✅ What's Configured

**Executor Service** is currently configured to use **Jira Simulator** (local mock):

```python
# services/executor/main.py (line 168)
jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://localhost:8080")
```

**Docker Compose Configuration:**
```yaml
# infra/docker-compose.yml (line 184)
JIRA_SIMULATOR_URL: http://jira-simulator:8080
```

**Current Behavior:**
- ✅ Uses `JIRA_SIMULATOR_URL` environment variable
- ✅ Defaults to `http://localhost:8080` (Jira Simulator)
- ✅ **NO authentication** (Jira Simulator doesn't require it)
- ✅ Makes plain HTTP POST requests without headers

---

## ❌ What's Missing: Real Jira Support

**Executor Service does NOT currently support real Jira with API keys.**

If you want to use **real Jira** instead of the simulator, Executor needs:

1. **Support for `JIRA_URL`** (not just `JIRA_SIMULATOR_URL`)
2. **Authentication headers** (Basic Auth with email:API_KEY)
3. **Environment variables**: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_KEY`

---

## Comparison: Seed Script vs Executor

### Seed Script (`scripts/seed_jira_data.py`) ✅ Supports Real Jira

```python
# Uses JIRA_URL, JIRA_EMAIL, JIRA_API_KEY
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_KEY = os.getenv("JIRA_API_KEY")

def get_jira_auth_headers() -> Dict[str, str]:
    """Get authentication headers for Jira API."""
    credentials = f"{JIRA_EMAIL}:{JIRA_API_KEY}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
```

### Executor Service ❌ Only Supports Simulator

```python
# Only uses JIRA_SIMULATOR_URL, no auth
jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://localhost:8080")
# NO authentication headers
response = await client.post(f"{jira_url}/rest/api/3/issue", json=jira_issue)
```

---

## Recommended Fix

Update Executor Service to support both Jira Simulator and real Jira:

```python
# services/executor/main.py

import base64
import os

def get_jira_config():
    """Get Jira URL and authentication headers."""
    # Check if using real Jira
    jira_url = os.getenv("JIRA_URL", "").rstrip("/")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_key = os.getenv("JIRA_API_KEY")
    
    # If real Jira credentials provided, use them
    if jira_url and jira_email and jira_api_key:
        credentials = f"{jira_email}:{jira_api_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return jira_url, headers
    
    # Otherwise, use Jira Simulator (no auth)
    jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://localhost:8080")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return jira_url, headers

async def create_jira_issue_with_retry(...):
    jira_url, headers = get_jira_config()
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{jira_url}/rest/api/3/issue",
            json=jira_issue,
            headers=headers  # Add headers here
        )
```

---

## Current Status Summary

| Component | Jira Simulator | Real Jira | Status |
|-----------|---------------|-----------|--------|
| **Seed Script** | ✅ | ✅ | Supports both |
| **Executor Service** | ✅ | ❌ | **Only simulator** |
| **Learner Service** | ✅ | ✅ | Supports both (via jira_client.py) |

---

## Action Required

**If you want Executor to work with real Jira:**

1. Update `services/executor/main.py` to:
   - Check for `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_KEY`
   - Add Basic Auth headers if real Jira credentials are provided
   - Fall back to `JIRA_SIMULATOR_URL` if not provided

2. Update `infra/docker-compose.yml` to:
   - Add `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_KEY` to executor environment variables

3. Update `.env` file to:
   - Add your real Jira credentials (if using real Jira)

---

## Verification

**To check current configuration:**

```bash
# Check Executor environment variables
docker exec goliath-executor env | grep JIRA

# Check if Executor can reach Jira Simulator
docker exec goliath-executor curl http://jira-simulator:8080/healthz

# Check Executor logs for Jira URL
docker logs goliath-executor | grep -i jira
```

**Expected output (current):**
```
JIRA_SIMULATOR_URL=http://jira-simulator:8080
```

**If using real Jira (after fix):**
```
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_KEY=your-api-key
```

