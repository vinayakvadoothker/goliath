"""
Jira Simulator - Full Jira REST API v3 mock
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
import logging

from jql_parser import parse_jql
from db import execute_query, execute_update, get_next_issue_key

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jira Simulator", version="0.1.0")


class Issue(BaseModel):
    id: str
    key: str
    fields: dict


class SearchResponse(BaseModel):
    issues: List[Issue]
    total: int
    startAt: int
    maxResults: int


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "jira-simulator"}


@app.get("/rest/api/3/search")
async def search_issues(
    jql: str = Query(..., description="JQL query"),
    startAt: int = Query(0, ge=0),
    maxResults: int = Query(50, ge=1, le=100)
):
    """
    JQL search endpoint - returns issues matching the JQL query.
    
    Example queries:
    - project=API AND status=Done
    - status=Done AND resolved >= -90d
    - assignee=557058:abc12345
    """
    try:
        # Parse JQL into SQL WHERE clause
        where_clause, params = parse_jql(jql)
        
        # Build SQL query
        # First, get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM jira_issues
            WHERE {where_clause}
        """
        count_result = execute_query(count_query, params)
        total = count_result[0]['total'] if count_result else 0
        
        # Then get the actual issues with pagination
        query = f"""
            SELECT 
                id,
                key,
                project_key,
                summary,
                description,
                issuetype_name,
                priority_name,
                status_name,
                assignee_account_id,
                reporter_account_id,
                story_points,
                created_at,
                updated_at,
                resolved_at
            FROM jira_issues
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        # Add pagination parameters
        params_with_pagination = params + [maxResults, startAt]
        
        results = execute_query(query, params_with_pagination)
        
        # Convert to Jira API format
        issues = []
        for row in results:
            # Get assignee and reporter details if they exist
            assignee = None
            reporter = None
            
            if row['assignee_account_id']:
                assignee_query = "SELECT account_id, display_name, email_address FROM jira_users WHERE account_id = %s"
                assignee_result = execute_query(assignee_query, [row['assignee_account_id']])
                if assignee_result:
                    assignee = {
                        "accountId": assignee_result[0]['account_id'],
                        "displayName": assignee_result[0]['display_name'],
                        "emailAddress": assignee_result[0].get('email_address')
                    }
            
            if row['reporter_account_id']:
                reporter_query = "SELECT account_id, display_name, email_address FROM jira_users WHERE account_id = %s"
                reporter_result = execute_query(reporter_query, [row['reporter_account_id']])
                if reporter_result:
                    reporter = {
                        "accountId": reporter_result[0]['account_id'],
                        "displayName": reporter_result[0]['display_name'],
                        "emailAddress": reporter_result[0].get('email_address')
                    }
            
            # Get project details
            project_query = "SELECT key, name FROM jira_projects WHERE key = %s"
            project_result = execute_query(project_query, [row['project_key']])
            project = None
            if project_result:
                project = {
                    "key": project_result[0]['key'],
                    "name": project_result[0]['name'],
                    "projectTypeKey": "software"
                }
            
            issue = {
                "id": row['id'],
                "key": row['key'],
                "self": f"http://localhost:8080/rest/api/3/issue/{row['key']}",
                "fields": {
                    "summary": row['summary'],
                    "description": row.get('description'),
                    "issuetype": {
                        "name": row['issuetype_name']
                    },
                    "priority": {
                        "name": row['priority_name']
                    },
                    "status": {
                        "name": row['status_name']
                    },
                    "project": project,
                    "assignee": assignee,
                    "reporter": reporter,
                    "created": row['created_at'].isoformat() if row['created_at'] else None,
                    "updated": row['updated_at'].isoformat() if row['updated_at'] else None,
                    "resolutiondate": row['resolved_at'].isoformat() if row['resolved_at'] else None,
                    "customfield_10016": row.get('story_points')  # Story points field
                }
            }
            issues.append(issue)
        
        return {
            "issues": issues,
            "total": total,
            "startAt": startAt,
            "maxResults": maxResults
        }
    
    except Exception as e:
        logger.error(f"JQL search failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"JQL query failed: {str(e)}")


@app.post("/rest/api/3/issue")
async def create_issue(issue: dict):
    """
    Create a Jira issue.
    
    Expected format:
    {
        "fields": {
            "project": {"key": "API"},
            "summary": "Issue title",
            "description": "Issue description",
            "issuetype": {"name": "Bug"},
            "priority": {"name": "High"},
            "assignee": {"accountId": "557058:abc12345"}
        }
    }
    """
    try:
        fields = issue.get('fields', {})
        project_key = fields.get('project', {}).get('key')
        if not project_key:
            raise HTTPException(status_code=400, detail="Project key is required")
        
        # Generate next issue key
        issue_key = get_next_issue_key(project_key)
        issue_id = f"issue-{datetime.now().timestamp()}"
        
        # Extract fields
        summary = fields.get('summary', '')
        description = fields.get('description')
        issuetype_name = fields.get('issuetype', {}).get('name', 'Task')
        priority_name = fields.get('priority', {}).get('name', 'Medium')
        assignee_account_id = fields.get('assignee', {}).get('accountId')
        story_points = fields.get('customfield_10016')  # Story points
        
        # Insert into database
        query = """
            INSERT INTO jira_issues (
                id, key, project_key, summary, description, issuetype_name,
                priority_name, status_name, assignee_account_id, story_points,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, key
        """
        
        now = datetime.now()
        params = [
            issue_id,
            issue_key,
            project_key,
            summary,
            description,
            issuetype_name,
            priority_name,
            "To Do",  # Default status
            assignee_account_id,
            story_points,
            now,
            now
        ]
        
        result = execute_query(query, params, commit=True)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create issue")
        
        return {
            "id": result[0]['id'],
            "key": result[0]['key'],
            "self": f"http://localhost:8080/rest/api/3/issue/{result[0]['key']}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create issue failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create issue: {str(e)}")


@app.get("/rest/api/3/issue/{issue_key}")
async def get_issue(issue_key: str):
    """Get a Jira issue by key."""
    try:
        query = """
            SELECT 
                id, key, project_key, summary, description, issuetype_name,
                priority_name, status_name, assignee_account_id, reporter_account_id,
                story_points, created_at, updated_at, resolved_at
            FROM jira_issues
            WHERE key = %s
        """
        
        results = execute_query(query, [issue_key])
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Issue {issue_key} not found")
        
        row = results[0]
        
        # Get assignee and reporter details
        assignee = None
        reporter = None
        
        if row['assignee_account_id']:
            assignee_query = "SELECT account_id, display_name, email_address FROM jira_users WHERE account_id = %s"
            assignee_result = execute_query(assignee_query, [row['assignee_account_id']])
            if assignee_result:
                assignee = {
                    "accountId": assignee_result[0]['account_id'],
                    "displayName": assignee_result[0]['display_name'],
                    "emailAddress": assignee_result[0].get('email_address')
                }
        
        if row['reporter_account_id']:
            reporter_query = "SELECT account_id, display_name, email_address FROM jira_users WHERE account_id = %s"
            reporter_result = execute_query(reporter_query, [row['reporter_account_id']])
            if reporter_result:
                reporter = {
                    "accountId": reporter_result[0]['account_id'],
                    "displayName": reporter_result[0]['display_name'],
                    "emailAddress": reporter_result[0].get('email_address')
                }
        
        # Get project details
        project_query = "SELECT key, name FROM jira_projects WHERE key = %s"
        project_result = execute_query(project_query, [row['project_key']])
        project = None
        if project_result:
            project = {
                "key": project_result[0]['key'],
                "name": project_result[0]['name'],
                "projectTypeKey": "software"
            }
        
        return {
            "id": row['id'],
            "key": row['key'],
            "self": f"http://localhost:8080/rest/api/3/issue/{row['key']}",
            "fields": {
                "summary": row['summary'],
                "description": row.get('description'),
                "issuetype": {
                    "name": row['issuetype_name']
                },
                "priority": {
                    "name": row['priority_name']
                },
                "status": {
                    "name": row['status_name']
                },
                "project": project,
                "assignee": assignee,
                "reporter": reporter,
                "created": row['created_at'].isoformat() if row['created_at'] else None,
                "updated": row['updated_at'].isoformat() if row['updated_at'] else None,
                "resolutiondate": row['resolved_at'].isoformat() if row['resolved_at'] else None,
                "customfield_10016": row.get('story_points')
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get issue failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get issue: {str(e)}")


@app.put("/rest/api/3/issue/{issue_key}")
async def update_issue(issue_key: str, update: dict):
    """Update a Jira issue."""
    try:
        # Check if issue exists
        check_query = "SELECT id FROM jira_issues WHERE key = %s"
        check_result = execute_query(check_query, [issue_key])
        
        if not check_result:
            raise HTTPException(status_code=404, detail=f"Issue {issue_key} not found")
        
        # Parse update structure (Jira API format)
        # update = {"fields": {"status": {"name": "In Progress"}}}
        fields = update.get('fields', {})
        
        updates = []
        params = []
        
        if 'status' in fields:
            status_name = fields['status'].get('name')
            if status_name:
                updates.append("status_name = %s")
                params.append(status_name)
        
        if 'assignee' in fields:
            assignee = fields['assignee']
            if assignee is None:
                updates.append("assignee_account_id = NULL")
            elif 'accountId' in assignee:
                updates.append("assignee_account_id = %s")
                params.append(assignee['accountId'])
        
        if 'summary' in fields:
            updates.append("summary = %s")
            params.append(fields['summary'])
        
        if 'description' in fields:
            updates.append("description = %s")
            params.append(fields.get('description'))
        
        if not updates:
            return {"status": "no changes"}
        
        updates.append("updated_at = %s")
        params.append(datetime.now())
        params.append(issue_key)  # For WHERE clause
        
        query = f"""
            UPDATE jira_issues
            SET {', '.join(updates)}
            WHERE key = %s
        """
        
        execute_update(query, params)
        
        return {"status": "updated"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update issue failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update issue: {str(e)}")


@app.get("/rest/api/3/user/search")
async def search_users(
    query: Optional[str] = Query(None, description="Search query (name or email)"),
    startAt: int = Query(0, ge=0),
    maxResults: int = Query(50, ge=1, le=100)
):
    """Search users by name or email."""
    try:
        if query:
            search_query = """
                SELECT account_id, display_name, email_address, active
                FROM jira_users
                WHERE (display_name ILIKE %s OR email_address ILIKE %s)
                AND active = TRUE
                ORDER BY display_name
                LIMIT %s OFFSET %s
            """
            search_pattern = f"%{query}%"
            params = [search_pattern, search_pattern, maxResults, startAt]
        else:
            search_query = """
                SELECT account_id, display_name, email_address, active
                FROM jira_users
                WHERE active = TRUE
                ORDER BY display_name
                LIMIT %s OFFSET %s
            """
            params = [maxResults, startAt]
        
        results = execute_query(search_query, params)
        
        users = []
        for row in results:
            users.append({
                "accountId": row['account_id'],
                "displayName": row['display_name'],
                "emailAddress": row.get('email_address'),
                "active": row['active']
            })
        
        return users
    
    except Exception as e:
        logger.error(f"User search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"User search failed: {str(e)}")


@app.get("/rest/api/3/project")
async def list_projects():
    """List all projects."""
    try:
        query = "SELECT key, name, project_type_key FROM jira_projects ORDER BY name"
        results = execute_query(query)
        
        projects = []
        for row in results:
            projects.append({
                "key": row['key'],
                "name": row['name'],
                "projectTypeKey": row['project_type_key']
            })
        
        return projects
    
    except Exception as e:
        logger.error(f"List projects failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"List projects failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("JIRA_SIMULATOR_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
