"""
CHIMERA ENVIRONMENT & SECRETS PRELOADER
Autonomous system for preloading environment variables, secrets, and credentials
across all platforms (Railway, GitHub, etc.) for optimized deployment strategy.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import secrets as crypto_secrets
from enum import Enum

# Import chimera_base - works for both direct execution and package import
try:
    from chimera_base import ChimeraComponentBase
except ImportError:
    try:
        from backend.chimera_base import ChimeraComponentBase
    except ImportError:
        from .chimera_base import ChimeraComponentBase


logger = logging.getLogger('ChimeraEnvPreloader')


class PlatformType(Enum):
    """Supported deployment platforms"""
    RAILWAY = "railway"
    GITHUB = "github"
    AWS = "aws"
    HEROKU = "heroku"
    VERCEL = "vercel"
    CUSTOM = "custom"


@dataclass
class EnvironmentVariable:
    """Environment variable definition"""
    key: str
    value: str
    platform: PlatformType
    is_secret: bool = False
    required: bool = True
    description: str = ""


@dataclass
class PlatformCredentials:
    """Platform-specific credentials"""
    platform: PlatformType
    api_token: str = ""
    project_id: str = ""
    service_name: str = ""
    api_url: str = ""
    additional_config: Dict[str, Any] = field(default_factory=dict)


class ChimeraEnvPreloader(ChimeraComponentBase):
    """
    Autonomous environment and secrets preloader for Chimera system.
    Manages credentials across platforms for optimized deployment strategy.
    """
    
    def __init__(self, config_dir: str = ".unified-system"):
        """Initialize the environment preloader."""
        super().__init__()
        self.config_dir = Path(config_dir)
        self.secrets_dir = self.config_dir / "secrets"
        self.cache_dir = self.config_dir / "cache"
        
        # Create directories
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        try:
            os.chmod(self.secrets_dir, 0o700)
            os.chmod(self.cache_dir, 0o700)
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {e}")
        
        self.env_cache: Dict[str, EnvironmentVariable] = {}
        self.platform_credentials: Dict[PlatformType, PlatformCredentials] = {}
        self.preloaded = False
        
        self.log_info("Chimera Environment Preloader initialized")
    
    def load_platform_credentials(self, platform: PlatformType) -> Optional[PlatformCredentials]:
        """
        Load credentials for a specific platform from environment variables.
        Credentials are read from the current process environment and cached
        in memory for subsequent use.
        """
        self.log_info(f"Loading credentials for platform: {platform.value}")
        
        creds = PlatformCredentials(platform=platform)
        
        if platform == PlatformType.RAILWAY:
            # Railway credentials
            creds.api_token = os.getenv('RAILWAY_TOKEN', '')
            creds.project_id = os.getenv('RAILWAY_PROJECT_ID', '')
            creds.service_name = os.getenv('RAILWAY_SERVICE_NAME', 'chimera-system')
            creds.api_url = "https://railway.app/api"
            
        elif platform == PlatformType.GITHUB:
            # GitHub credentials
            creds.api_token = os.getenv('GITHUB_TOKEN', os.getenv('GH_PAT', ''))
            creds.project_id = os.getenv('GITHUB_REPOSITORY', '')
            creds.api_url = "https://api.github.com"
            
        elif platform == PlatformType.AWS:
            # AWS credentials
            creds.api_token = os.getenv('AWS_SECRET_ACCESS_KEY', '')
            creds.additional_config = {
                'access_key_id': os.getenv('AWS_ACCESS_KEY_ID', ''),
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                'account_id': os.getenv('AWS_ACCOUNT_ID', '')
            }
            
        # Cache the credentials
        self.platform_credentials[platform] = creds
        
        if creds.api_token:
            self.log_success(f"Credentials loaded for {platform.value}")
            return creds
        else:
            self.log_info(f"No credentials found for {platform.value} (optional)")
            return creds
    
    def define_core_environment_variables(self) -> List[EnvironmentVariable]:
        """Define core environment variables needed by Chimera system."""
        core_vars = [
            # Application settings
            EnvironmentVariable(
                key="NODE_ENV",
                value=os.getenv("NODE_ENV", "production"),
                platform=PlatformType.RAILWAY,
                description="Node.js environment"
            ),
            EnvironmentVariable(
                key="PYTHON_ENV",
                value=os.getenv("PYTHON_ENV", "production"),
                platform=PlatformType.RAILWAY,
                description="Python environment"
            ),
            EnvironmentVariable(
                key="API_PORT",
                value=os.getenv("API_PORT", "8000"),
                platform=PlatformType.RAILWAY,
                description="API server port"
            ),
            EnvironmentVariable(
                key="API_HOST",
                value=os.getenv("API_HOST", "0.0.0.0"),
                platform=PlatformType.RAILWAY,
                description="API server host"
            ),
            
            # Trading settings (safe defaults)
            EnvironmentVariable(
                key="TRADING_MODE",
                value=os.getenv("TRADING_MODE", "paper"),
                platform=PlatformType.RAILWAY,
                description="Trading mode: paper or live"
            ),
            EnvironmentVariable(
                key="RISK_TOLERANCE",
                value=os.getenv("RISK_TOLERANCE", "0.05"),
                platform=PlatformType.RAILWAY,
                description="Risk tolerance level"
            ),
            EnvironmentVariable(
                key="MAX_POSITION_SIZE",
                value=os.getenv("MAX_POSITION_SIZE", "0.1"),
                platform=PlatformType.RAILWAY,
                description="Maximum position size"
            ),
            
            # Security settings (required - no auto-generation in production)
            EnvironmentVariable(
                key="SECRET_KEY",
                value=os.getenv("SECRET_KEY", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=True,
                description="Application secret key (must be provided)"
            ),
            EnvironmentVariable(
                key="JWT_SECRET",
                value=os.getenv("JWT_SECRET", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=True,
                description="JWT token secret (must be provided)"
            ),
            
            # Database (optional)
            EnvironmentVariable(
                key="DATABASE_URL",
                value=os.getenv("DATABASE_URL", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=False,
                description="Database connection URL"
            ),
            EnvironmentVariable(
                key="REDIS_URL",
                value=os.getenv("REDIS_URL", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=False,
                description="Redis connection URL"
            ),
        ]
        
        return core_vars
    
    def define_api_credentials(self) -> List[EnvironmentVariable]:
        """Define API credentials for trading platforms."""
        api_vars = [
            # NDAX API
            EnvironmentVariable(
                key="NDAX_API_KEY",
                value=os.getenv("NDAX_API_KEY", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=False,
                description="NDAX API key"
            ),
            EnvironmentVariable(
                key="NDAX_API_SECRET",
                value=os.getenv("NDAX_API_SECRET", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=False,
                description="NDAX API secret"
            ),
            
            # Generic exchange API
            EnvironmentVariable(
                key="EXCHANGE_API_KEY",
                value=os.getenv("EXCHANGE_API_KEY", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=False,
                description="Exchange API key"
            ),
            EnvironmentVariable(
                key="EXCHANGE_API_SECRET",
                value=os.getenv("EXCHANGE_API_SECRET", ""),
                platform=PlatformType.RAILWAY,
                is_secret=True,
                required=False,
                description="Exchange API secret"
            ),
        ]
        
        return api_vars
    
    def define_wallet_addresses(self) -> List[EnvironmentVariable]:
        """Define wallet addresses for Chimera system."""
        wallet_vars = [
            EnvironmentVariable(
                key="INFLOW_WALLET_ADDR",
                value=os.getenv("INFLOW_WALLET_ADDR", ""),
                platform=PlatformType.RAILWAY,
                required=False,
                description="Inflow wallet address"
            ),
            EnvironmentVariable(
                key="OPERATIONAL_WALLET_ADDR",
                value=os.getenv("OPERATIONAL_WALLET_ADDR", ""),
                platform=PlatformType.RAILWAY,
                required=False,
                description="Operational wallet address"
            ),
            EnvironmentVariable(
                key="COLD_STORAGE_ADDR",
                value=os.getenv("COLD_STORAGE_ADDR", ""),
                platform=PlatformType.RAILWAY,
                required=False,
                description="Cold storage wallet address"
            ),
            EnvironmentVariable(
                key="EMERGENCY_WALLET_ADDR",
                value=os.getenv("EMERGENCY_WALLET_ADDR", ""),
                platform=PlatformType.RAILWAY,
                required=False,
                description="Emergency wallet address"
            ),
        ]
        
        return wallet_vars
    
    def preload_all_environments(self) -> Dict[str, Any]:
        """
        Preload all environment variables, secrets, and credentials.
        This is called during system initialization for optimized deployment.
        """
        self.log_info("Starting environment preload process...")
        
        # Load platform credentials
        self.load_platform_credentials(PlatformType.RAILWAY)
        self.load_platform_credentials(PlatformType.GITHUB)
        self.load_platform_credentials(PlatformType.AWS)
        
        # Collect all environment variables
        all_env_vars = []
        all_env_vars.extend(self.define_core_environment_variables())
        all_env_vars.extend(self.define_api_credentials())
        all_env_vars.extend(self.define_wallet_addresses())
        
        # Cache environment variables
        for env_var in all_env_vars:
            self.env_cache[env_var.key] = env_var
        
        # Prepare summary
        summary = {
            'total_variables': len(all_env_vars),
            'secrets_count': sum(1 for v in all_env_vars if v.is_secret),
            'required_count': sum(1 for v in all_env_vars if v.required),
            'platforms': list(set(v.platform.value for v in all_env_vars)),
            'credentials_loaded': {
                platform.value: bool(creds.api_token)
                for platform, creds in self.platform_credentials.items()
            },
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        # Validate required variables
        missing_required = [
            v.key for v in all_env_vars 
            if v.required and not v.value
        ]
        
        if missing_required:
            summary['missing_required'] = missing_required
            summary['status'] = 'incomplete'
            self.log_error(f"Missing required environment variables: {missing_required}")
        else:
            self.log_success("All required environment variables loaded")
        
        self.preloaded = True
        self.log_success(f"Environment preload complete: {summary['total_variables']} variables loaded")
        
        # Save cache for Railway deployment
        self._save_preload_cache(summary)
        
        return summary
    
    def get_railway_environment(self) -> Dict[str, str]:
        """
        Get environment variables formatted for Railway deployment.
        Only includes non-secret variables (secrets handled separately).
        """
        if not self.preloaded:
            self.preload_all_environments()
        
        railway_env = {}
        for key, env_var in self.env_cache.items():
            if env_var.platform == PlatformType.RAILWAY and not env_var.is_secret:
                railway_env[key] = env_var.value
        
        return railway_env
    
    def get_railway_secrets(self) -> Dict[str, str]:
        """
        Get secret environment variables for Railway deployment.
        These should be set in Railway dashboard or via API.
        """
        if not self.preloaded:
            self.preload_all_environments()
        
        railway_secrets = {}
        for key, env_var in self.env_cache.items():
            if env_var.platform == PlatformType.RAILWAY and env_var.is_secret and env_var.value:
                railway_secrets[key] = env_var.value
        
        return railway_secrets
    
    def _format_env_value_for_dotenv(self, value: Any) -> str:
        """
        Format a value for safe inclusion in a .env file.

        - Normalizes newlines and escapes them as literal '\\n'.
        - Leaves values with only safe characters unquoted.
        - Otherwise, wraps the value in single quotes and escapes existing
          single quotes in a shell-safe way.
        """
        if value is None:
            return ""
        text = str(value)
        # Normalize newlines
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\n", "\\n")
        # Allow simple values without quoting
        if text and all(ch.isalnum() or ch in "._-/:" for ch in text):
            return text
        # Shell-safe single-quoted string: close quote, add escaped quote, reopen quote
        # (e.g., "it's" becomes 'it'"'"'s' to safely escape single quotes within)
        text = text.replace("'", "'\"'\"'")
        return f"'{text}'"

    def export_to_dotenv(self, filepath: str = ".env.railway", include_secrets: bool = False) -> None:
        """
        Export Railway environment variables to a .env file.

        By default, only non-secret variables are exported. To include secrets
        in the exported file, explicitly set include_secrets=True.
        WARNING: The resulting file may contain sensitive data - never commit to git!
        """
        if not self.preloaded:
            self.preload_all_environments()

        env_file_path = Path(filepath)

        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write("# CHIMERA SYSTEM - RAILWAY ENVIRONMENT VARIABLES\n")
            f.write(f"# Auto-generated: {datetime.now().isoformat()}\n")
            f.write("# WARNING: This file may contain sensitive data - never commit to git!\n\n")

            # Group by type
            f.write("# === CORE SETTINGS ===\n")
            for key, env_var in self.env_cache.items():
                # Only export Railway-specific variables
                if env_var.platform != PlatformType.RAILWAY:
                    continue
                if not env_var.is_secret and env_var.value:
                    formatted_value = self._format_env_value_for_dotenv(env_var.value)
                    f.write(f"{key}={formatted_value}\n")

            if include_secrets:
                f.write("\n# === SECRETS (Handle with care) ===\n")
                for key, env_var in self.env_cache.items():
                    # Only export Railway-specific secrets
                    if env_var.platform != PlatformType.RAILWAY:
                        continue
                    if env_var.is_secret and env_var.value:
                        formatted_value = self._format_env_value_for_dotenv(env_var.value)
                        f.write(f"{key}={formatted_value}\n")

        # Set secure permissions
        try:
            os.chmod(env_file_path, 0o600)
        except Exception as e:
            logger.warning(f"Could not set file permissions: {e}")

        self.log_success(f"Environment variables exported to {filepath} (include_secrets={include_secrets})")
    
    def validate_railway_deployment(self) -> Dict[str, Any]:
        """
        Enhanced validation that provides comprehensive deployment insights.
        
        This validation provides informative feedback without blocking deployment.
        It categorizes findings into critical, warning, and info levels to help
        users understand their deployment configuration.
        
        Requires preload_all_environments() to be called first.
        """
        if not self.preloaded:
            return {
                'preloaded': False,
                'deployment_ready': False,
                'critical': ['Environment preload required before validation - call preload_all_environments() first'],
                'warnings': [],
                'info': [],
                'recommendations': [],
                'railway_token': False,
                'required_vars': [],
                'missing_vars': [],
                'configured_vars': [],
                'optional_vars': [],
                'validation_level': 'not_ready'
            }
        
        validation = {
            'preloaded': True,
            'deployment_ready': True,
            'critical': [],
            'warnings': [],
            'info': [],
            'recommendations': [],
            'railway_token': False,
            'required_vars': [],
            'missing_vars': [],
            'configured_vars': [],
            'optional_vars': [],
            'validation_level': 'optimal'
        }
        
        # Check Railway token
        railway_creds = self.platform_credentials.get(PlatformType.RAILWAY)
        if railway_creds and railway_creds.api_token:
            validation['railway_token'] = True
            validation['info'].append("✓ Railway token configured")
        else:
            validation['deployment_ready'] = False
            validation['critical'].append("RAILWAY_TOKEN not configured - Railway deployment unavailable")
            validation['recommendations'].append("Set RAILWAY_TOKEN in GitHub secrets to enable Railway deployment")
        
        # Check required variables with enhanced reporting
        for key, env_var in self.env_cache.items():
            if env_var.required:
                validation['required_vars'].append(key)
                if not env_var.value:
                    validation['missing_vars'].append(key)
                    validation['warnings'].append(f"Required variable {key} is not set")
                    validation['recommendations'].append(f"Set {key} in environment or GitHub secrets")
                    if validation['validation_level'] == 'optimal':
                        validation['validation_level'] = 'acceptable'
                else:
                    validation['configured_vars'].append(key)
        
        # Check optional but recommended variables
        optional_recommended = {
            'DATABASE_URL': 'Database connection for persistent storage',
            'REDIS_URL': 'Redis for caching and session management',
            'NDAX_API_KEY': 'NDAX trading functionality',
            'NDAX_API_SECRET': 'NDAX trading functionality'
        }
        
        missing_optional_count = 0
        for key, description in optional_recommended.items():
            env_var = self.env_cache.get(key)
            if env_var:
                validation['optional_vars'].append(key)
                if not env_var.value:
                    missing_optional_count += 1
                    validation['info'].append(f"Optional: {key} not set ({description})")
                    validation['recommendations'].append(f"Consider setting {key} to enable {description}")
                else:
                    validation['configured_vars'].append(key)
                    validation['info'].append(f"✓ Optional {key} configured")
        
        # Determine final validation level based on configuration completeness
        if validation['critical']:
            # Critical issues prevent deployment
            validation['validation_level'] = 'not_ready'
            validation['deployment_ready'] = False
        elif validation['missing_vars']:
            # Missing required variables - acceptable but not ideal
            validation['validation_level'] = 'acceptable'
        elif missing_optional_count > 0:
            # All required present but some optional missing - good configuration
            validation['validation_level'] = 'good'
        else:
            # Everything configured - optimal
            validation['validation_level'] = 'optimal'
        
        # Enhanced logging with validation level
        if validation['deployment_ready']:
            self.log_success(f"Railway deployment validation: {validation['validation_level'].upper()}")
        else:
            self.log_info(f"Railway deployment validation: {validation['validation_level'].upper()}")
        
        return validation
    
    def _generate_secret_key(self, byte_length: int = 32) -> str:
        """
        Generate a secure random secret key.
        
        Args:
            byte_length: Number of random bytes (hex string will be 2x this length)
        
        Returns:
            Hexadecimal string (2 * byte_length characters)
        """
        return crypto_secrets.token_hex(byte_length)
    
    def _save_preload_cache(self, summary: Dict[str, Any]) -> None:
        """Save preload cache for Railway deployment."""
        cache_file = self.cache_dir / "preload_cache.json"
        
        # Don't save sensitive values in cache
        safe_summary = summary.copy()
        safe_summary['variables'] = [
            {
                'key': key,
                'platform': env_var.platform.value,
                'is_secret': env_var.is_secret,
                'required': env_var.required,
                'has_value': bool(env_var.value)
            }
            for key, env_var in self.env_cache.items()
        ]
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(safe_summary, f, indent=2)
        
        self.log_info(f"Preload cache saved to {cache_file}")


def create_env_preloader(config_dir: str = ".unified-system") -> ChimeraEnvPreloader:
    """Factory function to create environment preloader."""
    return ChimeraEnvPreloader(config_dir=config_dir)


def demo_preloader():
    """Demonstration of environment preloader."""
    print("\n" + "="*80)
    print("CHIMERA ENVIRONMENT PRELOADER - DEMONSTRATION")
    print("="*80 + "\n")
    
    # Create preloader
    preloader = create_env_preloader()
    
    # Preload all environments
    summary = preloader.preload_all_environments()
    
    print("\n📊 Preload Summary:")
    print(f"  Total variables: {summary['total_variables']}")
    print(f"  Secrets: {summary['secrets_count']}")
    print(f"  Required: {summary['required_count']}")
    print(f"  Status: {summary['status']}")
    
    # Get Railway environment
    railway_env = preloader.get_railway_environment()
    print(f"\n🚂 Railway Environment Variables: {len(railway_env)}")
    
    # Get Railway secrets
    railway_secrets = preloader.get_railway_secrets()
    print(f"🔐 Railway Secrets: {len(railway_secrets)}")
    
    # Enhanced Railway validation with detailed reporting
    validation = preloader.validate_railway_deployment()
    print(f"\n📊 Deployment Validation Report")
    print(f"================================")
    print(f"Validation Level: {validation['validation_level'].upper()}")
    print(f"Deployment Ready: {validation['deployment_ready']}")
    print(f"Railway Token: {'✓' if validation['railway_token'] else '✗'}")
    print(f"Configured Variables: {len(validation['configured_vars'])}")
    
    if validation['critical']:
        print(f"\n⚠️  Critical Issues:")
        for issue in validation['critical']:
            print(f"  - {issue}")
    
    if validation['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['info']:
        print(f"\n💡 Information:")
        for info in validation['info']:
            print(f"  - {info}")
    
    if validation['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in validation['recommendations']:
            print(f"  - {rec}")
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_preloader()
