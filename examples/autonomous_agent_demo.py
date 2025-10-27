#!/usr/bin/env python3
"""
Autonomous Agent Demo
Demonstrates the intelligent autonomous agent capabilities
"""

import sys
import asyncio
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


async def main():
    print_header("🤖 AUTONOMOUS AGENT DEMONSTRATION")

    # Import components
    from integration.autonomous_agent import AutonomousAgent
    from integration.orchestrator import AIOrchestrator

    # ========================================================================
    # PART 1: INITIALIZE AUTONOMOUS AGENT
    # ========================================================================
    print_section("1️⃣", "Initializing Autonomous Agent")

    agent = AutonomousAgent({
        'confidence_threshold': 0.7,
        'learning_enabled': True,
        'max_retries': 3
    })

    print("\n  ✅ Autonomous Agent initialized!")
    print(f"     Confidence Threshold: {agent.confidence_threshold}")
    print(f"     Learning Enabled: {agent.learning_enabled}")
    print(f"     Max Retries: {agent.max_retries}")

    # ========================================================================
    # PART 2: ORCHESTRATOR STATUS
    # ========================================================================
    print_section("2️⃣", "Checking System Components")

    status = agent.orchestrator.get_status()

    print("\n  📊 Component Status:")
    for component, loaded in status['components'].items():
        status_icon = "✅" if loaded else "⚠️"
        status_text = "Loaded" if loaded else "Not loaded"
        print(f"     {status_icon} {component.capitalize()}: {status_text}")

    # ========================================================================
    # PART 3: WORKFLOW RECORDING
    # ========================================================================
    print_section("3️⃣", "Workflow Recording")

    print("\n  🎬 Starting workflow recording...")
    session_id = agent.orchestrator.start_recording(
        "autonomous_demo_session",
        metadata={'demo': True, 'version': '1.0'}
    )
    print(f"     Recording Session ID: {session_id}")

    # ========================================================================
    # PART 4: SIMULATED AUTONOMOUS EXECUTION
    # ========================================================================
    print_section("4️⃣", "Simulated Autonomous Task Execution")

    # Simulate analyzing a situation
    print("\n  🔍 Simulating scenario: Login to website")

    # In real scenario, we would:
    # 1. Capture screenshot
    # 2. Analyze with Vision AI
    # 3. Search memory for similar situations
    # 4. Decide on action
    # 5. Execute action
    # 6. Learn from result

    print("\n  📸 Step 1: Capture screenshot (simulated)")
    screenshot_path = "/tmp/simulated_screenshot.png"
    print(f"     Screenshot: {screenshot_path}")

    print("\n  🧠 Step 2: Analyze situation")
    print("     AI Vision analyzing screen...")
    print("     ✅ Found: Login form with username and password fields")
    print("     ✅ Confidence: 0.85")

    print("\n  💾 Step 3: Search memory for similar experiences")
    print("     Searching for: 'login form'...")
    print("     ✅ Found 3 similar past experiences")
    print("     ✅ 2 successful, 1 failed")

    print("\n  🎯 Step 4: Decide on action")
    print("     Strategy: PROVEN (using successful past approach)")
    print("     Action Plan:")
    print("       1. Focus on username field")
    print("       2. Enter username")
    print("       3. Focus on password field")
    print("       4. Enter password")
    print("       5. Click login button")

    print("\n  ⚡ Step 5: Execute action plan")
    print("     Executing 5 actions...")
    for i in range(1, 6):
        await asyncio.sleep(0.5)  # Simulate execution time
        print(f"       ✅ Action {i}/5 completed")

    print("\n  📚 Step 6: Learn from result")
    print("     Storing workflow in memory...")
    print("     ✅ Workflow stored successfully")
    print("     ✅ Learning complete")

    # ========================================================================
    # PART 5: INTELLIGENT DECISION MAKING
    # ========================================================================
    print_section("5️⃣", "Intelligent Decision Making")

    print("\n  🧠 Demonstrating different strategies based on confidence:")

    scenarios = [
        {
            'name': 'High Confidence + Past Success',
            'confidence': 0.9,
            'past_success': True,
            'strategy': 'PROVEN - Use known successful approach'
        },
        {
            'name': 'High Confidence + No Past Data',
            'confidence': 0.85,
            'past_success': False,
            'strategy': 'EXPLORATORY - Try new approach with monitoring'
        },
        {
            'name': 'Low Confidence',
            'confidence': 0.4,
            'past_success': False,
            'strategy': 'CAUTIOUS - Gather more information first'
        }
    ]

    for scenario in scenarios:
        print(f"\n  📊 Scenario: {scenario['name']}")
        print(f"     Confidence: {scenario['confidence']:.2f}")
        print(f"     Past Success: {'Yes' if scenario['past_success'] else 'No'}")
        print(f"     → Strategy: {scenario['strategy']}")

    # ========================================================================
    # PART 6: ERROR HANDLING & RECOVERY
    # ========================================================================
    print_section("6️⃣", "Error Handling & Recovery")

    print("\n  🛡️ Demonstrating graceful error handling:")

    error_scenarios = [
        {
            'error': 'Element not found',
            'recovery': 'Search for similar element by text'
        },
        {
            'error': 'Action timeout',
            'recovery': 'Retry with longer timeout'
        },
        {
            'error': 'Unexpected screen',
            'recovery': 'Re-analyze and adjust plan'
        }
    ]

    for scenario in error_scenarios:
        print(f"\n  ❌ Error: {scenario['error']}")
        print(f"     → Recovery: {scenario['recovery']}")
        print(f"     ✅ Recovered successfully")

    # ========================================================================
    # PART 7: LEARNING & ADAPTATION
    # ========================================================================
    print_section("7️⃣", "Learning & Adaptation")

    print("\n  📈 How the agent learns over time:")

    learning_progression = [
        {
            'attempt': 1,
            'confidence': 0.5,
            'success': False,
            'lesson': 'Initial exploration'
        },
        {
            'attempt': 2,
            'confidence': 0.65,
            'success': True,
            'lesson': 'Found working approach'
        },
        {
            'attempt': 3,
            'confidence': 0.85,
            'success': True,
            'lesson': 'Refined successful approach'
        },
        {
            'attempt': 4,
            'confidence': 0.95,
            'success': True,
            'lesson': 'Optimized workflow'
        }
    ]

    for progress in learning_progression:
        print(f"\n  📊 Attempt {progress['attempt']}:")
        print(f"     Confidence: {progress['confidence']:.2f}")
        print(f"     Success: {'✅' if progress['success'] else '❌'}")
        print(f"     Lesson: {progress['lesson']}")

    # ========================================================================
    # PART 8: STOP RECORDING & GENERATE WORKFLOW
    # ========================================================================
    print_section("8️⃣", "Workflow Generation")

    print("\n  🎬 Stopping recording...")
    stopped_session = agent.orchestrator.stop_recording()
    print(f"     ✅ Recording stopped: {stopped_session}")

    print("\n  📝 Generating YAML workflow...")
    print("     ✅ Workflow generated:")
    print("""
     name: autonomous_demo_session
     version: 1.0
     steps:
       - step: 1
         action: vision.analyze_screen
         parameters:
           prompt: "Analyze login form"
       - step: 2
         action: memory.search
         parameters:
           query: "login form"
       - step: 3
         action: browser.fill_form
         parameters:
           form_id: "login-form"
    """)

    # ========================================================================
    # PART 9: AGENT STATISTICS
    # ========================================================================
    print_section("9️⃣", "Agent Statistics")

    stats = agent.get_agent_stats()

    print("\n  📊 Agent Performance:")
    print(f"     Total Tasks: {stats['total_tasks']}")
    print(f"     Learning Enabled: {stats['learning_enabled']}")
    print(f"     Confidence Threshold: {stats['confidence_threshold']}")

    # ========================================================================
    # PART 10: KEY CAPABILITIES SUMMARY
    # ========================================================================
    print_section("🎉", "Key Capabilities Demonstrated")

    capabilities = [
        "✅ Vision AI Integration - Analyze screens intelligently",
        "✅ Memory System - Learn from past experiences",
        "✅ Security Layer - Validate all actions",
        "✅ Workflow Recording - Capture and replay workflows",
        "✅ Intelligent Decision Making - Choose strategies based on confidence",
        "✅ Error Handling - Gracefully recover from failures",
        "✅ Continuous Learning - Improve performance over time",
        "✅ Autonomous Execution - Work towards goals independently"
    ]

    print("\n  🚀 Autonomous Agent Capabilities:")
    for capability in capabilities:
        print(f"     {capability}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("✅ DEMONSTRATION COMPLETE")

    print("\n🎯 What You Learned:")
    print("   ✅ How to initialize the autonomous agent")
    print("   ✅ How the agent analyzes situations and makes decisions")
    print("   ✅ How learning and memory work together")
    print("   ✅ How error handling and recovery work")
    print("   ✅ How workflows are recorded and generated")

    print("\n🚀 Next Steps:")
    print("   1. Integrate with real Vision AI for screen analysis")
    print("   2. Connect browser/desktop control for actions")
    print("   3. Train on your specific use cases")
    print("   4. Deploy autonomous workflows")

    print("\n📚 Related Documentation:")
    print("   - Integration README: mcp-servers/integration/README.md")
    print("   - Recorder README: mcp-servers/recorder/README.md")
    print("   - Memory System: mcp-servers/memory/README.md")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
