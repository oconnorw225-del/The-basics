"""Integration tests for the complete system."""
import pytest
import json
from pathlib import Path

class TestSystemIntegration:
    """Test system-wide integration."""
    
    def test_all_configs_loadable(self):
        """Test that all configuration files can be loaded."""
        config_dir = Path('config')
        assert config_dir.exists(), "Config directory should exist"
        
        config_files = list(config_dir.glob('*.json'))
        assert len(config_files) > 0, "Should have configuration files"
        
        for config_file in config_files:
            with open(config_file) as f:
                config = json.load(f)
                assert isinstance(config, dict), f"{config_file.name} should be a dict"
    
    def test_kill_switch_default_disabled(self):
        """Test that kill switch defaults to disabled."""
        with open('config/kill-switch.json') as f:
            ks = json.load(f)
        
        assert ks['enabled'] == False, "Kill switch should be disabled by default"
        assert ks['auto_trigger'] == False, "Auto-trigger should be disabled"
    
    def test_bot_limits_configured(self):
        """Test that bot limits are properly configured."""
        with open('config/bot-limits.json') as f:
            limits = json.load(f)
        
        required_bots = ['ndax_bot', 'quantum_bot', 'shadowforge_bot']
        for bot in required_bots:
            assert bot in limits, f"Should have limits for {bot}"
            assert 'max_daily_loss' in limits[bot]
            assert 'max_position_size' in limits[bot]
    
    def test_api_endpoints_configured(self):
        """Test that API endpoints are configured."""
        with open('config/api-endpoints.json') as f:
            endpoints = json.load(f)
        
        required_endpoints = ['ndax_bot', 'quantum_bot', 'shadowforge_bot']
        for endpoint in required_endpoints:
            assert endpoint in endpoints, f"Should have endpoint for {endpoint}"

    def test_no_config_conflicts(self):
        """Test that there are no conflicting port configurations."""
        with open('config/api-endpoints.json') as f:
            endpoints = json.load(f)
        
        ports = []
        for bot_name, bot_config in endpoints.items():
            if isinstance(bot_config, dict) and 'base_url' in bot_config:
                url = bot_config['base_url']
                if ':' in url:
                    port = url.split(':')[-1].split('/')[0]
                    if port.isdigit():
                        assert port not in ports, f"Port {port} is duplicated"
                        ports.append(port)
    
    def test_package_json_valid(self):
        """Test that package.json is valid and has required scripts."""
        with open('package.json') as f:
            package = json.load(f)
        
        assert 'scripts' in package
        assert 'test' in package['scripts']
        assert package['scripts']['test'] != 'echo "No tests configured" && exit 0'
        assert 'test:python' in package['scripts']
        assert 'test:all' in package['scripts']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
