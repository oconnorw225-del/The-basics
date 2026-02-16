#!/usr/bin/env python3
"""
Bot Configuration Initializer
Pre-fills all bot configurations with intelligent defaults for 24/7 autonomous operation
"""

import json
from pathlib import Path
from typing import Dict, Any


def create_bot_config() -> Dict[str, Any]:
    """Create comprehensive bot configuration"""
    return {
        "bot": {
            "name": "NDAX Quantum Bot",
            "version": "2.0.0",
            "mode": "autonomous_24_7",
            "auto_start": True,
            "continuous_mode": True
        },
        "trading": {
            "enabled": True,
            "mode": "paper",
            "auto_start": True,
            "max_trades": 5,
            "risk_level": "low",
            "exchanges": ["NDAX"],
            "pairs": ["BTC/CAD", "ETH/CAD", "USDT/CAD"],
            "strategy": "quantum_analysis"
        },
        "freelance": {
            "enabled": True,
            "auto_start": True,
            "auto_bid": True,
            "auto_execute": False,
            "platforms": {
                "fiverr": {"enabled": True, "max_projects": 3},
                "freelancer": {"enabled": True, "max_projects": 3},
                "toptal": {"enabled": True, "max_projects": 2},
                "guru": {"enabled": True, "max_projects": 2},
                "peopleperhour": {"enabled": True, "max_projects": 2}
            },
            "skills": [
                "Python", "JavaScript", "Node.js", "React",
                "Machine Learning", "Trading Bots", "API Integration"
            ],
            "min_rate": 50,
            "max_rate": 150,
            "currency": "USD"
        },
        "ai": {
            "enabled": True,
            "auto_start": True,
            "max_concurrent_tasks": 5,
            "task_queue_size": 100,
            "models": {
                "analysis": "gpt-4",
                "trading": "custom_quantum",
                "freelance": "gpt-4"
            },
            "features": {
                "market_analysis": True,
                "sentiment_analysis": True,
                "task_automation": True,
                "code_generation": True
            }
        },
        "monitoring": {
            "health_check_interval": 30000,
            "freeze_detection": {
                "soft_threshold": 60,
                "hard_threshold": 300
            },
            "metrics": {
                "enabled": True,
                "interval": 60000
            },
            "alerts": {
                "enabled": True,
                "channels": ["log", "webhook"]
            }
        },
        "recovery": {
            "auto_reconnect": True,
            "reconnect_interval": 5000,
            "max_retries": 10,
            "retry_backoff_base": 2.0,
            "circuit_breaker": {
                "threshold": 5,
                "timeout": 300
            }
        },
        "security": {
            "rate_limiting": {
                "enabled": True,
                "window": 15,
                "max_requests": 100
            },
            "authentication": {
                "required": True,
                "type": "jwt"
            },
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256-GCM"
            }
        },
        "features": {
            "trading": {
                "enabled": False,
                "critical": False,
                "autoStart": True,
                "dependencies": []
            },
            "freelance": {
                "enabled": True,
                "critical": True,
                "autoStart": True,
                "dependencies": ["ai"]
            },
            "ai": {
                "enabled": True,
                "critical": True,
                "autoStart": True,
                "dependencies": []
            },
            "payments": {
                "enabled": True,
                "critical": False,
                "autoStart": True,
                "dependencies": []
            },
            "database": {
                "enabled": True,
                "critical": True,
                "autoStart": True,
                "dependencies": []
            },
            "dashboard": {
                "enabled": True,
                "critical": False,
                "autoStart": True,
                "dependencies": ["database"]
            }
        }
    }


