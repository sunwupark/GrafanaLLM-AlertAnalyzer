"""
Service Test
"""

import pytest

from app.utils.text import clean_text, extract_analysis_sections


def test_clean_text():
    test_text = "<h1>Hello\nWorld</h1>  with   multiple    spaces"
    result = clean_text(test_text)
    assert result == "Hello World with multiple spaces"
    assert clean_text(None) == ""
    assert clean_text("") == ""


def test_extract_analysis_sections():
    test_content = """
    This is some preliminary text.
    
    Problem: The database has high CPU usage.
    The load is exceeding capacity.
    
    Cause of Problem: Too many concurrent requests
    are being processed without proper throttling.
    This leads to resource exhaustion.
    
    Solution: Implement connection pooling and
    rate limiting to prevent overload.
    Scale up the database as a short-term solution.
    
    Some additional notes.
    """

    result = extract_analysis_sections(test_content)

    assert "problem" in result
    assert "cause" in result
    assert "solution" in result

    assert "database has high CPU usage" in result["problem"]
    assert "load is exceeding capacity" in result["problem"]

    assert "Too many concurrent requests" in result["cause"]
    assert "resource exhaustion" in result["cause"]

    assert "connection pooling" in result["solution"]
    assert "short-term solution" in result["solution"]
