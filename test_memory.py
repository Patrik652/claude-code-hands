#!/usr/bin/env python3
"""
Test script for ChromaDB Memory System
Simple smoke test to verify all components work together
"""

import sys
import logging
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-servers"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_memory_system():
    """Test basic memory system functionality"""
    print("=" * 60)
    print("TESTING CHROMADB MEMORY SYSTEM")
    print("=" * 60)

    # Import memory system
    try:
        from memory.manager import MemoryManager
        from memory.config import load_config
        print("✅ Memory modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import memory modules: {e}")
        return False

    # Load configuration
    try:
        config = load_config()
        print(f"✅ Configuration loaded: {config.storage.path}")
        print(f"   - Embedding model: {config.embeddings.model}")
        print(f"   - Storage quota: {config.storage.max_size_mb} MB")
        print(f"   - Auto-capture: {config.auto_capture.enabled}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

    # Initialize Memory Manager
    try:
        manager = MemoryManager()
        print("✅ Memory Manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Memory Manager: {e}")
        return False

    # Start test session
    print("\n--- Starting Test Session ---")
    manager.start_session("test_session_001")
    print("✅ Session started: test_session_001")

    # Test 1: Store screen memory
    print("\n--- Test 1: Store Screen Memory ---")
    try:
        memory_id = manager.store_screen_memory(
            content="User clicked on login button at coordinates (245, 678)",
            ai_provider="gemini",
            ai_prompt="What is visible on this screen?",
            ai_analysis="This is a login page with username and password fields",
            screen_text="Login\nUsername: _____\nPassword: _____\n[Login Button]"
        )
        if memory_id:
            print(f"✅ Screen memory stored: {memory_id}")
        else:
            print("❌ Failed to store screen memory")
            return False
    except Exception as e:
        print(f"❌ Error storing screen memory: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Store action memory
    print("\n--- Test 2: Store Action Memory ---")
    try:
        action_id = manager.store_action_memory(
            content="Mouse click on element at (245, 678) using hands-mcp",
            action_type="mouse_click",
            action_params={"x": 245, "y": 678, "button": "left"},
            success=True,
            mcp_server="hands-mcp"
        )
        if action_id:
            print(f"✅ Action memory stored: {action_id}")
        else:
            print("❌ Failed to store action memory")
            return False
    except Exception as e:
        print(f"❌ Error storing action memory: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Store workflow memory
    print("\n--- Test 3: Store Workflow Memory ---")
    try:
        workflow_id = manager.store_workflow_memory(
            content="Complete login workflow: analyze screen, find login button, click button",
            workflow_name="user_login",
            steps=[
                {"step": 1, "action": "analyze_screen", "status": "success"},
                {"step": 2, "action": "find_login_button", "status": "success"},
                {"step": 3, "action": "click_button", "status": "success"}
            ],
            success=True,
            duration_seconds=2.5
        )
        if workflow_id:
            print(f"✅ Workflow memory stored: {workflow_id}")
        else:
            print("❌ Failed to store workflow memory")
            return False
    except Exception as e:
        print(f"❌ Error storing workflow memory: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Search memories
    print("\n--- Test 4: Search Memories ---")
    try:
        results = manager.search_memories(
            query="login button click",
            limit=5,
            min_score=0.3
        )
        print(f"✅ Search completed: {results.total_count} results in {results.search_time_ms:.2f}ms")

        for i, result in enumerate(results.results[:3], 1):
            print(f"\n   Result {i} (score: {result.score:.3f}):")
            print(f"   - Type: {result.memory.memory_type}")
            print(f"   - Content: {result.memory.content[:80]}...")
    except Exception as e:
        print(f"❌ Error searching memories: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 5: Get statistics
    print("\n--- Test 5: Get Statistics ---")
    try:
        stats = manager.get_stats()
        print(f"✅ Statistics retrieved:")
        print(f"   - Total memories: {stats.total_memories}")
        print(f"   - By type: {stats.memories_by_type}")
        print(f"   - Storage: {stats.storage_size_mb:.2f} MB / {stats.quota_limit_mb} MB")
        print(f"   - Usage: {stats.usage_percent:.1f}%")

        if stats.cache_stats:
            print(f"   - Cache: {stats.cache_stats.get('size', 0)}/{stats.cache_stats.get('max_size', 0)}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 6: Retrieve specific memory
    print("\n--- Test 6: Retrieve Memory ---")
    try:
        retrieved = manager.get_memory(memory_id, "screen")
        if retrieved:
            print(f"✅ Memory retrieved: {retrieved.id}")
            print(f"   - Type: {retrieved.memory_type}")
            print(f"   - Content: {retrieved.content[:80]}...")
            print(f"   - Timestamp: {retrieved.timestamp}")
        else:
            print("❌ Failed to retrieve memory")
            return False
    except Exception as e:
        print(f"❌ Error retrieving memory: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Memory system working correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_memory_system()
    sys.exit(0 if success else 1)
