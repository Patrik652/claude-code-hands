#!/usr/bin/env python3
"""
Intelligent AI Workflow with Memory Integration
Demonstrates integration of Vision AI, Browser Control, and Persistent Memory

This example shows how to:
1. Navigate to websites using browser automation
2. Analyze screens with AI (Gemini)
3. Store analyses in persistent memory
4. Search memories for context
5. Make intelligent decisions based on past experiences
"""

import sys
import asyncio
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

from memory.manager import MemoryManager


class IntelligentWorkflowAgent:
    """
    AI agent with persistent memory and multi-modal capabilities

    Combines:
    - Vision AI for screen analysis
    - Browser automation for web interaction
    - Persistent memory for context retention
    """

    def __init__(self):
        # Initialize memory system
        self.memory = MemoryManager()
        self.memory.start_session(f"intelligent_workflow_{self._get_timestamp()}")
        print("✅ Memory system initialized")

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    async def navigate_and_analyze(self, url: str, analysis_prompt: str):
        """
        Navigate to URL and analyze the screen with AI

        Args:
            url: Target URL
            analysis_prompt: What to look for

        Returns:
            Analysis results with memory ID
        """
        print(f"\n📍 Navigating to: {url}")

        # TODO: Browser navigation (browser-mcp integration)
        # await browser_navigate(url)

        # Simulate screen capture
        screenshot_path = "/tmp/screenshot.png"

        print(f"🔍 Analyzing screen: {analysis_prompt}")

        # TODO: AI vision analysis (vision-mcp integration)
        # analysis = await analyze_screen_ai(analysis_prompt)

        # Simulated analysis result
        analysis = {
            'raw_text': f"Screen shows {url} with login form",
            'analysis': f"Detected: Login form with username and password fields. Answer to '{analysis_prompt}': Yes, forms are visible.",
            'confidence': 0.95
        }

        # Store in persistent memory
        memory_id = self.memory.store_screen_memory(
            content=f"Website {url}: {analysis['raw_text']}",
            ai_provider="gemini",
            ai_prompt=analysis_prompt,
            ai_analysis=analysis['analysis'],
            screen_text=analysis['raw_text'],
            screenshot_path=screenshot_path
        )

        print(f"💾 Stored in memory: {memory_id}")
        print(f"📊 Analysis: {analysis['analysis'][:100]}...")

        return {
            'memory_id': memory_id,
            'analysis': analysis,
            'url': url
        }

    async def search_past_experiences(self, query: str, limit: int = 5):
        """
        Search memory for relevant past experiences

        Args:
            query: Natural language search query
            limit: Maximum results

        Returns:
            List of relevant memories
        """
        print(f"\n🔎 Searching memories: '{query}'")

        results = self.memory.search_memories(
            query=query,
            limit=limit,
            min_score=0.5
        )

        print(f"📚 Found {results.total_count} relevant memories in {results.search_time_ms:.2f}ms")

        for i, result in enumerate(results.results[:3], 1):
            print(f"  {i}. [Score: {result.score:.3f}] {result.memory.content[:80]}...")

        return results

    async def intelligent_form_fill(self, form_type: str):
        """
        Fill form using information from memory

        Args:
            form_type: Type of form (e.g., 'login', 'registration')
        """
        print(f"\n📝 Intelligent form filling: {form_type}")

        # Search memory for relevant credentials/info
        memories = await self.search_past_experiences(f"{form_type} form credentials")

        if memories.total_count > 0:
            print(f"✅ Found {memories.total_count} relevant memories")

            # TODO: Browser form automation (hands-mcp integration)
            # best_match = memories.results[0]
            # await browser_fill("#username", best_match.memory.metadata.get('username'))
            # await browser_fill("#password", best_match.memory.metadata.get('password'))
            # await browser_click("#login-button")

            # Store the action
            action_id = self.memory.store_action_memory(
                content=f"Filled {form_type} form using remembered credentials",
                action_type="form_fill",
                action_params={'form_type': form_type},
                success=True,
                mcp_server="hands-mcp"
            )

            print(f"✅ Form filled and action stored: {action_id}")
        else:
            print("⚠️ No relevant memories found - manual input required")

    async def execute_workflow(self, workflow_name: str, steps: list):
        """
        Execute multi-step workflow with memory tracking

        Args:
            workflow_name: Name of the workflow
            steps: List of step functions
        """
        print(f"\n🔄 Starting workflow: {workflow_name}")

        from datetime import datetime
        start_time = datetime.now()

        workflow_steps = []

        for i, step in enumerate(steps, 1):
            print(f"\n--- Step {i}/{len(steps)}: {step.__name__} ---")
            try:
                result = await step()
                workflow_steps.append({
                    'step': i,
                    'action': step.__name__,
                    'status': 'success',
                    'result': str(result)[:100]
                })
                print(f"✅ Step {i} completed")
            except Exception as e:
                workflow_steps.append({
                    'step': i,
                    'action': step.__name__,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"❌ Step {i} failed: {e}")
                break

        duration = (datetime.now() - start_time).total_seconds()
        success = all(s['status'] == 'success' for s in workflow_steps)

        # Store workflow in memory
        workflow_id = self.memory.store_workflow_memory(
            content=f"Workflow '{workflow_name}': {len(workflow_steps)} steps executed",
            workflow_name=workflow_name,
            steps=workflow_steps,
            success=success,
            duration_seconds=duration
        )

        print(f"\n{'✅' if success else '❌'} Workflow {'completed' if success else 'failed'}")
        print(f"⏱️ Duration: {duration:.2f}s")
        print(f"💾 Workflow stored: {workflow_id}")

        return {
            'workflow_id': workflow_id,
            'success': success,
            'duration': duration,
            'steps': workflow_steps
        }

    async def get_session_summary(self):
        """Get summary of current session's activities"""
        print("\n📊 Session Summary")
        print("=" * 60)

        stats = self.memory.get_stats()

        print(f"Total memories: {stats.total_memories}")
        print(f"  - Screen: {stats.memories_by_type.get('screen', 0)}")
        print(f"  - Action: {stats.memories_by_type.get('action', 0)}")
        print(f"  - Workflow: {stats.memories_by_type.get('workflow', 0)}")
        print(f"\nStorage: {stats.storage_size_mb:.2f} MB / {stats.quota_limit_mb} MB")
        print(f"Usage: {stats.usage_percent:.1f}%")

        if stats.cache_stats:
            cache = stats.cache_stats
            print(f"\nEmbedding Cache: {cache.get('size', 0)}/{cache.get('max_size', 0)} ({cache.get('usage_percent', 0):.1f}%)")


# ============================================================================
# EXAMPLE USAGE SCENARIOS
# ============================================================================

async def example_1_basic_workflow():
    """Example 1: Basic website analysis with memory"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Website Analysis with Memory")
    print("="*60)

    agent = IntelligentWorkflowAgent()

    # Analyze a website
    result = await agent.navigate_and_analyze(
        url="https://example.com/login",
        analysis_prompt="What forms are visible on this page?"
    )

    # Search for similar screens
    await agent.search_past_experiences("login forms")

    # Get summary
    await agent.get_session_summary()


async def example_2_intelligent_form_filling():
    """Example 2: Intelligent form filling using memory"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Intelligent Form Filling")
    print("="*60)

    agent = IntelligentWorkflowAgent()

    # First visit - analyze and remember
    await agent.navigate_and_analyze(
        url="https://example.com/login",
        analysis_prompt="Identify all form fields"
    )

    # Intelligent form filling based on memory
    await agent.intelligent_form_fill("login")

    await agent.get_session_summary()


