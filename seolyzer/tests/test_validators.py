"""
Tests für die Validierungsfunktionen
"""

import unittest
from seolyzer.utils.validators import validate_url, validate_depth, validate_output_path

class TestValidators(unittest.TestCase):
    def test_validate_url(self):
        # Test gültige URLs
        self.assertTrue(validate_url("https://example.com")[0])
        self.assertTrue(validate_url("http://example.com")[0])
        self.assertTrue(validate_url("example.com")[0])
        
        # Test ungültige URLs
        self.assertFalse(validate_url("")[0])
        self.assertFalse(validate_url("not-a-url")[0])
        self.assertFalse(validate_url("http://")[0])
    
    def test_validate_depth(self):
        # Test gültige Tiefen
        self.assertTrue(validate_depth(1)[0])
        self.assertTrue(validate_depth(5)[0])
        self.assertTrue(validate_depth(10)[0])
        
        # Test ungültige Tiefen
        self.assertFalse(validate_depth(0)[0])
        self.assertFalse(validate_depth(11)[0])
        self.assertFalse(validate_depth(-1)[0])
    
    def test_validate_output_path(self):
        # Test gültige Pfade
        self.assertTrue(validate_output_path("report.json")[0])
        self.assertTrue(validate_output_path("output/report.json")[0])
        
        # Test ungültige Pfade
        self.assertFalse(validate_output_path("")[0])
        self.assertFalse(validate_output_path("report.txt")[0])
        self.assertFalse(validate_output_path("report.json/")[0])

if __name__ == '__main__':
    unittest.main() 