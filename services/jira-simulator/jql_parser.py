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
                "project_key = %s AND status_name = %s AND resolved_at >= %s",
                ["API", "Done", datetime(...)]
            )
            
            jql = "status=Done OR status=Closed"
            returns: (
                "status_name = %s OR status_name = %s",
                ["Done", "Closed"]
            )
        """
        if not jql or not jql.strip():
            return "1=1", []  # No filter
        
        self.param_counter = 0
        jql = jql.strip()
        
        # Split by AND/OR operators, preserving operator order
        condition_strings, operators = self._split_by_operators(jql)
        
        if not condition_strings:
            return "1=1", []
        
        # Parse each condition
        sql_conditions = []
        params = []
        
        for condition_str in condition_strings:
            condition_str = condition_str.strip()
            if not condition_str:
                continue
            
            sql_condition, condition_params = self._parse_condition(condition_str)
            if sql_condition:
                sql_conditions.append(sql_condition)
                params.extend(condition_params)
        
        if not sql_conditions:
            return "1=1", []
        
        # Reconstruct SQL with proper AND/OR operators
        sql = self._reconstruct_sql(sql_conditions, operators)
        
        return sql, params
    
    def _split_by_operators(self, jql: str) -> Tuple[List[str], List[str]]:
        """
        Split JQL by AND/OR operators, preserving operator order.
        
        Returns:
            (conditions_list, operators_list)
            e.g., ("project=API AND status=Done OR status=Closed") 
            -> (["project=API", "status=Done", "status=Closed"], ["AND", "OR"])
        """
        import re
        # Split on " AND " or " OR " (with spaces), case insensitive
        parts = re.split(r'\s+(AND|OR)\s+', jql, flags=re.IGNORECASE)
        
        conditions = []
        operators = []
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are conditions
                if part.strip():
                    conditions.append(part.strip())
            else:  # Odd indices are operators
                operators.append(part.upper())  # Normalize to uppercase
        
        return conditions, operators
    
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
    
    def _reconstruct_sql(self, conditions: List[str], operators: List[str]) -> str:
        """
        Reconstruct SQL with AND/OR operators.
        
        Args:
            conditions: List of SQL conditions (e.g., ["field1 = %s", "field2 = %s"])
            operators: List of operators (e.g., ["AND", "OR"])
        
        Returns:
            SQL WHERE clause with proper operators
        """
        if not conditions:
            return "1=1"
        
        if len(conditions) == 1:
            return conditions[0]
        
        # Reconstruct: condition1 operator1 condition2 operator2 condition3 ...
        # If we have N conditions, we have N-1 operators
        result = conditions[0]
        
        for i in range(1, len(conditions)):
            # Use operator[i-1] between condition[i-1] and condition[i]
            operator = operators[i-1] if i-1 < len(operators) else "AND"
            result += f" {operator} {conditions[i]}"
        
        return result


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

