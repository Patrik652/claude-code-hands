#!/usr/bin/env python3
"""
Simple Memory System Demo
Quick demonstration of memory system capabilities without async complexity
"""

import sys
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

from memory.manager import MemoryManager


def main():
    print("=" * 70)
    print("🧠 SIMPLE MEMORY SYSTEM DEMO")
    print("=" * 70)

    # Initialize memory manager
    print("\n1️⃣ Initializing Memory Manager...")
    manager = MemoryManager()
    manager.start_session("demo_session_001")
    print("✅ Memory system ready!")

    # Store some screen memories
    print("\n2️⃣ Storing Screen Memories...")

    screens = [
        {
            'content': "Gmail inbox showing 5 unread emails with login button",
            'ai_analysis': "User's Gmail inbox. 5 unread messages. Login button visible in top-right.",
            'url': "https://gmail.com"
        },
        {
            'content': "GitHub repository page with star button and fork count",
            'ai_analysis': "GitHub repo 'claude-vision-hands'. 42 stars, 5 forks. README visible.",
            'url': "https://github.com/user/claude-vision-hands"
        },
        {
            'content': "Amazon product page showing laptop with price $999",
            'ai_analysis': "Laptop product page. Price: $999. Add to cart button present. 4.5 stars.",
            'url': "https://amazon.com/laptop"
        }
    ]

    for i, screen in enumerate(screens, 1):
        memory_id = manager.store_screen_memory(
            content=screen['content'],
            ai_provider="gemini",
            ai_analysis=screen['ai_analysis'],
            metadata={'url': screen['url']}
        )
        print(f"  ✅ Stored memory {i}: {memory_id[:30]}...")

    # Store some actions
    print("\n3️⃣ Storing Action Memories...")

    actions = [
        {
            'content': "Clicked login button on Gmail",
            'action_type': "mouse_click",
            'success': True
        },
        {
            'content': "Typed username 'user@example.com' into login form",
            'action_type': "keyboard_type",
            'success': True
        },
        {
            'content': "Clicked 'Add to Cart' button on Amazon",
            'action_type': "mouse_click",
            'success': True
        }
    ]

    for i, action in enumerate(actions, 1):
        action_id = manager.store_action_memory(
            content=action['content'],
            action_type=action['action_type'],
            success=action['success'],
            mcp_server="hands-mcp"
        )
        print(f"  ✅ Stored action {i}: {action_id[:30]}...")

    # Store a workflow
    print("\n4️⃣ Storing Workflow Memory...")

    workflow_id = manager.store_workflow_memory(
        content="Complete Gmail login workflow: navigate, find form, fill credentials, submit",
        workflow_name="gmail_login",
        steps=[
            {'step': 1, 'action': 'navigate_to_gmail', 'status': 'success'},
            {'step': 2, 'action': 'find_login_form', 'status': 'success'},
            {'step': 3, 'action': 'fill_credentials', 'status': 'success'},
            {'step': 4, 'action': 'submit_form', 'status': 'success'}
        ],
        success=True,
        duration_seconds=3.5
    )
    print(f"  ✅ Stored workflow: {workflow_id[:30]}...")

    # Search memories
    print("\n5️⃣ Searching Memories...")

    queries = [
        "login button",
        "Gmail inbox",
        "shopping cart",
        "keyboard typing"
    ]

    for query in queries:
        print(f"\n  🔍 Query: '{query}'")
        results = manager.search_memories(query, limit=3, min_score=0.3)

        if results.total_count > 0:
            print(f"     Found {results.total_count} results in {results.search_time_ms:.2f}ms:")
            for j, result in enumerate(results.results[:2], 1):
                print(f"       {j}. [Score: {result.score:.3f}] {result.memory.content[:60]}...")
        else:
            print("     No results found")

    # Get statistics
    print("\n6️⃣ Memory System Statistics...")
    stats = manager.get_stats()

    print(f"\n  📊 Total Memories: {stats.total_memories}")
    print(f"     - Screen memories: {stats.memories_by_type.get('screen', 0)}")
    print(f"     - Action memories: {stats.memories_by_type.get('action', 0)}")
    print(f"     - Workflow memories: {stats.memories_by_type.get('workflow', 0)}")

    print(f"\n  💾 Storage:")
    print(f"     - Used: {stats.storage_size_mb:.2f} MB")
    print(f"     - Quota: {stats.quota_limit_mb} MB")
    print(f"     - Usage: {stats.usage_percent:.1f}%")

    if stats.cache_stats:
        cache = stats.cache_stats
        print(f"\n  🗄️  Cache:")
        print(f"     - Entries: {cache.get('size', 0)}/{cache.get('max_size', 0)}")
        print(f"     - Usage: {cache.get('usage_percent', 0):.1f}%")

    # Demonstrate finding similar workflows
    print("\n7️⃣ Finding Similar Workflows...")

    similar_workflows = manager.find_similar_workflows(
        "email login process",
        limit=3,
        success_only=True
    )

    print(f"  Found {len(similar_workflows)} similar successful workflows:")
    for i, workflow in enumerate(similar_workflows, 1):
        print(f"    {i}. {workflow.workflow_name}")
        print(f"       Steps: {workflow.steps_count}, Duration: {workflow.duration_seconds:.2f}s")

    # Check quota
    print("\n8️⃣ Checking Storage Quota...")
    quota = manager.check_quota()

    print(f"  💾 Storage: {quota['used_mb']:.2f} MB / {quota['limit_mb']} MB")
    print(f"  📊 Usage: {quota['usage_percent']:.1f}%")

    if quota['warning']:
        print(f"  ⚠️  {quota['warning']}")

    if quota['should_cleanup']:
        print("  🧹 Cleanup recommended")

    # End session
    print("\n9️⃣ Ending Session...")
    manager.end_session()
    print("  ✅ Session ended")

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    print("\n💡 What you learned:")
    print("  ✅ How to initialize the memory system")
    print("  ✅ How to store screen, action, and workflow memories")
    print("  ✅ How to search memories with natural language")
    print("  ✅ How to get system statistics and quota info")
    print("  ✅ How to find similar past experiences")

    print("\n🚀 Next steps:")
    print("  1. Integrate with vision-mcp for real AI screen analysis")
    print("  2. Integrate with browser-mcp for web automation")
    print("  3. Integrate with hands-mcp for mouse/keyboard control")
    print("  4. Build your own intelligent workflows!")

    print("\n📚 Resources:")
    print("  - Memory README: ../mcp-servers/memory/README.md")
    print("  - Advanced examples: intelligent_workflow_example.py")
    print("  - Configuration: ../config/memory_config.yaml")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
