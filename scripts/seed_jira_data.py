#!/usr/bin/env python3
"""
Jira Seeding Script
Seeds Jira (real or simulator) with specialized users for learning framework:
- 5 specialized users, each with a specific role/expertise
- Each user has completed tasks matching their specialization
- Realistic work history (last 90 days) for capability learning

Supports two modes:
1. Local database (Jira Simulator) - if JIRA_URL is not set
2. Real Jira API - if JIRA_URL and JIRA_API_KEY are set
"""
import random
import os
import sys
import base64
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, try to install it
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "python-dotenv"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        from dotenv import load_dotenv
        load_dotenv()
    except:
        # If we can't load dotenv, just continue - env vars might be set manually
        pass

try:
    import httpx
except ImportError:
    print("⚠️  httpx not installed. Installing...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "httpx"])
    except subprocess.CalledProcessError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "httpx"])
    import httpx

try:
    from faker import Faker
except ImportError:
    print("⚠️  faker not installed. Installing...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "faker", "psycopg2-binary"])
    except subprocess.CalledProcessError:
        # Try with --break-system-packages for Python 3.13+
        print("⚠️  Trying with --break-system-packages flag...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "faker", "psycopg2-binary"])
    from faker import Faker

fake = Faker()

# Configuration
SERVICES = ["api-service", "payment-service", "frontend-app", "data-pipeline", "infrastructure"]

# ============================================================================
# 5 Specialized Users for Learning Framework
# ============================================================================
# Each user specializes in a specific domain. When incidents come in matching
# their specialization, they should be routed to them. The learning framework
# will build capability profiles based on their completed tickets.
#
# User 1: Agrim Dhingra - API Backend Specialist
#   - Role: backend-engineer
#   - Service: api-service
#   - Handles: API endpoint errors, high error rates, API authentication issues
#   - Severity: sev1, sev2 (critical API issues)
#
# User 2: ishaanbansal.dev - Frontend UI Specialist
#   - Role: frontend-engineer
#   - Service: frontend-app
#   - Handles: React component issues, UI layout problems, frontend bugs
#   - Severity: sev2, sev3 (UI/UX issues)
#
# User 3: Sahil Tallam - Infrastructure & DevOps Specialist
#   - Role: devops-engineer (Organization admin)
#   - Service: infrastructure
#   - Handles: CI/CD failures, deployment issues, infrastructure scaling
#   - Severity: sev1, sev2 (infrastructure and deployment critical)
#
# User 4: sasankgamini - Payment Systems Specialist
#   - Role: backend-engineer
#   - Service: payment-service
#   - Handles: Payment processing errors, transaction failures, PCI compliance
#   - Severity: sev1, sev2 (payment issues are always critical)
#
# User 5: Vin Vadoothker (Vinayak) - Data Pipeline Specialist
#   - Role: data-engineer
#   - Service: data-pipeline
#   - Handles: ETL failures, data processing issues, batch job problems
#   - Severity: sev2, sev3 (data pipeline issues)
# ============================================================================

SPECIALIZED_USERS = [
    {
        "display_name": "Agrim Dhingra",
        "email": "agrimd3@gmail.com",
        "role": "backend-engineer",
        "specialization": "API Backend Specialist",
        "primary_service": "api-service",
        "expertise_areas": ["API endpoints", "REST APIs", "microservices", "API performance"],
        "severity_focus": ["sev1", "sev2"],  # Handles high-severity API issues
        "issue_types": ["Bug", "Task"],
        "max_story_points": 21
    },
    {
        "display_name": "ishaanbansal.dev",
        "email": "ishaanbansal.dev@gmail.com",
        "role": "frontend-engineer",
        "specialization": "Frontend UI Specialist",
        "primary_service": "frontend-app",
        "expertise_areas": ["React", "UI components", "frontend performance", "user experience"],
        "severity_focus": ["sev2", "sev3"],
        "issue_types": ["Bug", "Story"],
        "max_story_points": 21
    },
    {
        "display_name": "Sahil Tallam",
        "email": "stallam@ucsc.edu",
        "role": "devops-engineer",
        "specialization": "Infrastructure & DevOps Specialist",
        "primary_service": "infrastructure",
        "expertise_areas": ["CI/CD", "deployment", "infrastructure", "monitoring", "scalability"],
        "severity_focus": ["sev1", "sev2"],  # Infrastructure is critical
        "issue_types": ["Bug", "Task"],
        "max_story_points": 34  # Admin/DevOps handles more
    },
    {
        "display_name": "sasankgamini",
        "email": "sasankgamini@gmail.com",
        "role": "backend-engineer",
        "specialization": "Payment Systems Specialist",
        "primary_service": "payment-service",
        "expertise_areas": ["payment processing", "transaction handling", "financial APIs", "PCI compliance"],
        "severity_focus": ["sev1", "sev2"],  # Payment issues are critical
        "issue_types": ["Bug", "Task"],
        "max_story_points": 21
    },
    {
        "display_name": "Vin Vadoothker",
        "email": "vinvadoothker@gmail.com",
        "role": "data-engineer",
        "specialization": "Data Pipeline Specialist",
        "primary_service": "data-pipeline",
        "expertise_areas": ["data pipelines", "ETL", "data processing", "batch jobs", "data quality"],
        "severity_focus": ["sev2", "sev3"],
        "issue_types": ["Task", "Story"],
        "max_story_points": 21
    }
]

# Issue summaries matching each specialization (for the 5 users)
SPECIALIZATION_ISSUES = {
    "API Backend Specialist": [
        "Fix API endpoint returning 500 errors",
        "Resolve high error rate on /api/v1/users endpoint",
        "Fix authentication middleware timeout",
        "Resolve API rate limiting issue",
        "Fix microservice communication failure",
        "Resolve API response time degradation",
        "Fix REST API validation error",
        "Resolve API endpoint memory leak"
    ],
    "Frontend UI Specialist": [
        "Fix React component rendering issue",
        "Resolve UI layout breakage on mobile",
        "Fix user interface accessibility issue",
        "Resolve frontend state management bug",
        "Fix component performance degradation",
        "Resolve UI styling inconsistency",
        "Fix user experience flow issue",
        "Resolve frontend build error"
    ],
    "Infrastructure & DevOps Specialist": [
        "Fix CI/CD pipeline deployment failure",
        "Resolve container orchestration issue",
        "Fix infrastructure as code deployment error",
        "Resolve deployment rollback failure",
        "Fix database connection pool exhaustion",
        "Resolve infrastructure scaling issue",
        "Fix monitoring system alert failure",
        "Resolve infrastructure provisioning failure"
    ],
    "Payment Systems Specialist": [
        "Fix payment transaction processing error",
        "Resolve payment gateway timeout",
        "Fix PCI compliance validation issue",
        "Resolve payment webhook processing failure",
        "Fix transaction reconciliation bug",
        "Resolve payment API authentication error",
        "Fix financial data integrity issue",
        "Resolve payment processing latency"
    ],
    "Data Pipeline Specialist": [
        "Fix ETL pipeline processing failure",
        "Resolve data pipeline batch job timeout",
        "Fix data quality validation error",
        "Resolve data processing performance issue",
        "Fix data pipeline memory leak",
        "Resolve data transformation error",
        "Fix data pipeline scheduling issue",
        "Resolve data pipeline dependency failure"
    ]
}

# Jira API configuration
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")  # e.g., "https://your-domain.atlassian.net" (strip trailing slash)
JIRA_EMAIL = os.getenv("JIRA_EMAIL")  # Your Jira account email
JIRA_API_KEY = os.getenv("JIRA_API_KEY")  # Your Jira API token
USE_REAL_JIRA = bool(JIRA_URL and JIRA_EMAIL and JIRA_API_KEY)

def get_jira_auth_headers() -> Dict[str, str]:
    """Get authentication headers for Jira API."""
    if not USE_REAL_JIRA:
        return {}
    
    # Basic Auth: email:api_token base64 encoded
    credentials = f"{JIRA_EMAIL}:{JIRA_API_KEY}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

async def search_jira_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Search for a Jira user by email address."""
    if not USE_REAL_JIRA:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{JIRA_URL}/rest/api/3/user/search",
                params={"query": email},
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            users = response.json()
            if users:
                return users[0]  # Return first match
            return None
    except Exception as e:
        print(f"  ⚠️  Failed to search user {email}: {e}")
        return None

async def get_user_issues(account_id: str, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all issues assigned to a user."""
    if not USE_REAL_JIRA:
        return []
    
    # Strategy: Use JQL with assignee filter directly - try multiple formats
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            all_issues = []
            start_at = 0
            max_results = 50
            
            # Try different JQL formats for assignee
            jql_formats = []
            if project_key:
                jql_formats.append(f'project = {project_key} AND assignee = "{account_id}"')
                jql_formats.append(f'project = {project_key} AND assignee = {account_id}')
            jql_formats.append(f'assignee = "{account_id}"')
            jql_formats.append(f'assignee = {account_id}')
            
            for jql in jql_formats:
                try:
                    start_at = 0
                    all_issues = []
                    
                    while True:
                        # Try GET first (may still work)
                        try:
                            response = await client.get(
                                f"{JIRA_URL}/rest/api/3/search",
                                params={
                                    "jql": jql,
                                    "startAt": start_at,
                                    "maxResults": max_results,
                                    "fields": "key,id,assignee"
                                },
                                headers=get_jira_auth_headers()
                            )
                            if response.status_code == 410:
                                # Try POST with new endpoint
                                response = await client.post(
                                    f"{JIRA_URL}/rest/api/3/search",
                                    json={
                                        "jql": jql,
                                        "startAt": start_at,
                                        "maxResults": max_results,
                                        "fields": ["key", "id", "assignee"]
                                    },
                                    headers=get_jira_auth_headers()
                                )
                        except httpx.HTTPStatusError as e:
                            if e.response.status_code == 410:
                                # Try POST with new endpoint
                                response = await client.post(
                                    f"{JIRA_URL}/rest/api/3/search",
                                    json={
                                        "jql": jql,
                                        "startAt": start_at,
                                        "maxResults": max_results,
                                        "fields": ["key", "id", "assignee"]
                                    },
                                    headers=get_jira_auth_headers()
                                )
                            else:
                                raise
                        
                        if response.status_code in [400, 410]:
                            break  # Try next JQL format
                        
                        response.raise_for_status()
                        data = response.json()
                        issues = data.get("issues", [])
                        all_issues.extend(issues)
                        
                        # Check if there are more results
                        total = data.get("total", 0)
                        if start_at + len(issues) >= total:
                            break
                        
                        start_at += max_results
                        
                        # Limit search to reasonable number
                        if start_at >= 1000:
                            break
                    
                    # If we got results, this format worked
                    if response.status_code == 200 and all_issues:
                        return all_issues
                        
                except httpx.HTTPStatusError:
                    continue  # Try next format
                except Exception:
                    continue  # Try next format
            
            # If all formats failed, return empty
            return []
            
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_response = e.response.json()
            error_detail = str(error_response.get("errorMessages", []))
        except:
            error_detail = e.response.text[:200] if e.response.text else str(e)
        print(f"  ⚠️  Failed to get issues for user {account_id}: {error_detail}")
        return []
    except Exception as e:
        print(f"  ⚠️  Failed to get issues for user {account_id}: {e}")
        return []

async def delete_jira_issue(issue_key: str) -> bool:
    """Delete a Jira issue."""
    if not USE_REAL_JIRA:
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(
                f"{JIRA_URL}/rest/api/3/issue/{issue_key}",
                params={"deleteSubtasks": "true"},  # Also delete subtasks if any
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Issue already deleted or doesn't exist
            return True
        print(f"  ⚠️  Failed to delete issue {issue_key}: {e.response.status_code}")
        return False
    except Exception as e:
        print(f"  ⚠️  Failed to delete issue {issue_key}: {e}")
        return False

async def clear_user_issues(account_id: str, user_name: str, project_key: Optional[str] = None) -> int:
    """Delete all issues assigned to a user. Returns number of issues deleted."""
    if not USE_REAL_JIRA:
        return 0
    
    project_suffix = f" in {project_key}" if project_key else ""
    print(f"    Checking existing issues for {user_name}{project_suffix}...")
    issues = await get_user_issues(account_id, project_key)
    
    if not issues:
        print(f"    ✅ No existing issues found for {user_name}{project_suffix}")
        return 0
    
    print(f"    🗑️  Found {len(issues)} existing issues for {user_name}{project_suffix}, deleting...")
    deleted_count = 0
    failed_count = 0
    
    for i, issue in enumerate(issues, 1):
        issue_key = issue.get("key")
        if issue_key:
            if await delete_jira_issue(issue_key):
                deleted_count += 1
                if i % 10 == 0:
                    print(f"      Deleted {i}/{len(issues)} issues...")
            else:
                failed_count += 1
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.2)
    
    if deleted_count > 0:
        print(f"    ✅ Deleted {deleted_count} issues for {user_name}{project_suffix}")
    if failed_count > 0:
        print(f"    ⚠️  Failed to delete {failed_count} issues for {user_name}{project_suffix} (may need delete permissions)")
    
    return deleted_count

async def get_jira_projects() -> List[Dict[str, Any]]:
    """Get list of projects from Jira."""
    if not USE_REAL_JIRA:
        return []
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{JIRA_URL}/rest/api/3/project",
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"  ⚠️  Failed to get projects: {e}")
        return []

async def get_jira_issue_types(project_key: str) -> List[Dict[str, Any]]:
    """Get available issue types for a project."""
    if not USE_REAL_JIRA:
        return []
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{JIRA_URL}/rest/api/3/project/{project_key}",
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            project_data = response.json()
            return project_data.get("issueTypes", [])
    except Exception as e:
        print(f"  ⚠️  Failed to get issue types for {project_key}: {e}")
        return []

def text_to_adf(text: str) -> Dict[str, Any]:
    """Convert plain text to Atlassian Document Format (ADF)."""
    if not text:
        return {
            "version": 1,
            "type": "doc",
            "content": []
        }
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    content = []
    
    for para in paragraphs:
        if para.strip():
            content.append({
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": para.strip()
                    }
                ]
            })
    
    if not content:
        # Empty description
        content.append({
            "type": "paragraph",
            "content": []
        })
    
    return {
        "version": 1,
        "type": "doc",
        "content": content
    }

