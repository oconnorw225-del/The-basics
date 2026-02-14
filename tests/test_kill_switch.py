#!/usr/bin/env python3
"""
Test script for kill switch functionality
Tests both bot.js and bot-coordinator.py kill switch implementations
"""

import subprocess
import time
import requests
import sys

def test_bot_kill_switch():
    """Test bot.js kill switch endpoints"""
    print("=" * 60)
    print("Testing bot.js kill switch functionality")
    print("=" * 60)
    
    # Start bot in background
    print("\n1. Starting bot.js...")
    bot_process = subprocess.Popen(
        ['node', 'bot.js'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={'BOT_PORT': '9000', 'TRADING_MODE': 'paper'}
    )
    
    # Wait for bot to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = requests.get('http://localhost:9000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test status before kill switch
        print("\n3. Checking initial status...")
        response = requests.get('http://localhost:9000/status', timeout=5)
        status = response.json()
        print(f"  Kill switch active: {status.get('state', {}).get('killSwitch', {}).get('active', 'unknown')}")
        
        # Activate kill switch
        print("\n4. Activating kill switch...")
        response = requests.post(
            'http://localhost:9000/kill-switch',
            json={'action': 'activate', 'reason': 'Test activation'},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Kill switch activated: {result.get('message')}")
        else:
            print(f"❌ Failed to activate kill switch: {response.status_code}")
            return False
        
        # Verify kill switch is active
        print("\n5. Verifying kill switch status...")
        response = requests.get('http://localhost:9000/status', timeout=5)
        status = response.json()
        kill_switch_active = status.get('state', {}).get('killSwitch', {}).get('active', False)
        if kill_switch_active:
            print("✅ Kill switch is active")
        else:
            print("❌ Kill switch should be active but isn't")
            return False
        
        # Try to start bot (should fail)
        print("\n6. Testing start while kill switch active...")
        response = requests.post(
            'http://localhost:9000/control',
            json={'action': 'start'},
            timeout=5
        )
        if response.status_code == 403:
            print("✅ Start correctly blocked by kill switch")
        else:
            print(f"❌ Start should have been blocked: {response.status_code}")
            return False
        
        # Deactivate kill switch
        print("\n7. Deactivating kill switch...")
        response = requests.post(
            'http://localhost:9000/kill-switch',
            json={'action': 'deactivate', 'reason': 'Test deactivation'},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Kill switch deactivated: {result.get('message')}")
        else:
            print(f"❌ Failed to deactivate kill switch: {response.status_code}")
            return False
        
        # Verify kill switch is inactive
        print("\n8. Verifying kill switch is inactive...")
        response = requests.get('http://localhost:9000/status', timeout=5)
        status = response.json()
        kill_switch_active = status.get('state', {}).get('killSwitch', {}).get('active', True)
        if not kill_switch_active:
            print("✅ Kill switch is inactive")
        else:
            print("❌ Kill switch should be inactive but isn't")
            return False
        
        # Try to start bot (should succeed)
        print("\n9. Testing start after kill switch deactivation...")
        response = requests.post(
            'http://localhost:9000/control',
            json={'action': 'start'},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Start succeeded after kill switch deactivation")
        else:
            print(f"❌ Start should have succeeded: {response.status_code}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All kill switch tests passed!")
        print("=" * 60)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        # Stop bot
        print("\n10. Stopping bot...")
        bot_process.terminate()
        bot_process.wait(timeout=5)
        print("✅ Bot stopped")


def test_coordinator_integration():
    """Test bot coordinator integration"""
    print("\n" + "=" * 60)
    print("Testing bot coordinator integration")
    print("=" * 60)
    
    # Just verify the coordinator can be imported
    try:
        import sys
        sys.path.insert(0, 'backend')
        from bot_coordinator import BotCoordinator
        print("✅ Bot coordinator imports successfully")
        
        # Check config files exist
        import json
        from pathlib import Path
        
        config_files = [
            'config/bot-limits.json',
            'config/kill-switch.json',
            'config/recovery-settings.json',
            'config/api-endpoints.json',
            'config/notification-config.json'
        ]
        
        print("\nChecking configuration files:")
        all_exist = True
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file) as f:
                        json.load(f)
                    print(f"  ✅ {config_file}")
                except Exception as e:
                    print(f"  ❌ {config_file} - Invalid JSON: {e}")
                    all_exist = False
            else:
                print(f"  ❌ {config_file} - Not found")
                all_exist = False
        
        return all_exist
        
    except ImportError as e:
        print(f"❌ Failed to import bot coordinator: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n🧪 Bot System Kill Switch Test Suite\n")
    
    # Test bot.js kill switch
    bot_test_passed = test_bot_kill_switch()
    
    # Test coordinator integration
    coordinator_test_passed = test_coordinator_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Bot.js kill switch tests: {'✅ PASSED' if bot_test_passed else '❌ FAILED'}")
    print(f"Coordinator integration: {'✅ PASSED' if coordinator_test_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if bot_test_passed and coordinator_test_passed:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