async def example_3_complex_workflow():
    """Example 3: Complex multi-step workflow with memory"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Complex Multi-Step Workflow")
    print("="*60)

    agent = IntelligentWorkflowAgent()

    # Define workflow steps
    async def step_1_navigate():
        return await agent.navigate_and_analyze(
            "https://example.com",
            "What is the main content?"
        )

    async def step_2_find_login():
        await agent.search_past_experiences("login button")
        return "Login button located"

    async def step_3_authenticate():
        await agent.intelligent_form_fill("login")
        return "Authentication completed"

    async def step_4_verify():
        return await agent.navigate_and_analyze(
            "https://example.com/dashboard",
            "Is user logged in?"
        )

    # Execute workflow
    result = await agent.execute_workflow(
        workflow_name="user_authentication",
        steps=[step_1_navigate, step_2_find_login, step_3_authenticate, step_4_verify]
    )

    # Search for similar workflows
    await agent.search_past_experiences("authentication workflow")

    await agent.get_session_summary()


async def example_4_learning_from_experience():
    """Example 4: Learning from past experiences"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Learning from Past Experiences")
    print("="*60)

    agent = IntelligentWorkflowAgent()

    # Simulate multiple login attempts
    for i in range(3):
        print(f"\n--- Attempt {i+1} ---")
        await agent.navigate_and_analyze(
            f"https://example.com/login?attempt={i+1}",
            "Check login form structure"
        )

    # Search for patterns
    print("\n🧠 Analyzing learned patterns...")
    results = await agent.search_past_experiences("login form structure", limit=10)

    print(f"\n📈 Learned from {results.total_count} experiences")
    print("Agent can now:")
    print("  - Recognize login forms instantly")
    print("  - Remember field locations")
    print("  - Optimize interaction speed")

    await agent.get_session_summary()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Run all examples"""
    print("\n🤖 INTELLIGENT AI WORKFLOW WITH MEMORY - EXAMPLES")
    print("="*70)

    # Run examples
    await example_1_basic_workflow()

    # Uncomment to run other examples:
    # await example_2_intelligent_form_filling()
    # await example_3_complex_workflow()
    # await example_4_learning_from_experience()

    print("\n" + "="*70)
    print("✅ Examples completed!")
    print("\nNext steps:")
    print("  1. Integrate with vision-mcp for real AI analysis")
    print("  2. Integrate with browser-mcp for real web automation")
    print("  3. Integrate with hands-mcp for real mouse/keyboard control")
    print("  4. Build custom workflows for your use cases")


if __name__ == "__main__":
    # Note: This is a demonstration. For production use:
    # - Add proper error handling
    # - Implement real browser/AI integrations
    # - Add configuration management
    # - Implement security measures

    asyncio.run(main())