def create_credentials_template() -> Dict[str, Any]:
    """Create credentials template configuration"""
    return {
        "exchanges": {
            "ndax": {
                "api_key": "",
                "api_secret": "",
                "user_id": "",
                "enabled": False,
                "note": "Get from https://ndax.io/"
            },
            "binance": {
                "api_key": "",
                "api_secret": "",
                "enabled": False,
                "note": "Optional: Binance exchange"
            }
        },
        "freelance_platforms": {
            "fiverr": {
                "username": "",
                "api_key": "",
                "enabled": False,
                "note": "Fiverr account credentials"
            },
            "freelancer": {
                "username": "",
                "api_key": "",
                "enabled": False,
                "note": "Freelancer.com credentials"
            },
            "toptal": {
                "username": "",
                "api_key": "",
                "enabled": False,
                "note": "Toptal credentials"
            }
        },
        "payment_processors": {
            "stripe": {
                "api_key": "",
                "secret_key": "",
                "enabled": False,
                "note": "Stripe payment processing"
            },
            "paypal": {
                "client_id": "",
                "secret": "",
                "enabled": False,
                "note": "PayPal payment processing"
            }
        },
        "ai_services": {
            "openai": {
                "api_key": "",
                "enabled": False,
                "note": "OpenAI API for AI features"
            },
            "huggingface": {
                "api_key": "",
                "enabled": False,
                "note": "HuggingFace for ML models"
            }
        },
        "notifications": {
            "discord": {
                "webhook_url": "",
                "enabled": False
            },
            "telegram": {
                "bot_token": "",
                "chat_id": "",
                "enabled": False
            },
            "email": {
                "smtp_host": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "enabled": False
            }
        },
        "database": {
            "postgresql": {
                "url": "",
                "enabled": False,
                "note": "PostgreSQL database URL"
            },
            "redis": {
                "url": "",
                "enabled": False,
                "note": "Redis cache URL"
            }
        }
    }


def create_automation_config() -> Dict[str, Any]:
    """Create automation configuration"""
    return {
        "enabled": True,
        "mode": "autonomous_24_7",
        "schedules": {
            "trading": {
                "enabled": True,
                "continuous": True,
                "interval": 60
            },
            "freelance": {
                "enabled": True,
                "scan_interval": 300,
                "bid_interval": 600
            },
            "health_check": {
                "enabled": True,
                "interval": 30
            },
            "reporting": {
                "enabled": True,
                "interval": 3600
            }
        },
        "rules": {
            "auto_restart_on_error": True,
            "max_restart_attempts": 10,
            "notify_on_critical": True,
            "auto_update_enabled": False
        }
    }


def save_config(config: Dict[str, Any], filepath: Path, create_backup: bool = True):
    """Save configuration to file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing file
    if filepath.exists() and create_backup:
        backup_path = filepath.with_suffix(filepath.suffix + '.backup')
        print(f"  📦 Creating backup: {backup_path}")
        backup_path.write_text(filepath.read_text())
    
    # Write new config
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"  ✅ Created: {filepath}")


def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize bot configurations')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--backup', action='store_true', default=True, help='Create backups of existing files')
    args = parser.parse_args()
    
    # Determine paths
    repo_root = Path(__file__).parent.parent
    config_dir = repo_root / 'config'
    
    print("🤖 Bot Configuration Initializer")
    print(f"📁 Config directory: {config_dir}")
    print()
    
    # Define configurations to create
    configs = {
        'bot-config.json': create_bot_config(),
        'credentials.template.json': create_credentials_template(),
        'automation-settings.json': create_automation_config(),
    }
    
    created_count = 0
    skipped_count = 0
    
    for filename, config_data in configs.items():
        filepath = config_dir / filename
        
        if filepath.exists() and not args.force:
            print(f"  ⏭️  Skipped (exists): {filepath}")
            skipped_count += 1
            continue
        
        save_config(config_data, filepath, create_backup=args.backup)
        created_count += 1
    
    print()
    print(f"📊 Summary:")
    print(f"  ✅ Created: {created_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    
    if created_count > 0:
        print()
        print("📋 Next steps:")
        print("1. Review the generated configuration files")
        print("2. Copy credentials.template.json to credentials.json")
        print("3. Fill in your API keys and credentials")
        print("4. Never commit credentials.json to version control")
    
    return 0


if __name__ == '__main__':
    exit(main())
