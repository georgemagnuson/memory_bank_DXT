#!/usr/bin/env python3
"""
Memory Bank DXT Test Script
Created: 2025-07-18.1905
Purpose: Test DXT functionality before building the extension

Tests:
1. Environment validation
2. AppleScript execution
3. Database connectivity
4. Tool functionality
"""

import asyncio
import sys
from pathlib import Path

# Add server directory to path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

async def test_applescript():
    """Test basic AppleScript functionality"""
    print("🧪 Testing AppleScript...")
    
    try:
        import subprocess
        
        # Test basic AppleScript
        result = subprocess.run([
            'osascript', '-e', 'return "AppleScript works!"'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ AppleScript test: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ AppleScript failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ AppleScript test failed: {e}")
        return False

async def test_clipboard():
    """Test clipboard operations"""
    print("🧪 Testing clipboard...")
    
    try:
        import subprocess
        
        # Set clipboard
        test_text = "Memory Bank DXT Test"
        subprocess.run([
            'osascript', '-e', f'set the clipboard to "{test_text}"'
        ], check=True, timeout=5)
        
        # Read clipboard
        result = subprocess.run([
            'osascript', '-e', 'return the clipboard as string'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and test_text in result.stdout:
            print("✅ Clipboard operations working")
            return True
        else:
            print("❌ Clipboard test failed")
            return False
            
    except Exception as e:
        print(f"❌ Clipboard test failed: {e}")
        return False

async def test_database():
    """Test database connectivity"""
    print("🧪 Testing database...")
    
    try:
        db_path = Path(__file__).parent / "memory-bank" / "context.db"
        
        if not db_path.exists():
            print(f"❌ Database not found: {db_path}")
            return False
        
        import sqlite3
        
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
        print(f"✅ Database connected: {len(tables)} tables found")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_memory_bank_dxt():
    """Test Memory Bank DXT server initialization"""
    print("🧪 Testing Memory Bank DXT server...")
    
    try:
        # Import our server
        from main import MemoryBankDXT
        
        # Initialize (but don't run)
        memory_bank = MemoryBankDXT()
        
        # Test tool listing
        tools = await memory_bank._handle_list_tools()
        
        expected_tools = ["start_session", "save_this", "replay", "off_the_record", "on_the_record", "session_status"]
        tool_names = [tool.name for tool in tools]
        
        missing_tools = set(expected_tools) - set(tool_names)
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        
        print(f"✅ DXT server initialized: {len(tools)} tools available")
        print(f"   Tools: {', '.join(tool_names)}")
        return True
        
    except Exception as e:
        print(f"❌ DXT server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_claude_detection():
    """Test if Claude Desktop is running and accessible"""
    print("🧪 Testing Claude Desktop detection...")
    
    try:
        import subprocess
        
        # Check if Claude is running
        result = subprocess.run([
            'osascript', '-e', '''
            tell application "System Events"
                return (count of processes whose name is "Claude") > 0
            end tell
            '''
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            is_running = result.stdout.strip() == "true"
            if is_running:
                print("✅ Claude Desktop is running")
                return True
            else:
                print("⚠️ Claude Desktop not running (but AppleScript works)")
                return True  # Still valid for testing
        else:
            print(f"❌ Claude detection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Claude detection failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Memory Bank DXT Test Suite")
    print("=" * 50)
    
    tests = [
        ("AppleScript", test_applescript),
        ("Clipboard", test_clipboard), 
        ("Database", test_database),
        ("Claude Detection", test_claude_detection),
        ("DXT Server", test_memory_bank_dxt)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Ready to build DXT extension.")
        print("\nNext steps:")
        print("1. Run: dxt pack")
        print("2. Install the generated .dxt file in Claude Desktop")
        print("3. Test with: start_session")
    else:
        print("\n⚠️ Some tests failed. Please fix issues before building DXT.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
