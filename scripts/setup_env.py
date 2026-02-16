#!/usr/bin/env python3
"""
Environment Setup Script
Automatically generates .env file from .env.example with intelligent defaults
"""

import os
import re
import secrets
from pathlib import Path
from typing import Dict, List, Tuple


def generate_secret(length: int = 64) -> str:
    """Generate a secure random secret"""
    return secrets.token_hex(length // 2)


def generate_jwt_secret(length: int = 32) -> str:
    """Generate a JWT secret"""
    return secrets.token_hex(length // 2)


def detect_secret_keys() -> List[str]:
    """Detect keys that likely need secrets"""
    return [
        'SECRET_KEY',
        'JWT_SECRET',
        'SESSION_SECRET',
        'ENCRYPTION_KEY',
        'WEBHOOK_SECRET',
    ]


def detect_api_keys() -> List[str]:
    """Detect keys that need API credentials"""
    return [
        'NDAX_API_KEY',
        'NDAX_API_SECRET',
        'EXCHANGE_API_KEY',
        'EXCHANGE_API_SECRET',
        'STRIPE_API_KEY',
        'STRIPE_SECRET_KEY',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'HUGGINGFACE_API_KEY',
        'RAILWAY_TOKEN',
        'GITHUB_TOKEN',
    ]


def generate_default_value(key: str, commented_value: str = "") -> Tuple[str, bool]:
    """
    Generate a default value for an environment variable.
    Returns (value, is_auto_generated)
    """
    key_upper = key.upper()
    
    # Check if it's a secret that we can auto-generate
    if key_upper in ['SECRET_KEY', 'ENCRYPTION_KEY']:
        return generate_secret(64), True
    
    if key_upper in ['JWT_SECRET', 'SESSION_SECRET', 'WEBHOOK_SECRET']:
        return generate_jwt_secret(32), True
    
    # Database URLs with defaults
    if 'DATABASE_URL' in key_upper and not commented_value:
        return 'sqlite:///./chimera.db', True
    
    if 'REDIS_URL' in key_upper and not commented_value:
        return 'redis://localhost:6379/0', True
    
    # Ports
    if key_upper == 'PORT':
        return '3000', True
    if key_upper == 'PYTHON_PORT':
        return '8000', True
    if key_upper == 'BOT_PORT':
        return '9000', True
    
    # URLs
    if key_upper == 'VITE_API_URL':
        return 'http://localhost:8000', True
    
    # Keep commented value if it exists
    if commented_value and commented_value.strip():
        return commented_value.strip(), False
    
    # Return empty for API keys that require manual configuration
    if key_upper in detect_api_keys():
        return '', False
    
    return '', False


def parse_env_example(example_path: Path) -> Dict[str, str]:
    """Parse .env.example file and generate values"""
    env_vars = {}
    
    if not example_path.exists():
        print(f"❌ File not found: {example_path}")
        return env_vars
    
    print(f"📖 Reading {example_path}")
    
    with open(example_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=value or # KEY=value
            match = re.match(r'^#?\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
            if match:
                key = match.group(1)
                commented_value = match.group(2)
                
                value, is_auto = generate_default_value(key, commented_value)
                env_vars[key] = value
                
                if is_auto and value:
                    print(f"  ✅ Auto-generated: {key}")
                elif value:
                    print(f"  ℹ️  Using default: {key}={value}")
                else:
                    print(f"  ⚠️  Needs manual config: {key}")
    
    return env_vars


def write_env_file(env_path: Path, env_vars: Dict[str, str], force: bool = False):
    """Write .env file with generated values"""
    if env_path.exists() and not force:
        print(f"\n⚠️  {env_path} already exists. Use --force to overwrite.")
        return False
    
    print(f"\n📝 Writing {env_path}")
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# NDAX Quantum Engine - Environment Configuration\n")
        f.write("# Auto-generated from .env.example\n")
        f.write("# DO NOT COMMIT THIS FILE TO VERSION CONTROL\n\n")
        
        # Group by category
        categories = {
            'Node.js Configuration': ['NODE_ENV', 'PORT'],
            'Python Backend Configuration': ['PYTHON_PORT'],
            'Trading Configuration': ['TRADING_MODE', 'AUTO_START', 'MAX_TRADES', 'RISK_LEVEL'],
            '24/7 AUTONOMOUS OPERATION SETTINGS': ['CONTINUOUS_MODE', 'AUTO_RECONNECT', 'RECONNECT_INTERVAL'],
            'Bot Configuration': ['BOT_PORT'],
            'Frontend Configuration': ['VITE_API_URL'],
            'Security Configuration': ['JWT_SECRET', 'SECRET_KEY', 'SESSION_SECRET'],
            'Database Configuration': ['DATABASE_URL', 'REDIS_URL'],
        }
        
        written_keys = set()
        
        for category, keys in categories.items():
            matching_keys = [k for k in keys if k in env_vars]
            if matching_keys:
                f.write(f"# {category}\n")
                for key in matching_keys:
                    value = env_vars[key]
                    f.write(f"{key}={value}\n")
                    written_keys.add(key)
                f.write("\n")
        
        # Write remaining keys
        remaining = set(env_vars.keys()) - written_keys
        if remaining:
            f.write("# Additional Configuration\n")
            for key in sorted(remaining):
                value = env_vars[key]
                f.write(f"{key}={value}\n")
    
    # Set secure permissions
    try:
        os.chmod(env_path, 0o600)
        print(f"✅ Set secure permissions (600) on {env_path}")
    except Exception as e:
        print(f"⚠️  Could not set permissions: {e}")
    
    return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate .env file from .env.example')
    parser.add_argument('--force', action='store_true', help='Overwrite existing .env file')
    parser.add_argument('--output', default='.env', help='Output file path (default: .env)')
    parser.add_argument('--example', default='.env.example', help='Example file path (default: .env.example)')
    args = parser.parse_args()
    
    # Determine paths
    repo_root = Path(__file__).parent.parent
    example_path = repo_root / args.example
    env_path = repo_root / args.output
    
    print("🚀 Environment Setup Script")
    print(f"📁 Repository: {repo_root}")
    print()
    
    # Parse and generate
    env_vars = parse_env_example(example_path)
    
    if not env_vars:
        print("\n❌ No environment variables found")
        return 1
    
    # Write .env file
    success = write_env_file(env_path, env_vars, force=args.force)
    
    if success:
        print(f"\n✅ Environment file created: {env_path}")
        print("\n📋 Next steps:")
        print("1. Review the generated .env file")
        print("2. Add your API keys and secrets where needed")
        print("3. Never commit .env to version control")
        print("\n⚠️  Variables needing manual configuration:")
        
        api_keys_found = [k for k in env_vars.keys() if k in detect_api_keys()]
        if api_keys_found:
            for key in sorted(api_keys_found):
                print(f"   - {key}")
        else:
            print("   (None - all set!)")
        
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
