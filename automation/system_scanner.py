#!/usr/bin/env python3
"""
Platform Scanner
Scans GitHub, Railway, and other connected platforms for issues
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PlatformScanner')


def scan_github(mode: str = "full") -> Dict:
    """Scan GitHub repositories and workflows"""
    logger.info(f"Scanning GitHub (mode: {mode})...")
    
    results = {
        "platform": "github",
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "findings": []
    }
    
    # Check workflows
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        all_workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        disabled_workflows = list(workflows_dir.glob("*.disabled"))
        
        results["findings"].append({
            "type": "workflows",
            "active_count": len(all_workflows),
            "disabled_count": len(disabled_workflows),
            "details": {
                "active": [w.name for w in all_workflows],
                "disabled": [w.name for w in disabled_workflows]
            }
        })
        
        if disabled_workflows:
            logger.warning(f"Found {len(disabled_workflows)} disabled workflows")
    
    # Check repository files
    critical_files = [
        "backend/chimera_master.py",
        "backend/chimera_base.py",
        "unified_system.py",
        "start_system.py",
        "bot.js",
        "server.js"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        results["findings"].append({
            "type": "missing_files",
            "severity": "high",
            "count": len(missing_files),
            "files": missing_files
        })
        logger.warning(f"Missing {len(missing_files)} critical files")
    
    logger.info("✓ GitHub scan completed")
    return results


def scan_railway(mode: str = "full") -> Dict:
    """Scan Railway deployments"""
    logger.info(f"Scanning Railway (mode: {mode})...")
    
    results = {
        "platform": "railway",
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "findings": []
    }
    
    # Check for Railway token
    railway_token = os.environ.get("RAILWAY_TOKEN")
    
    if not railway_token:
        results["findings"].append({
            "type": "configuration",
            "severity": "high",
            "issue": "Railway token not configured",
            "recommendation": "Set RAILWAY_TOKEN secret in GitHub repository"
        })
        logger.warning("Railway token not configured")
    else:
        results["findings"].append({
            "type": "configuration",
            "severity": "info",
            "status": "Railway token configured"
        })
        logger.info("✓ Railway token configured")
    
    # Check for Railway configuration files
    railway_files = ["railway.json", "railway.toml", "Procfile"]
    found_config = False
    
    for config_file in railway_files:
        if Path(config_file).exists():
            found_config = True
            results["findings"].append({
                "type": "configuration",
                "file": config_file,
                "status": "present"
            })
    
    if not found_config:
        results["findings"].append({
            "type": "configuration",
            "severity": "medium",
            "issue": "No Railway configuration files found",
            "recommendation": "Create railway.json or Procfile for deployment"
        })
        logger.warning("No Railway configuration files found")
    
    logger.info("✓ Railway scan completed")
    return results


def scan_all(mode: str = "full") -> Dict:
    """Scan all platforms"""
    logger.info(f"Scanning all platforms (mode: {mode})...")
    
    results = {
        "scan_type": "comprehensive",
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "platforms": {}
    }
    
    # Scan each platform
    results["platforms"]["github"] = scan_github(mode)
    results["platforms"]["railway"] = scan_railway(mode)
    
    # Add summary
    total_findings = sum(
        len(platform_data.get("findings", []))
        for platform_data in results["platforms"].values()
    )
    
    results["summary"] = {
        "platforms_scanned": len(results["platforms"]),
        "total_findings": total_findings,
        "status": "completed"
    }
    
    logger.info(f"✓ All platforms scanned: {total_findings} total findings")
    return results


def main():
    parser = argparse.ArgumentParser(description="Platform Scanner")
    parser.add_argument("--platform", required=True, choices=["github", "railway", "all"],
                       help="Platform to scan")
    parser.add_argument("--mode", default="full", choices=["full", "quick", "critical-only"],
                       help="Scan mode")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Perform scan
    if args.platform == "github":
        results = scan_github(args.mode)
    elif args.platform == "railway":
        results = scan_railway(args.mode)
    elif args.platform == "all":
        results = scan_all(args.mode)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
