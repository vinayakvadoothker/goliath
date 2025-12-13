#!/usr/bin/env python3
"""
Jira Simulator Seeding Script
Seeds Jira Simulator with realistic data:
- 200 people across different roles
- 3-5 services/projects
- Realistic work history (last 90 days):
  - Closed tickets (bugs, tasks, stories)
  - Open tickets (current capacity)
  - Story points assigned
  - Different severities/priorities
  - Different resolution times
"""

import random
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    from faker import Faker
except ImportError:
    print("⚠️  faker not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "faker", "psycopg2-binary"])
    from faker import Faker

fake = Faker()

# Configuration
# Comprehensive roles across all departments
ROLES = [
    # Engineering
    "backend-engineer", "frontend-engineer", "fullstack-engineer", "mobile-engineer",
    "sre", "devops-engineer", "platform-engineer", "infrastructure-engineer",
    "data-engineer", "ml-engineer", "security-engineer", "qa-engineer", "test-engineer",
    # Product & Design
    "product-manager", "product-owner", "product-designer", "ux-designer", "ui-designer",
    # Operations & Support
    "operations-manager", "support-engineer", "customer-success", "technical-support",
    # Finance & Business
    "finance-manager", "financial-analyst", "business-analyst", "accountant",
    # HR & People
    "hr-manager", "recruiter", "people-ops", "talent-acquisition",
    # Sales & Marketing
    "sales-engineer", "technical-writer", "marketing-manager", "growth-engineer",
    # Leadership
    "engineering-manager", "tech-lead", "staff-engineer", "principal-engineer",
    "director-of-engineering", "cto", "vp-engineering"
]

SERVICES = ["api-service", "payment-service", "frontend-app", "data-pipeline", "infrastructure"]

def get_db_connection():
    """Get database connection from environment."""
    import psycopg2
    from urllib.parse import urlparse
    
    postgres_url = os.getenv("POSTGRES_URL", "postgresql://goliath:goliath@postgres:5432/goliath")
    parsed = urlparse(postgres_url)
    
    # Try connecting with retries
    max_retries = 5
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname or "postgres",
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
                raise

def seed_jira_data():
    """Seed Jira Simulator database with realistic data."""
    print("🌱 Seeding Jira Simulator...")
    
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
        
        # Create projects
        print("  Creating projects...")
        projects = []
        for service in SERVICES:
            project_key = service.upper().replace("-", "")[:10]
            cur.execute("""
                INSERT INTO jira_projects (key, name, project_type_key)
                VALUES (%s, %s, 'software')
                ON CONFLICT (key) DO NOTHING
            """, (project_key, service))
            projects.append({"key": project_key, "name": service})
        
        conn.commit()
        print(f"  ✅ Created {len(projects)} projects")
        
        # Create 200 users
        print("  Creating 200 users...")
        users = []
        for i in range(200):
            role = random.choice(ROLES)
            max_story_points = random.choice([13, 21, 34])  # 2-week, 3-week, 5-week capacity
            account_id = f"557058:{fake.uuid4()[:8]}"
            
            cur.execute("""
                INSERT INTO jira_users (account_id, display_name, email_address, active, max_story_points, current_story_points, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (account_id) DO NOTHING
            """, (
                account_id,
                fake.name(),
                fake.email(),
                True,
                max_story_points,
                0,  # Will be updated after creating open tickets
                role
            ))
            
            users.append({
                "account_id": account_id,
                "max_story_points": max_story_points,
                "current_story_points": 0
            })
        
        conn.commit()
        print(f"  ✅ Created {len(users)} users")
        
        # Create closed tickets (last 90 days)
        print("  Creating closed tickets...")
        start_date = datetime.now() - timedelta(days=90)
        closed_count = 0
        
        for _ in range(5000):
            project = random.choice(projects)
            assignee = random.choice(users)
            created_at = fake.date_time_between(start_date=start_date, end_date='now')
            resolved_at = created_at + timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            
            issue_type = random.choice(["Bug", "Task", "Story"])
            priority = random.choice(["Critical", "High", "Medium", "Low"])
            story_points = random.choice([1, 2, 3, 5, 8, 13]) if issue_type != "Bug" else None
            
            issue_id = fake.uuid4()
            issue_key = f"{project['key']}-{random.randint(100, 9999)}"
            reporter = random.choice(users)
            
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
                fake.sentence(),
                fake.text(),
                issue_type,
                priority,
                "Done",
                assignee['account_id'],
                reporter['account_id'],
                story_points,
                created_at,
                resolved_at,
                resolved_at
            ))
            
            if cur.rowcount > 0:
                closed_count += 1
        
        conn.commit()
        print(f"  ✅ Created {closed_count} closed tickets")
        
        # Create open tickets (current capacity)
        print("  Creating open tickets...")
        open_count = 0
        
        for _ in range(1000):
            project = random.choice(projects)
            assignee = random.choice(users)
            created_at = fake.date_time_between(start_date=start_date, end_date='now')
            
            issue_type = random.choice(["Bug", "Task", "Story"])
            priority = random.choice(["Critical", "High", "Medium", "Low"])
            story_points = random.choice([1, 2, 3, 5, 8, 13]) if issue_type != "Bug" else None
            status = random.choice(["To Do", "In Progress"])
            
            issue_id = fake.uuid4()
            issue_key = f"{project['key']}-{random.randint(100, 9999)}"
            reporter = random.choice(users)
            
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
                fake.sentence(),
                fake.text(),
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
                open_count += 1
                # Update user's current_story_points
                if story_points:
                    assignee['current_story_points'] += story_points
        
        conn.commit()
        print(f"  ✅ Created {open_count} open tickets")
        
        # Update user current_story_points
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
        print("✅ Jira Simulator seeded successfully!")
        print(f"   - {len(projects)} projects")
        print(f"   - {len(users)} users")
        print(f"   - {closed_count} closed tickets")
        print(f"   - {open_count} open tickets")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_jira_data()

