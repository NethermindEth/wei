"""
Tests for the JSON parser utilities.
"""

import unittest
from app.utils.json_parser import extract_json_from_markdown, try_extract_json_from_markdown


class TestJsonParser(unittest.TestCase):
    """Test cases for JSON parser utilities."""
    
    def test_standard_markdown_code_block(self):
        """Test parsing JSON from standard markdown code blocks."""
        content = """
        Here's some JSON:
        
        ```json
        {
            "name": "test",
            "value": 123
        }
        ```
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result, {"name": "test", "value": 123})
    
    def test_uppercase_json_marker(self):
        """Test parsing JSON with uppercase JSON marker."""
        content = """
        ```JSON
        {
            "name": "test",
            "value": 123
        }
        ```
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result, {"name": "test", "value": 123})
    
    def test_no_language_marker(self):
        """Test parsing JSON with no language marker."""
        content = """
        ```
        {
            "name": "test",
            "value": 123
        }
        ```
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result, {"name": "test", "value": 123})
    
    def test_alternative_code_block_markers(self):
        """Test parsing JSON with alternative code block markers."""
        content = """
        ~~~json
        {
            "name": "test",
            "value": 123
        }
        ~~~
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result, {"name": "test", "value": 123})
    
    def test_json_without_markers(self):
        """Test parsing JSON without any code block markers."""
        content = """
        {
            "name": "test",
            "value": 123
        }
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result, {"name": "test", "value": 123})
    
    def test_json_with_surrounding_text(self):
        """Test parsing JSON with surrounding explanatory text."""
        content = """
        Here's the evaluation result:
        
        {
            "summary": "This is a good proposal",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Good reasoning"
                }
            }
        }
        
        I hope this helps!
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result["summary"], "This is a good proposal")
        self.assertEqual(result["response_map"]["criteria1"]["status"], "pass")
    
    def test_nested_json(self):
        """Test parsing complex nested JSON objects."""
        content = """
        ```json
        {
            "name": "test",
            "values": [1, 2, 3],
            "nested": {
                "a": "value",
                "b": [{"x": 1}, {"y": 2}]
            }
        }
        ```
        """
        success, result = extract_json_from_markdown(content)
        self.assertTrue(success)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["values"], [1, 2, 3])
        self.assertEqual(result["nested"]["a"], "value")
        self.assertEqual(result["nested"]["b"][1]["y"], 2)
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        content = """
        ```json
        {
            "name": "test",
            "value": 123,
        }
        ```
        """
        success, result = extract_json_from_markdown(content)
        self.assertFalse(success)
        self.assertIsInstance(result, str)
    
    def test_empty_content(self):
        """Test handling of empty content."""
        success, result = extract_json_from_markdown("")
        self.assertFalse(success)
        self.assertIsInstance(result, str)
    
    def test_try_extract_json_from_markdown(self):
        """Test the try_extract_json_from_markdown function."""
        # Valid JSON
        content = '{"name": "test", "value": 123}'
        result = try_extract_json_from_markdown(content)
        self.assertEqual(result, {"name": "test", "value": 123})
        
        # Invalid JSON
        content = '{"name": "test", value: 123}'
        result = try_extract_json_from_markdown(content)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
