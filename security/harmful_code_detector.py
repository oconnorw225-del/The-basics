"""
HARMFUL CODE DETECTION SYSTEM
Three-Stage Approval System for Security-Critical Changes

This module implements automated detection of potentially harmful code patterns
that could hinder uptime, cause system slowdowns, or introduce malicious behavior.
"""

import re
import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class ThreatPattern:
    """Definition of a harmful code pattern"""
    name: str
    pattern: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    impact: str
    recommendation: str
    regex_flags: int = re.IGNORECASE | re.MULTILINE


@dataclass
class DetectionResult:
    """Result of harmful code detection"""
    file_path: str
    threats: List[Dict] = field(default_factory=list)
    approval_required: bool = False
    danger_report: str = ""
    
    
class HarmfulCodeDetector:
    """
    Automated detector for potentially harmful code patterns.
    Requires three-stage approval for security-critical changes.
    """
    
    # Define harmful patterns
    THREAT_PATTERNS = [
        ThreatPattern(
            name="pipe_to_shell",
            pattern=r"curl\s+.*\|\s*(bash|sh|zsh|python|ruby|perl)",
            severity="CRITICAL",
            description="Piping remote content directly to shell interpreter",
            impact="Can execute arbitrary malicious code from compromised or MITM'd servers",
            recommendation="Download files, verify checksums/signatures, then execute"
        ),
        ThreatPattern(
            name="secrets_in_subprocess_env",
            pattern=r"(SECRET|PASSWORD|TOKEN|API_KEY|PRIVATE_KEY).*:\s*\$\{\{.*secrets\.",
            severity="CRITICAL",
            description="Passing secrets as subprocess environment variables",
            impact="Secrets visible in process listings and logs, potential credential exposure",
            recommendation="Use secure file passing with restricted permissions or stdin"
        ),
        ThreatPattern(
            name="unverified_dynamic_import",
            pattern=r"(exec|eval|importlib\.util\.(spec_from_file_location|module_from_spec))",
            severity="HIGH",
            description="Dynamic code execution without integrity verification",
            impact="Arbitrary code execution if source files are compromised",
            recommendation="Add file integrity checks (SHA256) before dynamic loading"
        ),
        ThreatPattern(
            name="infinite_loop",
            pattern=r"while\s+(True|1|true)\s*:\s*(?!.*break)(?!.*return)",
            severity="HIGH",
            description="Infinite loop without break condition",
            impact="CPU exhaustion, system freeze, uptime degradation",
            recommendation="Add timeout, break condition, or resource limits"
        ),
        ThreatPattern(
            name="recursive_without_limit",
            pattern=r"def\s+(\w+)\([^)]*\):[^}]*\1\(",
            severity="MEDIUM",
            description="Recursive function without depth limit",
            impact="Stack overflow, memory exhaustion, system crash",
            recommendation="Add recursion depth limit or use iteration"
        ),
        ThreatPattern(
            name="unsafe_file_permissions",
            pattern=r"chmod\s+(777|666|0o777|0o666)",
            severity="HIGH",
            description="Setting overly permissive file permissions",
            impact="Unauthorized file access, privilege escalation",
            recommendation="Use minimum required permissions (600 for secrets, 700 for dirs)"
        ),
        ThreatPattern(
            name="hardcoded_credentials",
            pattern=r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}['\"]",
            severity="CRITICAL",
            description="Hardcoded credentials in source code",
            impact="Credential exposure in version control, unauthorized access",
            recommendation="Use environment variables or secure vaults"
        ),
        ThreatPattern(
            name="sql_injection_risk",
            pattern=r"(execute|executemany|cursor\.execute)\s*\([^?]*%s|f['\"].*SELECT.*FROM",
            severity="HIGH",
            description="Potential SQL injection vulnerability",
            impact="Database compromise, data theft, data manipulation",
            recommendation="Use parameterized queries or ORM"
        ),
        ThreatPattern(
            name="command_injection_risk",
            pattern=r"(os\.system|subprocess\.(call|run|Popen))\s*\([^)]*f['\"]",
            severity="HIGH",
            description="Potential command injection via string formatting",
            impact="Arbitrary command execution, system compromise",
            recommendation="Use subprocess with list arguments, validate inputs"
        ),
        ThreatPattern(
            name="insecure_deserialization",
            pattern=r"(pickle\.loads|yaml\.load(?!_safe)|marshal\.loads)\s*\(",
            severity="HIGH",
            description="Insecure deserialization of untrusted data",
            impact="Remote code execution, object injection attacks",
            recommendation="Use yaml.safe_load or json.loads for untrusted data"
        ),
        ThreatPattern(
            name="disabled_ssl_verification",
            pattern=r"verify\s*=\s*(False|0)|VERIFY\s*=\s*(False|0)",
            severity="HIGH",
            description="Disabled SSL/TLS certificate verification",
            impact="Man-in-the-middle attacks, credential interception",
            recommendation="Always verify SSL certificates in production"
        ),
        ThreatPattern(
            name="excessive_memory_allocation",
            pattern=r"(\[\s*0\s*\]\s*\*\s*[0-9]{7,}|\{[^}]*:\s*None\s*for\s+\w+\s+in\s+range\([0-9]{7,}\))",
            severity="MEDIUM",
            description="Large memory allocation that could exhaust resources",
            impact="Out of memory errors, system slowdown, denial of service",
            recommendation="Use generators, streaming, or chunked processing"
        ),
        ThreatPattern(
            name="unprotected_network_binding",
            pattern=r"(bind|listen)\s*\(\s*['\"]0\.0\.0\.0['\"]",
            severity="MEDIUM",
            description="Binding to all network interfaces without authentication",
            impact="Unauthorized network access, potential attack surface",
            recommendation="Bind to specific interfaces or add authentication"
        ),
        ThreatPattern(
            name="debug_mode_enabled",
            pattern=r"(DEBUG\s*=\s*True|app\.debug\s*=\s*True|debug\s*=\s*True)",
            severity="MEDIUM",
            description="Debug mode enabled in production",
            impact="Information disclosure, stack traces visible to attackers",
            recommendation="Disable debug mode in production environments"
        ),
    ]
    
    def __init__(self):
        """Initialize the harmful code detector"""
        self.detection_log = []
        self.approval_history = []
        
    def scan_file(self, file_path: str) -> DetectionResult:
        """
        Scan a single file for harmful code patterns.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            DetectionResult with detected threats
        """
        result = DetectionResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            result.danger_report = f"ERROR: Could not read file: {e}"
            return result
        
        # Scan for each threat pattern
        for pattern in self.THREAT_PATTERNS:
            matches = re.finditer(pattern.pattern, content, pattern.regex_flags)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                result.threats.append({
                    'name': pattern.name,
                    'severity': pattern.severity,
                    'line': line_num,
                    'match': match.group(0)[:100],  # First 100 chars
                    'description': pattern.description,
                    'impact': pattern.impact,
                    'recommendation': pattern.recommendation
                })
        
        # Determine if approval required
        critical_count = sum(1 for t in result.threats if t['severity'] == 'CRITICAL')
        high_count = sum(1 for t in result.threats if t['severity'] == 'HIGH')
        
        if critical_count > 0 or high_count >= 2:
            result.approval_required = True
            result.danger_report = self._generate_danger_report(result)
        
        return result
    
    def scan_directory(self, directory: str, extensions: Optional[List[str]] = None) -> List[DetectionResult]:
        """
        Scan all files in a directory recursively.
        
        Args:
            directory: Directory to scan
            extensions: File extensions to scan (default: ['.py', '.js', '.yml', '.yaml', '.sh'])
            
        Returns:
            List of DetectionResults
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.yml', '.yaml', '.sh', '.bash']
        
        results = []
        for root, _, files in os.walk(directory):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    result = self.scan_file(file_path)
                    if result.threats:
                        results.append(result)
        
        return results
    
    def _generate_danger_report(self, result: DetectionResult) -> str:
        """Generate detailed danger report for threats requiring approval"""
        report_lines = [
            "=" * 80,
            f"SECURITY THREAT REPORT: {result.file_path}",
            "=" * 80,
            "",
            "⚠️  THREE-STAGE APPROVAL REQUIRED ⚠️",
            "",
            "This file contains potentially harmful code patterns that could:",
            "  • Hinder system uptime",
            "  • Cause system slowdowns or shutdowns",
            "  • Introduce malicious behavior",
            "  • Expose sensitive credentials",
            "",
            "DETECTED THREATS:",
            ""
        ]
        
        # Group by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            threats = [t for t in result.threats if t['severity'] == severity]
            if not threats:
                continue
                
            report_lines.append(f"{severity} THREATS ({len(threats)}):")
            report_lines.append("-" * 80)
            
            for i, threat in enumerate(threats, 1):
                report_lines.extend([
                    f"{i}. {threat['name'].replace('_', ' ').title()}",
                    f"   Line: {threat['line']}",
                    f"   Code: {threat['match']}",
                    f"   Description: {threat['description']}",
                    f"   Impact: {threat['impact']}",
                    f"   Recommendation: {threat['recommendation']}",
                    ""
                ])
        
        report_lines.extend([
            "=" * 80,
            "APPROVAL PROCESS:",
            "=" * 80,
            "",
            "To approve these changes, you must provide THREE explicit confirmations:",
            "",
            "1. FIRST APPROVAL: Acknowledge you understand the threats above",
            "2. SECOND APPROVAL: Confirm the changes are necessary and benefits outweigh risks",
            "3. THIRD APPROVAL: Verify all recommended mitigations have been applied",
            "",
            "Each approval must include a full review of the dangers and issues.",
            "=" * 80,
        ])
        
        return "\n".join(report_lines)
    
    def generate_summary_report(self, results: List[DetectionResult]) -> str:
        """Generate a summary report of all detected threats"""
        total_files = len(results)
        total_threats = sum(len(r.threats) for r in results)
        files_requiring_approval = sum(1 for r in results if r.approval_required)
        
        critical_threats = sum(1 for r in results for t in r.threats if t['severity'] == 'CRITICAL')
        high_threats = sum(1 for r in results for t in r.threats if t['severity'] == 'HIGH')
        medium_threats = sum(1 for r in results for t in r.threats if t['severity'] == 'MEDIUM')
        
        summary = [
            "",
            "=" * 80,
            "HARMFUL CODE DETECTION SUMMARY",
            "=" * 80,
            "",
            f"Files Scanned: {total_files}",
            f"Total Threats Detected: {total_threats}",
            f"Files Requiring Approval: {files_requiring_approval}",
            "",
            "Threats by Severity:",
            f"  🔴 CRITICAL: {critical_threats}",
            f"  🟠 HIGH: {high_threats}",
            f"  🟡 MEDIUM: {medium_threats}",
            "",
        ]
        
        if files_requiring_approval > 0:
            summary.extend([
                "⚠️  ACTION REQUIRED ⚠️",
                "",
                "The following files require three-stage approval:",
                ""
            ])
            
            for result in results:
                if result.approval_required:
                    summary.append(f"  • {result.file_path} ({len(result.threats)} threats)")
            
            summary.extend([
                "",
                "Review the detailed danger reports for each file before proceeding.",
                ""
            ])
        else:
            summary.extend([
                "✅ No critical threats requiring approval detected.",
                ""
            ])
        
        summary.append("=" * 80)
        return "\n".join(summary)


def main():
    """Main entry point for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python harmful_code_detector.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    detector = HarmfulCodeDetector()
    
    if os.path.isfile(target):
        result = detector.scan_file(target)
        if result.threats:
            print(result.danger_report if result.danger_report else "Threats detected - see details above")
            sys.exit(1 if result.approval_required else 0)
        else:
            print(f"✅ No threats detected in {target}")
            sys.exit(0)
    elif os.path.isdir(target):
        results = detector.scan_directory(target)
        print(detector.generate_summary_report(results))
        
        # Print detailed reports for files requiring approval
        for result in results:
            if result.approval_required:
                print("\n" + result.danger_report)
        
        sys.exit(1 if any(r.approval_required for r in results) else 0)
    else:
        print(f"ERROR: {target} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
