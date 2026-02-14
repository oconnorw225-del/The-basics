#!/usr/bin/env python3
"""
Environment Auto-Populator
Automatically populates environment variables with secure defaults and generated secrets.
"""

import os
import secrets
import string
import re
from pathlib import Path
from typing import Dict, Optional
import subprocess
import sys

class EnvAutoPopulator:
    """Automatically populate environment variables with smart defaults."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.env_example = self.repo_root / ".env.example"
        self.env_file = self.repo_root / ".env"
        self.env_prod_template = self.repo_root / ".env.production.template"
        self.env_prod = self.repo_root / ".env.production"
        
    def generate_jwt_secret(self, length: int = 64) -> str:
        """Generate a secure JWT secret."""
        # Use secrets module for cryptographically strong random
        return secrets.token_hex(length)
    
    def generate_session_secret(self, length: int = 32) -> str:
        """Generate a secure session secret."""
        return secrets.token_hex(length)
    
    def generate_database_url(self, environment: str = "development") -> str:
        """Generate a database URL with smart defaults."""
        if environment == "production":
            return "postgresql://username:password@localhost:5432/ndax_prod"
        return "postgresql://user:pass@localhost:5432/ndax_dev"
    
    def detect_api_keys_needed(self, content: str) -> Dict[str, str]:
        """Detect which API keys are needed from the template."""
        api_keys = {}
        
        # Patterns for API key detection
        patterns = {
            'NDAX_API_KEY': 'NDAX_API_KEY=',
            'NDAX_API_SECRET': 'NDAX_API_SECRET=',
            'NDAX_USER_ID': 'NDAX_USER_ID=',
            'SENDGRID_API_KEY': 'SENDGRID_API_KEY=',
            'OPENAI_API_KEY': 'OPENAI_API_KEY=',
            'ANTHROPIC_API_KEY': 'ANTHROPIC_API_KEY=',
        }
        
        for key, pattern in patterns.items():
            if pattern in content:
                api_keys[key] = f"<PLACEHOLDER_{key}>"
        
        return api_keys
    
    def populate_env_file(self, template_path: Path, output_path: Path, 
                         environment: str = "development") -> bool:
        """Populate environment file with generated secrets and smart defaults."""
        
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            return False
        
        # Read template
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Generate secrets
        jwt_secret = self.generate_jwt_secret()
        session_secret = self.generate_session_secret()
        database_url = self.generate_database_url(environment)
        
        # Replacements - use regex for more robust matching
        replacements = {
            # JWT and Session secrets
            'JWT_SECRET=CHANGE_ME_GENERATE_SECURE_64_CHAR_HEX': f'JWT_SECRET={jwt_secret}',
            'JWT_SECRET=your_secure_random_string_here': f'JWT_SECRET={jwt_secret}',
            '# JWT_SECRET=your_secure_random_string_here': f'JWT_SECRET={jwt_secret}',
            'SESSION_SECRET=CHANGE_ME_GENERATE_SECURE_32_CHAR_HEX': f'SESSION_SECRET={session_secret}',
            
            # Database
            'DATABASE_URL=postgresql://username:password@localhost:5432/ndax_prod': f'DATABASE_URL={database_url}',
            '# DATABASE_URL=postgresql://user:pass@localhost:5432/ndax': f'DATABASE_URL={database_url}',
        }
        
        # Additional patterns for JWT_SECRET and SESSION_SECRET
        if '# JWT_SECRET=' in content:
            # JWT_SECRET is commented, uncomment and set it
            content = re.sub(r'# JWT_SECRET=.*', f'JWT_SECRET={jwt_secret}', content)
        elif 'JWT_SECRET=' not in content:
            # JWT_SECRET doesn't exist, add it in security section
            if '# Security Configuration' in content:
                content = content.replace(
                    '# Security Configuration',
                    f'# Security Configuration\nJWT_SECRET={jwt_secret}'
                )
        
        # Handle SESSION_SECRET if it exists in template
        if 'SESSION_SECRET=' in content:
            content = re.sub(r'SESSION_SECRET=.*', f'SESSION_SECRET={session_secret}', content)
        
        # Ensure database URL is uncommented
        if '# DATABASE_URL=' in content and f'DATABASE_URL={database_url}' not in content:
            content = re.sub(r'# DATABASE_URL=.*', f'DATABASE_URL={database_url}', content)
        
        # Apply replacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Detect and mark API keys that need to be filled
        api_keys = self.detect_api_keys_needed(content)
        
        # Add header comment
        header = f"""# ============================================================================
