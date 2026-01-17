#!/usr/bin/env python3
"""
Repository Analysis Tool
Analyzes repository structure, frameworks, and generates consolidation plan
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class RepositoryAnalyzer:
    """Analyzes repository structure and content"""
    
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "repo_path": str(repo_path),
            "structure": {},
            "frameworks": [],
            "languages": defaultdict(int),
            "file_types": defaultdict(int),
            "total_files": 0,
            "total_lines": 0,
            "directories": []
        }
        
        self.exclude_dirs = {".git", "node_modules", "venv", "__pycache__", 
                            "dist", "build", ".next", "backups", "source"}
        
        self.framework_indicators = {
            "React": ["package.json", "jsx", "tsx"],
            "Vue": ["vue.config.js", ".vue"],
            "Angular": ["angular.json", ".component.ts"],
            "Next.js": ["next.config.js"],
            "Vite": ["vite.config.js", "vite.config.ts"],
            "FastAPI": ["from fastapi", "FastAPI()"],
            "Flask": ["from flask", "Flask(__name__)"],
            "Django": ["django", "settings.py"],
            "Express": ["express", "app.listen"],
            "TypeScript": ["tsconfig.json"],
            "Tailwind": ["tailwind.config.js"],
            "PostgreSQL": ["asyncpg", "psycopg2"],
            "MongoDB": ["pymongo", "motor"],
            "Redis": ["redis", "aioredis"],
            "Solidity": [".sol"],
            "Web3": ["web3", "ethers"],
            "Blockchain": ["blockchain", "smart contract"]
        }
        
        self.language_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JavaScript (React)",
            ".tsx": "TypeScript (React)",
            ".sol": "Solidity",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".md": "Markdown",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".sh": "Shell",
            ".sql": "SQL"
        }

    def analyze(self):
        """Run complete repository analysis"""
        print("🔍 Analyzing repository structure...")
        self._scan_directory()
        self._detect_frameworks()
        self._generate_structure_tree()
        print("✅ Analysis complete!")

    def _scan_directory(self):
        """Scan directory and collect file statistics"""
        for root, dirs, files in os.walk(self.repo_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            rel_root = Path(root).relative_to(self.repo_path)
            if str(rel_root) != ".":
                self.analysis["directories"].append(str(rel_root))
            
            for file in files:
                filepath = Path(root) / file
                self._analyze_file(filepath)

    def _analyze_file(self, filepath):
        """Analyze individual file"""
        try:
            self.analysis["total_files"] += 1
            
            # Count file type
            ext = filepath.suffix.lower()
            self.analysis["file_types"][ext] += 1
            
            # Detect language
            if ext in self.language_extensions:
                lang = self.language_extensions[ext]
                self.analysis["languages"][lang] += 1
            
            # Count lines for text files
            if ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".json", 
                      ".yaml", ".yml", ".html", ".css", ".sh", ".sol"]:
                try:
                    with open(filepath, "r", errors="ignore") as f:
                        lines = len(f.readlines())
                        self.analysis["total_lines"] += lines
                except:
                    pass
                    
        except Exception as e:
            pass

    def _detect_frameworks(self):
        """Detect frameworks and technologies used"""
        detected = set()
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                filepath = Path(root) / file
                
                # Check filename-based detection
                for framework, indicators in self.framework_indicators.items():
                    for indicator in indicators:
                        if indicator in file:
                            detected.add(framework)
                
                # Check content-based detection for code files
                if filepath.suffix in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                    try:
                        with open(filepath, "r", errors="ignore") as f:
                            content = f.read(10000)  # Read first 10KB
                            for framework, indicators in self.framework_indicators.items():
                                for indicator in indicators:
                                    if indicator in content:
                                        detected.add(framework)
                    except:
                        pass
        
        self.analysis["frameworks"] = sorted(list(detected))

    def _generate_structure_tree(self):
        """Generate directory structure tree"""
        structure = {}
        
        for directory in sorted(self.analysis["directories"]):
            parts = Path(directory).parts
            current = structure
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        self.analysis["structure"] = structure

    def save_report(self, output_file="analysis.json"):
        """Save analysis report"""
        with open(output_file, "w") as f:
            json.dump(self.analysis, f, indent=2)

    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📊 REPOSITORY ANALYSIS REPORT")
        print("="*60)
        print(f"📁 Total Files: {self.analysis['total_files']}")
        print(f"📝 Total Lines: {self.analysis['total_lines']:,}")
        print(f"📂 Directories: {len(self.analysis['directories'])}")
        print(f"\n🔧 Detected Frameworks:")
        for framework in self.analysis["frameworks"]:
            print(f"   • {framework}")
        print(f"\n💻 Languages Used:")
        for lang, count in sorted(self.analysis["languages"].items(), 
                                  key=lambda x: x[1], reverse=True):
            print(f"   • {lang}: {count} files")
        print(f"\n📄 File Types:")
        for ext, count in sorted(self.analysis["file_types"].items(), 
                                key=lambda x: x[1], reverse=True)[:10]:
            ext_display = ext if ext else "(no extension)"
            print(f"   • {ext_display}: {count} files")
        print("="*60 + "\n")


def main():
    analyzer = RepositoryAnalyzer()
    print("🔍 Starting repository analysis...")
    analyzer.analyze()
    analyzer.save_report()
    analyzer.print_summary()
    print("✅ Analysis saved to analysis.json\n")


if __name__ == "__main__":
    main()
