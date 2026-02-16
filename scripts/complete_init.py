#!/usr/bin/env python3
"""
Complete System Initialization Script
Pre-fills all environments, credentials, and bot configurations
for 24/7 autonomous operation
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}", file=sys.stderr)
        
        return result.returncode == 0, result.stdout + result.stderr
    
    except Exception as e:
        print(f"❌ Exception: {e}", file=sys.stderr)
        return False, str(e)


def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete system initialization - sets up all configs and credentials'
    )
    parser.add_argument(
        '--skip-env',
        action='store_true',
        help='Skip .env file generation'
    )
    parser.add_argument(
        '--skip-bot-config',
        action='store_true',
        help='Skip bot configuration files'
    )
    parser.add_argument(
        '--skip-secrets',
        action='store_true',
        help='Skip secrets template'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite existing files'
    )
    args = parser.parse_args()
    
    # Determine paths
    repo_root = Path(__file__).parent.parent
    scripts_dir = repo_root / 'scripts'
    
    print("=" * 60)
    print("🚀 COMPLETE SYSTEM INITIALIZATION")
    print("=" * 60)
    print(f"📁 Repository: {repo_root}")
    print()
    
    tasks = []
    results = []
    
    # Task 1: Generate .env file
    if not args.skip_env:
        env_args = ['python3', str(scripts_dir / 'setup_env.py')]
        if args.force:
            env_args.append('--force')
        tasks.append(('Environment Setup (.env)', env_args))
    
    # Task 2: Initialize bot configurations
    if not args.skip_bot_config:
        bot_args = ['python3', str(scripts_dir / 'init_bot_configs.py')]
        if args.force:
            bot_args.append('--force')
        tasks.append(('Bot Configuration Files', bot_args))
    
    # Task 3: Verify secrets template
    if not args.skip_secrets:
        secrets_template = repo_root / 'config' / 'secrets.template.yaml'
        if secrets_template.exists():
            print(f"\n✅ Secrets template exists: {secrets_template}")
            results.append(('Secrets Template', True, 'Already exists'))
        else:
            print(f"\n⚠️  Secrets template not found: {secrets_template}")
            results.append(('Secrets Template', False, 'Not found'))
    
    # Run all tasks
    for description, cmd in tasks:
        success, output = run_command(cmd, description)
        results.append((description, success, output))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INITIALIZATION SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for task_name, success, _ in results:
        status = "✅" if success else "❌"
        print(f"{status} {task_name}")
    
    print()
    print(f"Total: {success_count}/{total_count} successful")
    
    # Next steps
    if success_count == total_count:
        print("\n" + "=" * 60)
        print("🎉 ALL INITIALIZATION COMPLETE!")
        print("=" * 60)
        print("\n📋 Next steps:")
        print("1. Review generated .env file and add any missing API keys")
        print("2. Review config/bot-config.json for bot settings")
        print("3. Copy config/credentials.template.json to config/credentials.json")
        print("4. Fill in your API credentials in config/credentials.json")
        print("5. Run 'npm run fia' or 'bun fia' to start the system")
        print("\n⚠️  Remember:")
        print("- Never commit .env or credentials.json to version control")
        print("- Store secrets securely in your deployment platform")
        print("- Use environment variables in CI/CD pipelines")
        return 0
    else:
        print("\n⚠️  Some tasks failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    exit(main())
