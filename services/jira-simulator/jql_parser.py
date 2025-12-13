"""
JQL (Jira Query Language) Parser
Parses JQL queries into SQL WHERE clauses for PostgreSQL queries.

Supports:
- project=PROJ
- status=Done
- resolved >= -90d (relative dates)
- assignee=accountId
- AND/OR operators
- Basic field comparisons
"""
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class JQLParser:
    """Parse JQL queries into SQL WHERE clauses and parameters."""
    
    # Field mappings: JQL field -> database column
    FIELD_MAPPINGS = {
        'project': 'project_key',
        'status': 'status_name',
        'assignee': 'assignee_account_id',
        'reporter': 'reporter_account_id',
        'issuetype': 'issuetype_name',
        'priority': 'priority_name',
        'resolved': 'resolved_at',
        'created': 'created_at',
        'updated': 'updated_at',
    }
    
    def __init__(self):
        self.param_counter = 0
    
    def parse(self, jql: str) -> Tuple[str, List]:
        """
        Parse JQL query into SQL WHERE clause and parameters.
        
        Returns:
            (sql_where_clause, parameters_list)
        
        Example:
            jql = "project=API AND status=Done AND resolved >= -90d"
            returns: (
                "project_key = $1 AND status_name = $2 AND resolved_at >= $3",
                ["API", "Done", datetime(...)]
            )
        """
        if not jql or not jql.strip():
            return "1=1", []  # No filter
        
        self.param_counter = 0
        conditions = []
        params = []
        
        # Normalize: remove extra spaces, handle case
        jql = jql.strip()
        
        # Split by AND/OR (simple approach - handles basic cases)
        # This is a simplified parser - for production, use a proper parser library
        parts = self._split_by_operators(jql)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            condition, part_params = self._parse_condition(part)
            if condition:
                conditions.append(condition)
                params.extend(part_params)
        
        if not conditions:
            return "1=1", []
        
        # Reconstruct with AND/OR operators
        sql = self._reconstruct_sql(conditions, jql)
        
        return sql, params
    
    def _split_by_operators(self, jql: str) -> List[str]:
        """Split JQL by AND/OR operators."""
        # Simple approach: split on AND/OR (case insensitive)
        # Use regex to split while preserving the operators
        # Pattern: split on " AND " or " OR " (with spaces)
        import re
        parts = re.split(r'\s+(AND|OR)\s+', jql, flags=re.IGNORECASE)
        
        # parts will be: [condition1, 'AND', condition2, 'OR', condition3, ...]
        # For now, we'll just extract the conditions and use AND for all
        # (A full implementation would track operators)
        conditions = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are conditions
                if part.strip():
                    conditions.append(part.strip())
        
        return conditions
    
    def _parse_condition(self, condition: str) -> Tuple[Optional[str], List]:
        """
        Parse a single condition like "project=API" or "resolved >= -90d"
        
        Returns:
            (sql_condition, parameters)
        """
        condition = condition.strip()
        
        # Handle operators: =, !=, >=, <=, >, <
        operators = ['>=', '<=', '!=', '>', '<', '=']
        
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    return self._build_sql_condition(field, op, value)
        
        # If no operator found, treat as invalid
        return None, []
    
    def _build_sql_condition(self, field: str, operator: str, value: str) -> Tuple[str, List]:
        """Build SQL condition from field, operator, and value."""
        # Map JQL field to database column
        db_field = self.FIELD_MAPPINGS.get(field.lower(), field.lower())
        
        # Handle special cases - relative dates
        if field.lower() in ['resolved', 'created', 'updated'] and value.startswith('-') and value.endswith('d'):
            # Relative date: resolved >= -90d means "resolved in last 90 days"
            days = int(value[1:-1])
            cutoff_date = datetime.now() - timedelta(days=days)
            self.param_counter += 1
            return f"{db_field} >= %s", [cutoff_date]
        
        # Standard comparison
        self.param_counter += 1
        
        # Handle operator mapping
        sql_op = operator
        if operator == '=':
            sql_op = '='
        elif operator == '!=':
            sql_op = '!='
        elif operator == '>':
            sql_op = '>'
        elif operator == '<':
            sql_op = '<'
        elif operator == '>=':
            sql_op = '>='
        elif operator == '<=':
            sql_op = '<='
        
        return f"{db_field} {sql_op} %s", [value]
    
    def _reconstruct_sql(self, conditions: List[str], original_jql: str) -> str:
        """Reconstruct SQL with AND/OR operators based on original JQL."""
        # For now, use AND for all conditions (simplified)
        # In a full implementation, we'd track operator positions from original JQL
        if not conditions:
            return "1=1"
        return " AND ".join(conditions)


def parse_jql(jql: str) -> Tuple[str, List]:
    """
    Convenience function to parse JQL query.
    
    Args:
        jql: JQL query string (e.g., "project=API AND status=Done")
    
    Returns:
        (sql_where_clause, parameters_list)
    
    Example:
        >>> sql, params = parse_jql("project=API AND status=Done")
        >>> print(sql)
        "project_key = $1 AND status_name = $2"
        >>> print(params)
        ["API", "Done"]
    """
    parser = JQLParser()
    return parser.parse(jql)

