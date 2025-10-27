#!/usr/bin/env python3
"""
FULL SYSTEM INTEGRATION DEMO
Demonstrates Vision AI + Browser Control + Memory + Security working together
"""

import sys
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(number, title):
    print(f"\n{number} {title}")
    print("-" * 60)

def main():
    print_header("🚀 CLAUDE VISION & HANDS - FULL SYSTEM DEMO")

    # ========================================================================
    # PART 1: SECURITY LAYER
    # ========================================================================
    print_section("1️⃣", "Security Layer - Input Validation & Protection")

    from security.validator import SecurityValidator

    validator = SecurityValidator()

    # Test various inputs
    test_cases = [
        ("https://example.com", "url"),
        ("rm -rf /", "command"),
        ("/home/user/file.txt", "path"),
        ("SELECT * FROM users", "sql"),
    ]

    print("\n  Testing Security Validation:")
    for test_input, input_type in test_cases:
        is_valid, reason = validator.validate_input(test_input, input_type)
        status = "✅ SAFE" if is_valid else "❌ BLOCKED"
        print(f"    {status}: {input_type:10} - {test_input[:40]}")
        if not is_valid:
            print(f"           Reason: {reason}")

    # ========================================================================
    # PART 2: MEMORY SYSTEM
    # ========================================================================
    print_section("2️⃣", "Memory System - Persistent Learning")

    from memory.manager import MemoryManager

    memory = MemoryManager()
    session_id = "full_demo_001"
    memory.start_session(session_id)
    print(f"\n  ✅ Started memory session: {session_id}")

    # Store some example memories
    memories_to_store = [
        {
            'type': 'screen',
            'content': 'Login page with username and password fields',
            'analysis': 'Form contains: username field, password field, submit button, forgot password link',
            'metadata': {'url': 'https://example.com/login'}
        },
        {
            'type': 'action',
            'content': 'Clicked login button',
            'action_type': 'mouse_click',
            'success': True
        }
    ]

    print("\n  Storing memories:")
    for mem in memories_to_store:
        if mem['type'] == 'screen':
            mem_id = memory.store_screen_memory(
                content=mem['content'],
                ai_provider="gemini",
                ai_analysis=mem['analysis'],
                metadata=mem.get('metadata', {})
            )
        elif mem['type'] == 'action':
            mem_id = memory.store_action_memory(
                content=mem['content'],
                action_type=mem['action_type'],
                success=mem['success'],
                mcp_server="hands-mcp"
            )
        print(f"    ✅ Stored {mem['type']} memory: {mem_id[:30]}...")

    # Search memories
    print("\n  Searching memories:")
    search_results = memory.search_memories("login", limit=5)
    print(f"    🔍 Found {search_results.total_count} results for 'login'")
    for i, result in enumerate(search_results.results[:2], 1):
        print(f"       {i}. [Score: {result.score:.3f}] {result.memory.content[:50]}...")

    # ========================================================================
    # PART 3: VISION AI SIMULATION
    # ========================================================================
    print_section("3️⃣", "Vision AI - Screen Analysis (Simulated)")

    # Simulated vision analysis
    print("\n  📷 Analyzing screenshot...")
    simulated_vision_result = {
        'raw_text': 'Login form with email and password fields',
        'elements': [
            {'type': 'input', 'label': 'Email', 'id': 'email'},
            {'type': 'input', 'label': 'Password', 'id': 'password'},
            {'type': 'button', 'label': 'Login', 'id': 'submit'}
        ],
        'ai_analysis': 'This is a standard login form. The email field is required, password field has a show/hide toggle. Login button is disabled until both fields are filled.'
    }

    print(f"\n  ✅ Vision Analysis Complete:")
    print(f"     Raw Text: {simulated_vision_result['raw_text']}")
    print(f"     Elements Found: {len(simulated_vision_result['elements'])}")
    print(f"     AI Analysis: {simulated_vision_result['ai_analysis']}")

    # Store vision result in memory
    vision_mem_id = memory.store_screen_memory(
        content=simulated_vision_result['raw_text'],
        ai_provider="gemini",
        ai_analysis=simulated_vision_result['ai_analysis'],
        metadata={'elements': len(simulated_vision_result['elements'])}
    )
    print(f"\n  💾 Vision result stored in memory: {vision_mem_id[:30]}...")

    # ========================================================================
    # PART 4: BROWSER CONTROL SIMULATION
    # ========================================================================
    print_section("4️⃣", "Browser Control - Automation (Simulated)")

    # Simulated browser actions
    print("\n  🌐 Browser Actions:")
    browser_actions = [
        "Navigate to https://example.com",
        "Wait for page load",
        "Find email input field",
        "Type: user@example.com",
        "Find password field",
        "Type: ••••••••",
        "Click login button"
    ]

    for i, action in enumerate(browser_actions, 1):
        print(f"     {i}. {action}")
        # Store action in memory
        action_mem = memory.store_action_memory(
            content=action,
            action_type="browser_automation",
            success=True,
            mcp_server="browser-mcp"
        )

    print(f"\n  ✅ {len(browser_actions)} actions executed and stored in memory")

    # ========================================================================
    # PART 5: INTELLIGENT WORKFLOW
    # ========================================================================
    print_section("5️⃣", "Intelligent Workflow - Learning from Experience")

    # Create a workflow combining all components
    workflow_steps = [
        {'step': 1, 'action': 'analyze_screen', 'status': 'success'},
        {'step': 2, 'action': 'validate_inputs', 'status': 'success'},
        {'step': 3, 'action': 'execute_browser_actions', 'status': 'success'},
        {'step': 4, 'action': 'store_results', 'status': 'success'}
    ]

    workflow_id = memory.store_workflow_memory(
        content="Complete login workflow: analyze screen -> validate -> execute -> store",
        workflow_name="automated_login",
        steps=workflow_steps,
        success=True,
        duration_seconds=2.5
    )

    print(f"\n  ✅ Workflow 'automated_login' completed successfully")
    print(f"     Steps: {len(workflow_steps)}")
    print(f"     Duration: 2.5 seconds")
    print(f"     Workflow ID: {workflow_id[:30]}...")

    # Search for similar workflows
    print("\n  🔍 Finding similar past workflows...")
    similar_workflows = memory.find_similar_workflows(
        "login process",
        limit=3,
        success_only=True
    )

    print(f"     Found {len(similar_workflows)} similar successful workflows")
    for i, wf in enumerate(similar_workflows, 1):
        print(f"       {i}. {wf.workflow_name} ({wf.steps_count} steps, {wf.duration_seconds:.2f}s)")

    # ========================================================================
    # PART 6: SYSTEM STATISTICS
    # ========================================================================
    print_section("6️⃣", "System Statistics & Health")

    # Memory stats
    stats = memory.get_stats()
    print(f"\n  📊 Memory System:")
    print(f"     Total Memories: {stats.total_memories}")
    print(f"     - Screen: {stats.memories_by_type.get('screen', 0)}")
    print(f"     - Action: {stats.memories_by_type.get('action', 0)}")
    print(f"     - Workflow: {stats.memories_by_type.get('workflow', 0)}")
    print(f"\n     Storage: {stats.storage_size_mb:.2f} MB / {stats.quota_limit_mb} MB ({stats.usage_percent:.1f}%)")

    # Security report
    security_report = validator.get_security_report()
    print(f"\n  🔒 Security System:")
    print(f"     Strict Mode: {'✅ Enabled' if security_report['strict_mode'] else '❌ Disabled'}")
    print(f"     Validation Rules: {sum(security_report['validation_rules'].values())} patterns")
    print(f"     File Operations: {'✅ Allowed' if security_report['file_operations_allowed'] else '❌ Blocked'}")

    # ========================================================================
    # PART 7: CLEANUP
    # ========================================================================
    print_section("7️⃣", "Session Cleanup")

    memory.end_session()
    print("\n  ✅ Session ended successfully")
    print("  💾 All memories persisted to database")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("✅ DEMO COMPLETED SUCCESSFULLY")

    print("\n🎯 What This Demo Showed:")
    print("   ✅ Security validation protecting against malicious inputs")
    print("   ✅ Memory system storing and retrieving experiences")
    print("   ✅ Vision AI analyzing screen content")
    print("   ✅ Browser automation executing actions")
    print("   ✅ Intelligent workflows learning from past experiences")
    print("   ✅ Full system integration with all components working together")

    print("\n🚀 Next Steps:")
    print("   1. Replace simulated components with real integrations")
    print("   2. Add more complex workflows")
    print("   3. Train on your specific use cases")
    print("   4. Deploy to production")

    print("\n📚 Documentation:")
    print("   - Vision AI: mcp-servers/vision-mcp/README.md")
    print("   - Browser Control: mcp-servers/browser-mcp/README.md")
    print("   - Memory System: mcp-servers/memory/README.md")
    print("   - Security: mcp-servers/security/README.md")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
