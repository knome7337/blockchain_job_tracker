#!/usr/bin/env python3
"""
Test script to demonstrate different discovery modes with safety limits
"""

import sys
import os
sys.path.append('modules')

from module_0_directory import AcceleratorDirectoryBuilder

def test_discovery_modes():
    """Test different discovery modes with their respective limits"""
    
    print("🧪 Testing Discovery Modes with Safety Limits")
    print("=" * 50)
    
    try:
        builder = AcceleratorDirectoryBuilder()
        
        # Test 1: Default mode
        print("\n1️⃣ Testing DEFAULT mode (20 min, 150 max)")
        print("-" * 40)
        count1 = builder.discover_accelerators()
        print(f"✅ Default mode completed: {count1} accelerators found")
        
        # Test 2: Comprehensive mode
        print("\n2️⃣ Testing COMPREHENSIVE mode (30 min, 200 max)")
        print("-" * 40)
        count2 = builder.run_comprehensive_discovery()
        print(f"✅ Comprehensive mode completed: {count2} accelerators found")
        
        # Test 3: Emergency mode
        print("\n3️⃣ Testing EMERGENCY mode (10 min, 50 max)")
        print("-" * 40)
        count3 = builder.run_emergency_discovery()
        print(f"✅ Emergency mode completed: {count3} accelerators found")
        
        # Test 4: Custom limits
        print("\n4️⃣ Testing CUSTOM limits (5 min, 25 max)")
        print("-" * 40)
        count4 = builder.discover_accelerators(time_limit_minutes=5, max_accelerators=25)
        print(f"✅ Custom mode completed: {count4} accelerators found")
        
        print("\n" + "=" * 50)
        print("🎉 All discovery modes tested successfully!")
        print(f"Total accelerators discovered: {count1 + count2 + count3 + count4}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def show_config_info():
    """Show current configuration settings"""
    print("\n📋 Current Discovery Configuration:")
    print("-" * 40)
    
    try:
        builder = AcceleratorDirectoryBuilder()
        settings = builder.discovery_settings
        
        print("Discovery Limits:")
        for key, value in settings['discovery_limits'].items():
            print(f"  {key}: {value}")
        
        print("\nRate Limiting:")
        for key, value in settings['rate_limiting'].items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Failed to load config: {e}")

if __name__ == "__main__":
    show_config_info()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_discovery_modes()
    else:
        print("\nUsage: python test_discovery_limits.py --test")
        print("This will test all discovery modes with their respective limits.") 