async def create_jira_issue(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str,
    priority: str,
    assignee_account_id: Optional[str] = None,
    story_points: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Create a Jira issue via API."""
    if not USE_REAL_JIRA:
        return None
    
    # Convert description to Atlassian Document Format (ADF)
    description_adf = text_to_adf(description) if description else None
    
    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }
    }
    
    # Priority: Jira Cloud may require just the name string, or we can omit it
    # Try omitting priority first - Jira will use default priority
    # If priority is required, we'll need to get priority IDs from the project
    # For now, omit priority to avoid errors
    
    # Description: Must be in Atlassian Document Format (ADF) for Jira Cloud
    if description_adf and description_adf.get("content"):
        issue_data["fields"]["description"] = description_adf
    
    if assignee_account_id:
        issue_data["fields"]["assignee"] = {"accountId": assignee_account_id}
    
    # Don't include story points for now - custom field IDs vary by Jira instance
    # if story_points:
    #     issue_data["fields"]["customfield_10016"] = story_points
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{JIRA_URL}/rest/api/3/issue",
                json=issue_data,
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            # Rate limiting - wait a bit
            await asyncio.sleep(2)
            return None
        
        # Get the actual error message from Jira
        error_detail = "Unknown error"
        try:
            error_response = e.response.json()
            if "errors" in error_response:
                error_detail = str(error_response["errors"])
            elif "errorMessages" in error_response:
                error_detail = ", ".join(error_response["errorMessages"])
            else:
                error_detail = e.response.text[:200]  # First 200 chars
        except:
            error_detail = e.response.text[:200] if e.response.text else str(e)
        
        # Only print detailed error for first few failures to avoid spam
        if not hasattr(create_jira_issue, "_error_count"):
            create_jira_issue._error_count = 0
        create_jira_issue._error_count += 1
        
        if create_jira_issue._error_count <= 3:
            print(f"  ⚠️  Failed to create issue in {project_key}: {error_detail}")
        return None
    except Exception as e:
        print(f"  ⚠️  Failed to create issue: {e}")
        return None

async def transition_issue(issue_key: str, target_status: str) -> bool:
    """Transition a Jira issue to a specific status (e.g., 'Done', 'In Progress')."""
    if not USE_REAL_JIRA:
        return False
    
    try:
        # First, get available transitions
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions",
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            transitions = response.json().get("transitions", [])
            
            # Find the transition to the target status
            target_transition = None
            target_lower = target_status.lower()
            for trans in transitions:
                to_status = trans.get("to", {}).get("name", "").lower()
                # Match common status names
                if target_lower == "done":
                    if to_status in ["done", "closed", "resolved"]:
                        target_transition = trans
                        break
                elif target_lower == "in progress":
                    if to_status in ["in progress", "inprogress", "start progress"]:
                        target_transition = trans
                        break
                elif to_status == target_lower:
                    target_transition = trans
                    break
            
            if not target_transition:
                return False
            
            # Transition to target status
            transition_data = {
                "transition": {"id": target_transition["id"]}
            }
            
            response = await client.post(
                f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions",
                json=transition_data,
                headers=get_jira_auth_headers()
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"  ⚠️  Failed to transition issue {issue_key} to {target_status}: {e}")
        return False

async def transition_issue_to_done(issue_key: str) -> bool:
    """Transition a Jira issue to 'Done' status."""
    return await transition_issue(issue_key, "Done")

async def transition_issue_to_in_progress(issue_key: str) -> bool:
    """Transition a Jira issue to 'In Progress' status."""
    return await transition_issue(issue_key, "In Progress")

def get_db_connection():
    """Get database connection from environment."""
    import psycopg2
    from urllib.parse import urlparse
import uuid
    
    # Detect if running from host machine or inside Docker
    postgres_url = os.getenv("POSTGRES_URL")
    
    if not postgres_url:
        import socket
        is_docker = os.path.exists("/.dockerenv") or socket.gethostname().endswith("container")
        
        if is_docker:
            postgres_url = "postgresql://goliath:goliath@postgres:5432/goliath"
        else:
            postgres_url = "postgresql://goliath:goliath@localhost:5432/goliath"
    
    parsed = urlparse(postgres_url)
    
    # If hostname is "postgres" but we're not in Docker, change to localhost
    if parsed.hostname == "postgres":
        import socket
        is_docker = os.path.exists("/.dockerenv") or socket.gethostname().endswith("container")
        if not is_docker:
            postgres_url = postgres_url.replace("postgres:", "localhost:")
            parsed = urlparse(postgres_url)
    
    # Try connecting with retries
    max_retries = 10
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 5432,
                database=parsed.path[1:] or "goliath",
                user=parsed.username or "goliath",
                password=parsed.password or "goliath",
                connect_timeout=5
            )
            return conn
        except psycopg2.OperationalError as e:
            if i < max_retries - 1:
                print(f"  Waiting for database... ({i+1}/{max_retries})")
                import time
                time.sleep(2)
            else:
                print(f"❌ Failed to connect to database at {parsed.hostname}:{parsed.port}")
                print(f"   Error: {e}")
                raise

def create_human_in_db(conn, account_id: str, display_name: str, email: str, jira_account_id: str = None):
    """Create or update human in the main database (work_items, humans tables)."""
    cur = conn.cursor()
    try:
        # Use account_id as human_id, or jira_account_id if provided
        human_id = jira_account_id or account_id
        
        cur.execute("""
            INSERT INTO humans (id, display_name, email, jira_account_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET display_name = EXCLUDED.display_name,
                email = EXCLUDED.email,
                jira_account_id = EXCLUDED.jira_account_id
        """, (human_id, display_name, email, account_id))
        conn.commit()
        return human_id
    except Exception as e:
        conn.rollback()
        print(f"  ⚠️  Failed to create human {display_name}: {e}")
        return None

async deitem_via_ingest(
    jira_issue_key: str,
    service: str,
    severity: str,
    description: str,
    issue_type: str,
    priority: str,
    created_at: datetime,
    assignee_account_id: str = None,
    story_points: int = None,
    resolved_at: datetime = None
) -> Optional[str]:
    """Create WorkItem via Ingest Service (maintains single source of truth)."""
    ingest_url = os.getenv("INGEST_SERVICE_URL", "http://localhost:8001")
    
    # Map Jira priority to severity if needed
    if severity not in ["sev1", "sev2", "sev3", "sev4"]:
        priority_map = {
            "Critical": "sev1",
            "High": "sev2",
            "Medium": "sev3",
            "Low": "sev4"
        }
        severity = priority_map.get(priority, "sev2")
    
    # Map issue type to work item type
    type_map = {
        "Bug": "incident",
        "Task": "ticket",
        "Story": "ticket"
    }
    work_item_type = type_map.get(issue_type, "incident")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Call Ingest Service to create WorkItem
            response = await client.post(
                f"{ingest_url}/ingest/demo",
                json={
                    "service": service,
                    "severity": severity,
                    "description": description,
                    "type": work_item_type,
                    "story_points": story_points,
                    "raw_log": description  # Store original description as raw_log
                }
            )
            
            if response.status_code == 201:
                result = response.json()
                work_item_id = result.get("work_item_id")
                
                # Link WorkItem to Jira issue in database
                if work_item_id:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    try:
                        cur.execute("""
                            UPDATE work_items
                            SET jira_issue_key = %s, origin_system = %s, created_at = %s
                            WHERE id = %s
                        """, (jira_issue_key, f"JIRA-{jira_issue_key}", created_at, work_item_id))
                        conn.commit()
                        
                        # If resolved, create resolved_edge (historical data)
                        if resolved_at and assignee_account_id:
                            cur.execute("""
                                SELECT id FROM humans WHERE jira_account_id = %s
                            """, (assignee_account_id,))
                            result = cur.fetchone()
                            if result:
                                human_id = result[0]
                                # Check if edge already exists
                                cur.execute("""
                                    SELECT id FROM resolved_edges 
                                    WHERE human_id = %s AND work_item_id = %s
                                """, (human_id, work_item_id))
                                if not cur.fetchone():
                                    cur.execute("""
                                        INSERT INTO resolved_edges (human_id, work_item_id, resolved_at)
                                        VALUES (%s, %s, %s)
                                    """, (human_id, work_item_id, resolved_at))
                                    conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print(f"  ⚠️  Failed to link WorkItem {work_item_id} to Jira issue: {e}")
                    finally:
                        cur.close()
                        conn.close()
                
                return work_item_id
            else:
                print(f"  ⚠️  Ingest Service returned {response.status_code}: {response.text}")
                return None
    except httpx.RequestError as e:
        print(f"  ⚠️  Failed to call Ingest Service: {e}")
        print(f"      Make sure Ingest Service is running at {ingest_url}")
        return None
    except Exception as e:
        print(f"  ⚠️  Failed to create WorkItem via Ingest for {jira_issue_key}: {e}")
        return None

async def sync_learner_service(days_back: int = 90) -> bool:
    """Automatically sync Learner Service with seeded data."""
    learner_url = os.getenv("LEARNER_SERVICE_URL", "http://localhost:8003")
    
    # Try multiple URLs (localhost for host, learner for Docker)
    urls_to_try = [
        learner_url,
        "http://localhost:8003",
        "http://learner:8000"  # Docker internal network
    ]
    
    print("")
    print("🔄 Syncing Learner Service with seeded data...")
    print("   (Building capability profiles from closed tickets...)")
    
    for url in urls_to_try:
        try:
            # First check if Learner Service is ready
            async with httpx.AsyncClient(timeout=5.0) as client:
                health_response = await client.get(f"{url}/healthz")
                if health_response.status_code == 200:
                    # Service is ready, try sync
                    print(f"   Connecting to Learner Service at {url}...")
                    sync_response = await client.post(
                        f"{url}/sync/jira",
                        json={"days_back": days_back},
                        timeout=60.0  # Sync can take a while
                    )
                    sync_response.raise_for_status()
                    result = sync_response.json()
                    synced_count = result.get("synced", 0)
                    humans_updated = result.get("humans_updated", 0)
                    print(f"   ✅ Learner Service synced: {synced_count} tickets processed, {humans_updated} humans updated")
                    return True
        except httpx.RequestError as e:
            # Try next URL
            continue
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Service might not be running, try next URL
                continue
            else:
                print(f"   ⚠️  Learner Service returned error: {e.response.status_code}")
                print(f"   Response: {e.response.text}")
                continue
        except Exception as e:
            # Try next URL
            continue
    
    # If we get here, all URLs failed
    print("   ⚠️  Could not connect to Learner Service")
    print("   This is OK - you can sync manually later with: make sync-learner")
    print("   Or: curl -X POST http://localhost:8003/sync/jira -H 'Content-Type: application/json' -d '{\"days_back\": 90}'")
    return False

async def seed_jira_data():
    """Seed Jira (real or simulator) with specialized users and their work history."""
    if USE_REAL_JIRA:
        print(f"🌱 Seeding REAL Jira ({JIRA_URL}) with 5 specialized users...")
        print(f"   Using email: {JIRA_EMAIL}")
    else:
        print("🌱 Seeding Jira Simulator (local database) with 5 specialized users...")
        print("   (Set JIRA_URL, JIRA_EMAIL, and JIRA_API_KEY to use real Jira)")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create tables if they don't exist
        print("  Creating tables...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jira_projects (
                key TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                project_type_key TEXT NOT NULL
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jira_users (
                account_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                email_address TEXT,
                active BOOLEAN DEFAULT TRUE,
                max_story_points INTEGER DEFAULT 21,
                current_story_points INTEGER DEFAULT 0,
                role TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jira_issues (
                id TEXT PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                project_key TEXT NOT NULL,
                summary TEXT NOT NULL,
                description TEXT,
                issuetype_name TEXT NOT NULL,
                priority_name TEXT NOT NULL,
                status_name TEXT NOT NULL,
                assignee_account_id TEXT,
                reporter_account_id TEXT,
                story_points INTEGER,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                resolved_at TIMESTAMP,
                FOREIGN KEY (assignee_account_id) REFERENCES jira_users(account_id),
                FOREIGN KEY (reporter_account_id) REFERENCES jira_users(account_id),
                FOREIGN KEY (project_key) REFERENCES jira_projects(key)
            )
        """)
        
        conn.commit()
        print("  ✅ Tables created")
        
        # Get/create projects
        print("  Getting projects...")
        projects = []
        
        if USE_REAL_JIRA:
            # Get actual projects from Jira
            jira_projects = await get_jira_projects()
            if jira_projects:
                print(f"  Found {len(jira_projects)} projects in Jira:")
                for jp in jira_projects:
                    print(f"    - {jp.get('key')}: {jp.get('name')}")
                    projects.append({
                        "key": jp.get("key"),
                        "name": jp.get("name"),
                        "id": jp.get("id")
                    })
                
                # Map services to actual project keys
                # Try to match service names to project keys
                service_to_project = {}
                for service in SERVICES:
                    # Try exact match first
                    matched = None
                    for jp in jira_projects:
                        project_key = jp.get("key", "").upper()
                        project_name = jp.get("name", "").lower()
                        service_upper = service.upper().replace("-", "")
                        
                        if project_key == service_upper[:10] or service in project_name:
                            matched = jp.get("key")
                            break
                    
                    if matched:
                        service_to_project[service] = matched
                    else:
                        # Use first project as fallback
                        service_to_project[service] = jira_projects[0].get("key")
                        print(f"    ⚠️  No match for {service}, using project {service_to_project[service]}")
                
                # Update projects list with matched keys
                projects = [{"key": service_to_project.get(s, jira_projects[0].get("key")), "name": s} for s in SERVICES]
            else:
                print("  ⚠️  No projects found in Jira. You need to create projects first.")
                print("     Expected project keys: API, PAYMENT, FRONTEND, DATAPIPELINE, INFRASTRUCTURE")
                print("     Or update SERVICES list in script to match your project keys.")
                # Use default project keys anyway
                for service in SERVICES:
                    project_key = service.upper().replace("-", "")[:10]
                    projects.append({"key": project_key, "name": service})
        else:
            # Local database mode
        for service in SERVICES:
            project_key = service.upper().replace("-", "")[:10]
            cur.execute("""
                INSERT INTO jira_projects (key, name, project_type_key)
                VALUES (%s, %s, 'software')
                ON CONFLICT (key) DO NOTHING
            """, (project_key, service))
            projects.append({"key": project_key, "name": service})
        conn.commit()
        
        print(f"  ✅ Using {len(projects)} projects")
        
        # Create 5 specialized users
        print("  Creating 5 specialized users...")
        users = []
        for i, user_spec in enumerate(SPECIALIZED_USERS):
            if USE_REAL_JIRA:
                # Search for existing user by email in real Jira
                print(f"    Searching for user: {user_spec['email']}...")
                jira_user = await search_jira_user_by_email(user_spec["email"])
                if jira_user:
                    account_id = jira_user.get("accountId")
                    display_name = jira_user.get("displayName", user_spec["display_name"])
                    print(f"    ✅ Found existing user: {display_name} ({account_id})")
                else:
                    print(f"    ⚠️  User {user_spec['email']} not found in Jira")
                    print(f"       Note: Users must be created by Jira admin. Skipping user creation.")
                    print(f"       You can create users manually in Jira, then re-run this script.")
                    # Use a placeholder account ID
                    account_id = f"557058:user{i+1:03d}"
                    display_name = user_spec["display_name"]
            else:
                # Local database mode
                account_id = f"557058:user{i+1:03d}"  # Consistent IDs: 557058:user001, 557058:user002, etc.
                display_name = user_spec["display_name"]
            
            # Store in local database (for simulator or tracking)
            if not USE_REAL_JIRA:
            cur.execute("""
                INSERT INTO jira_users (account_id, display_name, email_address, active, max_story_points, current_story_points, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (account_id) DO UPDATE SET
                        display_name = EXCLUDED.display_name,
                        email_address = EXCLUDED.email_address,
                        role = EXCLUDED.role,
                        max_story_points = EXCLUDED.max_story_points
            """, (
                account_id,
                    display_name,
                    user_spec["email"],
                True,
                    user_spec["max_story_points"],
                0,  # Will be updated after creating open tickets
                    user_spec["role"]
            ))
            
            # Create human in main database (work_items, humans tables)
            human_id = create_human_in_db(conn, account_id, display_name, user_spec["email"], account_id)
            
            users.append({
                "account_id": account_id,
                "display_name": display_name,
                "email": user_spec["email"],
                "specialization": user_spec["specialization"],
                "primary_service": user_spec["primary_service"],
                "expertise_areas": user_spec["expertise_areas"],
                "severity_focus": user_spec["severity_focus"],
                "issue_types": user_spec["issue_types"],
                "max_story_points": user_spec["max_story_points"],
                "current_story_points": 0,
                "human_id": human_id
            })
        
        if not USE_REAL_JIRA:
        conn.commit()
        print(f"  ✅ Processed {len(users)} specialized users")
        print(f"  ✅ Created {len(users)} humans in main database")
        print("")
        print("  User Specializations:")
        for user in users:
            print(f"    - {user['display_name']}: {user['specialization']} ({user['primary_service']})")
        
        # Note: Existing issues should be cleared manually before running make seed
        
        # Create closed tickets (last 90 days) - Each user gets tickets matching their specialization
        print("")
        print("  Creating closed tickets (last 90 days)...")
        start_date = datetime.now() - timedelta(days=90)
        closed_count = 0
        
        # Each user gets 30-50 closed tickets matching their specialization
        for user in users:
            user_closed_count = random.randint(30, 50)
            user_project = next(p for p in projects if p["name"] == user["primary_service"])
            user_issues = SPECIALIZATION_ISSUES.get(user["specialization"], [f"Resolved {user['specialization']} issue"])
            
            for _ in range(user_closed_count):
                # Create ticket matching user's specialization
            created_at = fake.date_time_between(start_date=start_date, end_date='now')
            resolved_at = created_at + timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            
                issue_type = random.choice(user["issue_types"])
                priority = random.choice(user["severity_focus"]).replace("sev", "").capitalize()  # sev1 -> Critical
                if priority == "Sev1":
                    priority = "Critical"
                elif priority == "Sev2":
                    priority = "High"
                elif priority == "Sev3":
                    priority = "Medium"
                
            story_points = random.choice([1, 2, 3, 5, 8, 13]) if issue_type != "Bug" else None
                summary = random.choice(user_issues)
                description = f"Description for {summary}. Related to {', '.join(user['expertise_areas'][:2])}."
                
                if USE_REAL_JIRA:
                    # Create issue in real Jira
                    jira_issue = await create_jira_issue(
                        project_key=user_project['key'],
                        summary=summary,
                        description=description,
                        issue_type=issue_type,
                        priority=priority,
                        assignee_account_id=user['account_id'],
                        story_points=story_points
                    )
                    
                    if jira_issue:
                        issue_key = jira_issue.get("key")
                        # Transition to Done
                        await transition_issue_to_done(issue_key)
                        
                        # Create WorkItem in main database
                        # Map priority to severity
                        priority_to_severity = {
                            "Critical": "sev1",
                            "High": "sev2",
                            "Medium": "sev3",
                            "Low": "sev4"
                        }
                        severity = priority_to_severity.get(priority, "sev2")
                        
                        # Map project to service
                        service = user["primary_service"]
                        
                        await create_work_item_via_ingest(
                            jira_issue_key=issue_key,
                            service=service,
                            severity=severity,
                            description=description,
                            issue_type=issue_type,
                            priority=priority,
                            created_at=created_at,
                            assignee_account_id=user['account_id'],
                            story_points=story_points,
                            resolved_at=resolved_at
                        )
                        
                        closed_count += 1
                        if closed_count % 10 == 0:
                            print(f"    Created {closed_count} issues...")
                    
                    # Add delay to avoid rate limiting (429 errors)
                    await asyncio.sleep(0.5)  # 500ms delay between issues
                else:
                    # Local database mode
            issue_id = fake.uuid4()
                    issue_key = f"{user_project['key']}-{random.randint(100, 9999)}"
                    reporter = random.choice(users)  # Any user can report
            
            cur.execute("""
                INSERT INTO jira_issues (
                    id, key, project_key, summary, description, issuetype_name, priority_name,
                    status_name, assignee_account_id, reporter_account_id, story_points,
                    created_at, updated_at, resolved_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (key) DO NOTHING
            """, (
                issue_id,
                issue_key,
                        user_project['key'],
                        summary,
                        description,
                issue_type,
                priority,
                "Done",
                        user['account_id'],  # Assigned to this specialized user
                reporter['account_id'],
                story_points,
                created_at,
                resolved_at,
                resolved_at
            ))
            
            if cur.rowcount > 0:
                        # Create WorkItem via Ingest Service (maintains single source of truth)
                        # Map priority to severity
                        priority_to_severity = {
                            "Critical": "sev1",
                            "High": "sev2",
                            "Medium": "sev3",
                            "Low": "sev4"
                        }
                        severity = priority_to_severity.get(priority, "sev2")
                        
                        # Map project to service
                        service = user["primary_service"]
                        
                        await create_work_item_via_ingest(
                            jira_issue_key=issue_key,
                            service=service,
                            severity=severity,
                            description=description,
                            issue_type=issue_type,
                            priority=priority,
                            created_at=created_at,
                            assignee_account_id=user['account_id'],
                            story_points=story_points,
                            resolved_at=resolved_at
                        )
                        
                closed_count += 1
        
        if not USE_REAL_JIRA:
        conn.commit()
        print(f"  ✅ Created {closed_count} closed tickets (specialized per user)")
        
        # Create some open tickets (current capacity) - distributed across users
        print("  Creating open tickets (current capacity)...")
        open_count = 0
        
        for _ in range(50):  # 50 open tickets total
            project = random.choice(projects)
            assignee = random.choice(users)
            created_at = fake.date_time_between(start_date=start_date, end_date='now')
            
            issue_type = random.choice(["Bug", "Task", "Story"])
            priority = random.choice(["Critical", "High", "Medium", "Low"])
            story_points = random.choice([1, 2, 3, 5, 8, 13]) if issue_type != "Bug" else None
            summary = fake.sentence()
            description = fake.text()
            
            if USE_REAL_JIRA:
                # Create issue in real Jira (will be in "To Do" status by default)
                jira_issue = await create_jira_issue(
                    project_key=project['key'],
                    summary=summary,
                    description=description,
                    issue_type=issue_type,
                    priority=priority,
                    assignee_account_id=assignee['account_id'],
                    story_points=story_points
                )
                
                if jira_issue:
                    open_count += 1
                    issue_key = jira_issue.get("key")
                    
                    # Randomly transition some issues to "In Progress" (about 40% of open tickets)
                    if random.random() < 0.4:
                        await transition_issue_to_in_progress(issue_key)
                    
                    # Create WorkItem in main database (open tickets)
                    priority_to_severity = {
                        "Critical": "sev1",
                        "High": "sev2",
                        "Medium": "sev3",
                        "Low": "sev4"
                    }
                    severity = priority_to_severity.get(priority, "sev2")
                    
                    # Map project to service
                    service = project.get("name", "api-service")
                    
                    await create_work_item_via_ingest(
                        jira_issue_key=issue_key,
                        service=service,
                        severity=severity,
                        description=description,
                        issue_type=issue_type,
                        priority=priority,
                        created_at=created_at,
                        assignee_account_id=assignee['account_id'],
                        story_points=story_points,
                        resolved_at=None  # Open ticket, not resolved
                    )
                    
                    if story_points:
                        assignee['current_story_points'] += story_points
                    if open_count % 10 == 0:
                        print(f"    Created {open_count} open issues...")
                
                # Add delay to avoid rate limiting (429 errors)
                await asyncio.sleep(0.5)  # 500ms delay between issues
            else:
                # Local database mode
            issue_id = fake.uuid4()
            issue_key = f"{project['key']}-{random.randint(100, 9999)}"
            reporter = random.choice(users)
                status = random.choice(["To Do", "In Progress"])
            
            cur.execute("""
                INSERT INTO jira_issues (
                    id, key, project_key, summary, description, issuetype_name, priority_name,
                    status_name, assignee_account_id, reporter_account_id, story_points,
                    created_at, updated_at, resolved_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (key) DO NOTHING
            """, (
                issue_id,
                issue_key,
                project['key'],
                    summary,
                    description,
                issue_type,
                priority,
                status,
                assignee['account_id'],
                reporter['account_id'],
                story_points,
                created_at,
                created_at,
                None
            ))
            
            if cur.rowcount > 0:
                    # Create WorkItem via Ingest Service (open tickets)
                    priority_to_severity = {
                        "Critical": "sev1",
                        "High": "sev2",
                        "Medium": "sev3",
                        "Low": "sev4"
                    }
                    severity = priority_to_severity.get(priority, "sev2")
                    
                    # Map project to service
                    service = project.get("name", "api-service")
                    
                    await create_work_item_via_ingest(
                        jira_issue_key=issue_key,
                        service=service,
                        severity=severity,
                        description=description,
                        issue_type=issue_type,
                        priority=priority,
                        created_at=created_at,
                        assignee_account_id=assignee['account_id'],
                        story_points=story_points,
                        resolved_at=None  # Open ticket, not resolved
                    )
                    
                open_count += 1
                # Update user's current_story_points
                if story_points:
                    assignee['current_story_points'] += story_points
        
        if not USE_REAL_JIRA:
        conn.commit()
        print(f"  ✅ Created {open_count} open tickets")
        
        # Summary
        print("")
        print("✅ Seeding complete!")
        print("")
        print("📊 Summary:")
        print(f"  - {len(users)} specialized users created")
        print(f"  - {closed_count} closed tickets created (with WorkItems and resolved_edges)")
        print(f"  - {open_count} open tickets created (with WorkItems)")
        print("")
        print("💾 Data stored in:")
        print("  - Jira (real or simulator): Users and issues")
        print("  - Ingest Service: All WorkItems (via POST /ingest/demo)")
        print("  - Main database (work_items table): All WorkItems linked to Jira issues")
        print("  - Main database (humans table): All users")
        print("  - Main database (resolved_edges table): Closed ticket relationships")
        print("")
        # Automatically sync Learner Service
        await sync_learner_service(days_back=90)
        print("")
        
        # Update user current_story_points (local database only)
        if not USE_REAL_JIRA:
        print("  Updating user capacity...")
        for user in users:
            cur.execute("""
                UPDATE jira_users
                SET current_story_points = (
                    SELECT COALESCE(SUM(story_points), 0)
                    FROM jira_issues
                    WHERE assignee_account_id = %s
                    AND status_name IN ('To Do', 'In Progress')
                )
                WHERE account_id = %s
            """, (user['account_id'], user['account_id']))
        
        conn.commit()
        print("  ✅ Updated user capacity")
        
        print("")
        if USE_REAL_JIRA:
            print("✅ Real Jira seeded successfully!")
        else:
        print("✅ Jira Simulator seeded successfully!")
        print(f"   - {len(projects)} projects")
        print(f"   - {len(users)} specialized users")
        print(f"   - {closed_count} closed tickets (specialized per user)")
        print(f"   - {open_count} open tickets")
        print("")
        print("📊 User Specializations Summary:")
        for user in users:
            cur.execute("""
                SELECT COUNT(*) as resolved_count
                FROM jira_issues
                WHERE assignee_account_id = %s
                AND status_name = 'Done'
            """, (user['account_id'],))
            resolved = cur.fetchone()[0]
            print(f"   - {user['display_name']}: {resolved} resolved tickets in {user['primary_service']}")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_jira_data())