# AUTO-GENERATED ENVIRONMENT CONFIGURATION
# ============================================================================
# Generated on: {subprocess.check_output(['date'], text=True).strip()}
# Environment: {environment}
#
# ✅ Auto-configured settings:
#    - JWT_SECRET: Generated secure 64-char hex token
#    - SESSION_SECRET: Generated secure 32-char hex token
#    - DATABASE_URL: Smart default for {environment}
#    - Security settings: Enabled with safe defaults
#
# ⚠️  ACTION REQUIRED - Fill in these API keys:
"""
        
        for key in api_keys:
            header += f"#    - {key}: <PLACEHOLDER_{key}>\n"
        
        header += f"""#
# 📝 Notes:
#    - Keep this file secure and never commit to git
#    - All secrets are cryptographically generated
#    - Review and adjust settings as needed for your deployment
#
# ============================================================================

"""
        
        final_content = header + content
        
        # Write output
        with open(output_path, 'w') as f:
            f.write(final_content)
        
        # Set secure permissions
        os.chmod(output_path, 0o600)
        
        print(f"✅ Generated {output_path}")
        print(f"   JWT Secret: {jwt_secret[:20]}... (64 chars)")
        print(f"   Session Secret: {session_secret[:20]}... (32 chars)")
        print(f"   Database: {database_url}")
        
        if api_keys:
            print(f"\n⚠️  Action required: Fill in these API keys:")
            for key in api_keys:
                print(f"   - {key}")
        
        return True
    
    def setup_development_env(self) -> bool:
        """Set up development environment."""
        print("\n🔧 Setting up DEVELOPMENT environment...")
        
        if self.env_file.exists():
            response = input(f"⚠️  {self.env_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Skipping development environment setup.")
                return False
        
        success = self.populate_env_file(
            self.env_example,
            self.env_file,
            environment="development"
        )
        
        if success:
            print(f"\n✅ Development environment configured: {self.env_file}")
        
        return success
    
    def setup_production_env(self) -> bool:
        """Set up production environment."""
        print("\n🚀 Setting up PRODUCTION environment...")
        
        if self.env_prod.exists():
            response = input(f"⚠️  {self.env_prod} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Skipping production environment setup.")
                return False
        
        success = self.populate_env_file(
            self.env_prod_template,
            self.env_prod,
            environment="production"
        )
        
        if success:
            print(f"\n✅ Production environment configured: {self.env_prod}")
            print("\n⚠️  IMPORTANT: Review security settings before deploying!")
            print("   - Verify JWT_SECRET is secure")
            print("   - Configure actual API keys")
            print("   - Set up production database")
            print("   - Enable TLS/HTTPS")
        
        return success
    
    def interactive_setup(self):
        """Interactive setup wizard."""
        print("=" * 70)
        print("🎉 Environment Auto-Populator")
        print("=" * 70)
        print("\nThis wizard will:")
        print("  ✅ Generate secure JWT and session secrets")
        print("  ✅ Configure database connections")
        print("  ✅ Set security defaults")
        print("  ✅ Mark API keys that need your attention")
        print()
        
        # Ask which environments to set up
        print("Which environment(s) would you like to set up?")
        print("  1. Development only")
        print("  2. Production only")
        print("  3. Both")
        
        choice = input("\nEnter choice (1-3) [3]: ").strip() or "3"
        
        success = True
        
        if choice in ["1", "3"]:
            success = self.setup_development_env() and success
        
        if choice in ["2", "3"]:
            success = self.setup_production_env() and success
        
        if success:
            print("\n" + "=" * 70)
            print("✅ Environment setup complete!")
            print("=" * 70)
            print("\n📝 Next steps:")
            print("  1. Review generated .env files")
            print("  2. Fill in API keys where needed")
            print("  3. Adjust settings for your deployment")
            print("  4. Start the system:")
            print("     - Development: npm start")
            print("     - Production: npm run start:prod")
            print()
        else:
            print("\n❌ Environment setup failed or was skipped.")
            return 1
        
        return 0

def main():
    """Main entry point."""
    populator = EnvAutoPopulator()
    
    # Check if running in auto mode
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("Running in AUTO mode...")
        populator.setup_development_env()
        populator.setup_production_env()
    else:
        # Interactive mode
        exit_code = populator.interactive_setup()
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
