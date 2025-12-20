#!/usr/bin/env python3
"""
Advanced Security & Code Quality Audit Tool
Integrated with Chimera Intelligence V8.0
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class CodeAuditor:
    """Enhanced security auditor with Chimera intelligence"""
    
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        self.results = {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "chimera_version": "8.0",
            "scanner_version": "2.0",
            "files_scanned": 0,
            "keyword_hits": [],
            "wallet_addresses": [],
            "sensitive_data": [],
            "dependencies": {},
            "code_quality": [],
            "file_stats": {},
            "summary": {}
        }
        
        self.exclude_dirs = {".git", "node_modules", "venv", "__pycache__", 
                            "backups", "source", "dist", "build", ".next"}
        
        self.keywords = [
            "web3", "ethers", "solana", "stripe", "paypal",
            "wallet", "rpc", "infura", "alchemy", "private",
            "seed", "mnemonic", "address", "api_key", "secret",
            "token", "auth", "password", "credential"
        ]
        
        self.wallet_patterns = {
            "ethereum": r"0x[a-fA-F0-9]{40}",
            "solana": r"[1-9A-HJ-NP-Za-km-z]{32,44}",
            "bitcoin": r"(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,90}"
        }
        
        self.sensitive_patterns = {
            "private_key": r"(?i)(private[_-]?key|priv[_-]?key)[\"'\s:=]+[a-fA-F0-9]{64}",
            "api_key": r"(?i)(api[_-]?key|apikey)[\"'\s:=]+[a-zA-Z0-9_\-]{20,}",
            "mnemonic": r"(?i)(mnemonic|seed[_-]?phrase)[\"'\s:=]+([a-z]+\s){11,23}[a-z]+",
            "aws_key": r"AKIA[0-9A-Z]{16}",
            "github_token": r"ghp_[a-zA-Z0-9]{36}",
            "stripe_key": r"sk_live_[a-zA-Z0-9]{24,}",
            "password": r"(?i)(password|passwd|pwd)[\"'\s:=]+[^\s\"']{8,}"
        }
        
        self.code_smells = {
            "hardcoded_ip": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "todo": r"(?i)(TODO|FIXME|HACK|XXX|BUG):",
            "console_log": r"console\.(log|debug|info)",
            "eval": r"\beval\s*\(",
            "sql_query": r"(?i)(SELECT|INSERT|UPDATE|DELETE)\s+.*\s+(FROM|INTO|WHERE)"
        }

    def scan_directory(self):
        """Recursively scan directory with Chimera intelligence"""
        print("🧬 Chimera V8.0 Scanner Activated...")
        print("   Transcendent Analysis Mode: ENABLED\n")
        
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if self.should_scan(file):
                    filepath = Path(root) / file
                    self.scan_file(filepath)

    def scan_file(self, filepath):
        """Scan individual file"""
        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()
            
            self.results["files_scanned"] += 1
            file_info = {
                "size": os.path.getsize(filepath),
                "lines": content.count('\n') + 1,
                "hash": hashlib.md5(content.encode()).hexdigest()
            }
            
            # Keyword search
            for kw in self.keywords:
                count = content.lower().count(kw.lower())
                if count > 0:
                    self.results["keyword_hits"].append({
                        "file": str(filepath),
                        "keyword": kw,
                        "count": count
                    })
            
            # Wallet address search
            for chain, pattern in self.wallet_patterns.items():
                matches = re.findall(pattern, content)
                for match in matches:
                    self.results["wallet_addresses"].append({
                        "chain": chain,
                        "address": match,
                        "file": str(filepath)
                    })
            
            # Sensitive data search
            for data_type, pattern in self.sensitive_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    self.results["sensitive_data"].append({
                        "type": data_type,
                        "file": str(filepath),
                        "count": len(matches),
                        "severity": "CRITICAL" if data_type in ["private_key", "mnemonic"] else "HIGH"
                    })
            
            # Code quality checks
            for smell_type, pattern in self.code_smells.items():
                matches = re.findall(pattern, content)
                if matches:
                    self.results["code_quality"].append({
                        "type": smell_type,
                        "file": str(filepath),
                        "count": len(matches),
                        "severity": "MEDIUM" if smell_type in ["todo", "console_log"] else "HIGH"
                    })
            
            # Dependency extraction
            self.extract_dependencies(filepath, content)
            
            self.results["file_stats"][str(filepath)] = file_info
            
        except Exception as e:
            pass

    def extract_dependencies(self, filepath, content):
        """Extract dependencies from package files"""
        filename = os.path.basename(filepath)
        
        if filename == "package.json":
            try:
                data = json.loads(content)
                self.results["dependencies"]["npm"] = {
                    "file": str(filepath),
                    "dependencies": data.get("dependencies", {}),
                    "devDependencies": data.get("devDependencies", {})
                }
            except:
                pass
        
        elif filename == "requirements.txt":
            deps = [line.strip() for line in content.split('\n') 
                   if line.strip() and not line.startswith('#')]
            self.results["dependencies"]["python"] = {
                "file": str(filepath),
                "packages": deps
            }

    def should_scan(self, filename):
        """Check if file should be scanned"""
        scan_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".json", 
            ".env", ".txt", ".md", ".yaml", ".yml", ".toml",
            ".sol", ".rs", ".go", ".java", ".cpp", ".c"
        }
        return any(filename.endswith(ext) for ext in scan_extensions)

    def generate_summary(self):
        """Generate audit summary"""
        sensitive_files = set(item["file"] for item in self.results["sensitive_data"])
        wallet_files = set(item["file"] for item in self.results["wallet_addresses"])
        
        critical_issues = len([s for s in self.results["sensitive_data"] 
                              if s["severity"] == "CRITICAL"])
        high_issues = len([s for s in self.results["sensitive_data"] 
                          if s["severity"] == "HIGH"])
        
        # Calculate risk level
        if critical_issues > 0:
            risk_level = "CRITICAL"
        elif high_issues > 0 or len(wallet_files) > 0:
            risk_level = "HIGH"
        elif self.results["code_quality"]:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        self.results["summary"] = {
            "total_files": self.results["files_scanned"],
            "files_with_keywords": len(set(hit["file"] for hit in self.results["keyword_hits"])),
            "wallet_addresses_found": len(self.results["wallet_addresses"]),
            "unique_wallet_files": len(wallet_files),
            "sensitive_data_files": len(sensitive_files),
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "code_quality_issues": len(self.results["code_quality"]),
            "dependencies_found": len(self.results["dependencies"]),
            "risk_level": risk_level,
            "total_lines_scanned": sum(f.get("lines", 0) for f in self.results["file_stats"].values())
        }

    def save_report(self, output_file="audit_report.json"):
        """Save audit report"""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self):
        """Print human-readable summary"""
        summary = self.results["summary"]
        print("\n" + "="*60)
        print("🔍 CHIMERA V8.0 SECURITY AUDIT REPORT")
        print("="*60)
        print(f"📁 Files Scanned: {summary['total_files']}")
        print(f"📝 Total Lines: {summary['total_lines_scanned']:,}")
        print(f"⚠️  Risk Level: {summary['risk_level']}")
        print(f"🔴 Critical Issues: {summary['critical_issues']}")
        print(f"🟠 High Issues: {summary['high_issues']}")
        print(f"💰 Wallet Addresses Found: {summary['wallet_addresses_found']}")
        print(f"🔑 Sensitive Data Files: {summary['sensitive_data_files']}")
        print(f"📦 Dependencies Analyzed: {summary['dependencies_found']}")
        print(f"🐛 Code Quality Issues: {summary['code_quality_issues']}")
        print("="*60)
        
        if summary['risk_level'] in ['CRITICAL', 'HIGH']:
            print("\n⚠️  WARNING: Security issues detected!")
            print("Review audit_report.json for details.\n")

def main():
    auditor = CodeAuditor()
    print("🔍 Starting Chimera-powered comprehensive audit...")
    auditor.scan_directory()
    auditor.generate_summary()
    auditor.save_report()
    auditor.print_summary()
    print("✅ Audit complete → audit_report.json\n")

if __name__ == "__main__":
    main()
