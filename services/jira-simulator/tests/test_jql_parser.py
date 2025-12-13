"""
Tests for JQL Parser.
"""
import pytest
from datetime import datetime, timedelta
from jql_parser import parse_jql, JQLParser


class TestJQLParserBasic:
    """Test basic JQL parsing."""
    
    def test_simple_equality(self):
        """Parse simple equality condition."""
        jql = "project=API"
        sql, params = parse_jql(jql)
        
        assert "project_key" in sql.lower()
        assert "=" in sql
        assert len(params) == 1
        assert params[0] == "API"
    
    def test_and_operator(self):
        """Parse AND operator."""
        jql = "project=API AND status=Done"
        sql, params = parse_jql(jql)
        
        assert "AND" in sql.upper()
        assert len(params) == 2
        assert "API" in params
        assert "Done" in params
    
    def test_or_operator(self):
        """Parse OR operator."""
        jql = "status=Done OR status=Closed"
        sql, params = parse_jql(jql)
        
        assert "OR" in sql.upper()
        assert len(params) == 2
        assert "Done" in params
        assert "Closed" in params
    
    def test_mixed_and_or(self):
        """Parse mixed AND/OR operators."""
        jql = "project=API AND status=Done OR status=Closed"
        sql, params = parse_jql(jql)
        
        assert "AND" in sql.upper() or "OR" in sql.upper()
        assert len(params) >= 2
    
    def test_relative_date(self):
        """Parse relative date queries."""
        jql = "resolved >= -90d"
        sql, params = parse_jql(jql)
        
        assert "resolved_at" in sql.lower()
        assert ">=" in sql
        assert len(params) == 1
        assert isinstance(params[0], datetime)
        
        # Check date is approximately 90 days ago
        expected_date = datetime.now() - timedelta(days=90)
        assert abs((params[0] - expected_date).total_seconds()) < 86400  # Within 1 day
    
    def test_quoted_values(self):
        """Parse quoted values."""
        jql = 'project="API" AND status="Done"'
        sql, params = parse_jql(jql)
        
        assert len(params) == 2
        assert params[0] == "API"
        assert params[1] == "Done"
    
    def test_empty_query(self):
        """Handle empty query."""
        sql, params = parse_jql("")
        
        assert sql == "1=1"
        assert params == []
    
    def test_whitespace_handling(self):
        """Handle extra whitespace."""
        jql = "  project = API   AND   status = Done  "
        sql, params = parse_jql(jql)
        
        assert len(params) == 2
        assert "API" in params
        assert "Done" in params


class TestJQLParserOperators:
    """Test different operators."""
    
    def test_greater_than(self):
        """Parse > operator."""
        jql = "story_points > 5"
        sql, params = parse_jql(jql)
        
        assert ">" in sql
        assert len(params) == 1
    
    def test_less_than(self):
        """Parse < operator."""
        jql = "story_points < 10"
        sql, params = parse_jql(jql)
        
        assert "<" in sql
        assert len(params) == 1
    
    def test_greater_equal(self):
        """Parse >= operator."""
        jql = "resolved >= -30d"
        sql, params = parse_jql(jql)
        
        assert ">=" in sql
        assert len(params) == 1
    
    def test_not_equal(self):
        """Parse != operator."""
        jql = "status != Done"
        sql, params = parse_jql(jql)
        
        assert "!=" in sql or "<>" in sql
        assert len(params) == 1


class TestJQLParserFieldMapping:
    """Test field name mapping."""
    
    def test_project_mapping(self):
        """Map 'project' to 'project_key'."""
        jql = "project=API"
        sql, params = parse_jql(jql)
        
        assert "project_key" in sql.lower()
    
    def test_status_mapping(self):
        """Map 'status' to 'status_name'."""
        jql = "status=Done"
        sql, params = parse_jql(jql)
        
        assert "status_name" in sql.lower()
    
    def test_assignee_mapping(self):
        """Map 'assignee' to 'assignee_account_id'."""
        jql = "assignee=557058:abc123"
        sql, params = parse_jql(jql)
        
        assert "assignee_account_id" in sql.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

