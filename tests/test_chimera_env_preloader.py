"""
Unit tests for Chimera Environment Preloader.
Tests cover preload_all_environments(), validate_railway_deployment(),
and export_to_dotenv() with various scenarios.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add backend to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from chimera_env_preloader import (
    ChimeraEnvPreloader,
    create_env_preloader,
    PlatformType,
    EnvironmentVariable
)


class TestChimeraEnvPreloader:
    """Test suite for ChimeraEnvPreloader"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def preloader(self, temp_dir):
        """Create a preloader instance for testing"""
        return ChimeraEnvPreloader(config_dir=temp_dir)

    def test_preloader_initialization(self, preloader, temp_dir):
        """Test that preloader initializes correctly"""
        assert preloader.config_dir == Path(temp_dir)
        assert preloader.secrets_dir.exists()
        assert preloader.cache_dir.exists()
        assert not preloader.preloaded
        assert len(preloader.env_cache) == 0

    def test_factory_function(self, temp_dir):
        """Test the create_env_preloader factory function"""
        preloader = create_env_preloader(config_dir=temp_dir)
        assert isinstance(preloader, ChimeraEnvPreloader)
        assert preloader.config_dir == Path(temp_dir)

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-railway-token',
        'RAILWAY_PROJECT_ID': 'test-project-id',
        'NODE_ENV': 'test',
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET': 'test-jwt-secret'
    }, clear=True)
    def test_preload_all_environments_with_secrets(self, preloader):
        """Test preload_all_environments() with required secrets set"""
        summary = preloader.preload_all_environments()
        
        assert summary['status'] == 'success'
        assert summary['total_variables'] > 0
        assert summary['secrets_count'] > 0
        assert PlatformType.RAILWAY.value in summary['platforms']
        assert preloader.preloaded
        
        # Check that required variables are loaded
        assert 'SECRET_KEY' in preloader.env_cache
        assert 'JWT_SECRET' in preloader.env_cache
        assert preloader.env_cache['SECRET_KEY'].value == 'test-secret-key'
        assert preloader.env_cache['JWT_SECRET'].value == 'test-jwt-secret'

    @patch.dict(os.environ, {
        'NODE_ENV': 'test',
        'RAILWAY_TOKEN': 'test-token'
    }, clear=True)
    def test_preload_all_environments_missing_secrets(self, preloader):
        """Test preload_all_environments() with missing required secrets"""
        summary = preloader.preload_all_environments()
        
        # Should be incomplete due to missing SECRET_KEY and JWT_SECRET
        assert summary['status'] == 'incomplete'
        assert 'missing_required' in summary
        assert 'SECRET_KEY' in summary['missing_required']
        assert 'JWT_SECRET' in summary['missing_required']

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt'
    }, clear=True)
    def test_validate_railway_deployment_success(self, preloader):
        """Test validate_railway_deployment() when all required vars are present"""
        preloader.preload_all_environments()
        validation = preloader.validate_railway_deployment()
        
        assert validation['deployment_ready'] is True
        assert validation['railway_token'] is True
        assert len(validation['critical']) == 0
        assert len(validation['missing_vars']) == 0
        assert validation['validation_level'] in ['optimal', 'good', 'acceptable']

    @patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt'
    }, clear=True)
    def test_validate_railway_deployment_missing_token(self, preloader):
        """Test validate_railway_deployment() when Railway token is missing"""
        preloader.preload_all_environments()
        validation = preloader.validate_railway_deployment()
        
        assert validation['deployment_ready'] is False
        assert validation['railway_token'] is False
        assert any('RAILWAY_TOKEN' in msg for msg in validation['critical'])
        assert validation['validation_level'] == 'not_ready'

    def test_validate_railway_deployment_before_preload(self, preloader):
        """Test that validate_railway_deployment() provides info if called before preload"""
        validation = preloader.validate_railway_deployment()
        
        assert validation['preloaded'] is False
        assert validation['deployment_ready'] is False
        assert any('preload required' in msg.lower() for msg in validation['critical'])
        assert validation['validation_level'] == 'not_ready'

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt',
        'NODE_ENV': 'production',
        'API_PORT': '8000'
    }, clear=True)
    def test_export_to_dotenv_no_secrets(self, preloader, temp_dir):
        """Test export_to_dotenv() without including secrets"""
        preloader.preload_all_environments()
        
        dotenv_path = Path(temp_dir) / ".env.test"
        preloader.export_to_dotenv(str(dotenv_path), include_secrets=False)
        
        assert dotenv_path.exists()
        
        # Read the file and verify contents
        content = dotenv_path.read_text()
        assert 'NODE_ENV=' in content
        assert 'API_PORT=' in content
        # Secrets should not be included
        assert 'SECRET_KEY=' not in content
        assert 'JWT_SECRET=' not in content

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt',
        'NODE_ENV': 'production'
    }, clear=True)
    def test_export_to_dotenv_with_secrets(self, preloader, temp_dir):
        """Test export_to_dotenv() including secrets"""
        preloader.preload_all_environments()
        
        dotenv_path = Path(temp_dir) / ".env.test"
        preloader.export_to_dotenv(str(dotenv_path), include_secrets=True)
        
        assert dotenv_path.exists()
        
        # Read the file and verify contents
        content = dotenv_path.read_text()
        assert 'NODE_ENV=' in content
        # Secrets should be included
        assert 'SECRET_KEY=' in content
        assert 'JWT_SECRET=' in content

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt',
        'TEST_VAR': "value with\nnewlines and 'quotes'"
    }, clear=True)
    def test_format_env_value_for_dotenv(self, preloader):
        """Test _format_env_value_for_dotenv() handles special characters"""
        # Simple alphanumeric value
        assert preloader._format_env_value_for_dotenv("simple123") == "simple123"
        
        # Value with special characters needs quoting
        formatted = preloader._format_env_value_for_dotenv("value with spaces")
        assert formatted.startswith("'")
        assert formatted.endswith("'")
        
        # Value with single quotes
        formatted = preloader._format_env_value_for_dotenv("value's test")
        assert '"' in formatted  # Should escape the single quote
        
        # None value
        assert preloader._format_env_value_for_dotenv(None) == ""

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-railway-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt'
    }, clear=True)
    def test_get_railway_environment(self, preloader):
        """Test get_railway_environment() returns only non-secret Railway vars"""
        preloader.preload_all_environments()
        railway_env = preloader.get_railway_environment()
        
        # Should include non-secret Railway variables
        assert 'NODE_ENV' in railway_env
        assert 'API_PORT' in railway_env
        
        # Should not include secrets
        assert 'SECRET_KEY' not in railway_env
        assert 'JWT_SECRET' not in railway_env

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-railway-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt'
    }, clear=True)
    def test_get_railway_secrets(self, preloader):
        """Test get_railway_secrets() returns only Railway secrets"""
        preloader.preload_all_environments()
        railway_secrets = preloader.get_railway_secrets()
        
        # Should include Railway secrets
        assert 'SECRET_KEY' in railway_secrets
        assert 'JWT_SECRET' in railway_secrets
        assert railway_secrets['SECRET_KEY'] == 'test-secret'
        
        # Should not include non-secrets
        assert 'NODE_ENV' not in railway_secrets

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'GITHUB_TOKEN': 'test-github-token',
        'AWS_ACCESS_KEY_ID': 'test-aws-key'
    }, clear=True)
    def test_load_platform_credentials(self, preloader):
        """Test loading credentials for different platforms"""
        # Load Railway credentials
        railway_creds = preloader.load_platform_credentials(PlatformType.RAILWAY)
        assert railway_creds.api_token == 'test-token'
        assert railway_creds.platform == PlatformType.RAILWAY
        
        # Load GitHub credentials
        github_creds = preloader.load_platform_credentials(PlatformType.GITHUB)
        assert github_creds.api_token == 'test-github-token'
        assert github_creds.platform == PlatformType.GITHUB
        
        # Load AWS credentials
        aws_creds = preloader.load_platform_credentials(PlatformType.AWS)
        assert 'access_key_id' in aws_creds.additional_config

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt'
    }, clear=True)
    def test_preload_cache_saved(self, preloader, temp_dir):
        """Test that preload cache is saved to disk"""
        preloader.preload_all_environments()
        
        cache_file = Path(temp_dir) / "cache" / "preload_cache.json"
        assert cache_file.exists()
        
        # Verify cache doesn't contain actual secret values
        import json
        with open(cache_file) as f:
            cache_data = json.load(f)
        
        assert 'total_variables' in cache_data
        assert 'variables' in cache_data
        
        # Verify secrets are marked but values not saved
        for var in cache_data['variables']:
            assert 'key' in var
            assert 'is_secret' in var
            assert 'has_value' in var
            # Should not contain actual value
            assert 'value' not in var

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt',
        'DATABASE_URL': 'postgresql://test'
    }, clear=True)
    def test_optional_variables(self, preloader):
        """Test that optional variables are handled correctly"""
        summary = preloader.preload_all_environments()
        
        # Should succeed even if optional vars like NDAX_API_KEY are missing
        assert summary['status'] == 'success'
        
        # Optional DATABASE_URL should be loaded if present
        assert 'DATABASE_URL' in preloader.env_cache
        assert preloader.env_cache['DATABASE_URL'].value == 'postgresql://test'
        assert not preloader.env_cache['DATABASE_URL'].required

    def test_environment_variable_dataclass(self):
        """Test EnvironmentVariable dataclass"""
        env_var = EnvironmentVariable(
            key="TEST_KEY",
            value="test_value",
            platform=PlatformType.RAILWAY,
            is_secret=True,
            required=False,
            description="Test variable"
        )
        
        assert env_var.key == "TEST_KEY"
        assert env_var.value == "test_value"
        assert env_var.platform == PlatformType.RAILWAY
        assert env_var.is_secret is True
        assert env_var.required is False

    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt',
        'DATABASE_URL': 'postgresql://test',
        'REDIS_URL': 'redis://test'
    }, clear=True)
    def test_enhanced_validation_features(self, preloader):
        """Test that enhanced validation provides detailed insights"""
        preloader.preload_all_environments()
        validation = preloader.validate_railway_deployment()
        
        # Should have all the new validation structure
        assert 'validation_level' in validation
        assert 'deployment_ready' in validation
        assert 'critical' in validation
        assert 'warnings' in validation
        assert 'info' in validation
        assert 'recommendations' in validation
        assert 'configured_vars' in validation
        assert 'optional_vars' in validation
        
        # Should be ready for deployment with all vars configured
        assert validation['deployment_ready'] is True
        assert validation['validation_level'] in ['optimal', 'good']
        
        # Should have info about configured optional vars
        assert len(validation['configured_vars']) > 0
        
    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret'
        # Missing JWT_SECRET
    }, clear=True)
    def test_validation_with_missing_required(self, preloader):
        """Test validation with missing required variables"""
        preloader.preload_all_environments()
        validation = preloader.validate_railway_deployment()
        
        # Should have warnings about missing required vars
        assert len(validation['warnings']) > 0
        assert len(validation['missing_vars']) > 0
        assert 'JWT_SECRET' in validation['missing_vars']
        
        # Should provide recommendations
        assert len(validation['recommendations']) > 0
        
        # Validation level should reflect missing vars
        assert validation['validation_level'] == 'acceptable'
        
        # Should still be deployment ready (warns but doesn't block)
        assert validation['deployment_ready'] is True
    
    @patch.dict(os.environ, {
        'RAILWAY_TOKEN': 'test-token',
        'SECRET_KEY': 'test-secret',
        'JWT_SECRET': 'test-jwt'
        # No optional vars like DATABASE_URL, REDIS_URL
    }, clear=True)
    def test_validation_with_missing_optional(self, preloader):
        """Test validation with missing optional variables"""
        preloader.preload_all_environments()
        validation = preloader.validate_railway_deployment()
        
        # Should still be ready for deployment
        assert validation['deployment_ready'] is True
        
        # Should have info about missing optional vars
        assert len(validation['info']) > 0
        
        # Should have recommendations for optional features
        assert len(validation['recommendations']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
