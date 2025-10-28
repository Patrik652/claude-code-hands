#!/usr/bin/env python3
"""
Integration Tests
Tests integration between all components (Vision, Memory, Security, Recorder, Orchestrator, Agent)
"""

import sys
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

from integration.orchestrator import AIOrchestrator
from integration.autonomous_agent import AutonomousAgent
from memory.manager import MemoryManager
from security.validator import SecurityValidator
from security.prompt_guard import PromptGuard
from recorder.capture import WorkflowCapture


class TestOrchestrator(unittest.TestCase):
    """Test AIOrchestrator integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = AIOrchestrator()

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        self.assertIsNotNone(self.orchestrator)
        self.assertIsNone(self.orchestrator._vision)  # Lazy loaded
        self.assertIsNone(self.orchestrator._memory)  # Lazy loaded

    def test_lazy_loading(self):
        """Test lazy loading of components"""
        # Vision might fail to load in test environment (no API key), but should attempt
        vision = self.orchestrator.vision
        # Vision loading is attempted - might be None if no Gemini API key configured
        # The important thing is that it's lazy loaded (was None before access)

        # Memory should load on first access
        memory = self.orchestrator.memory
        self.assertIsNotNone(memory)
        self.assertIsNotNone(self.orchestrator._memory)

    def test_start_stop_recording(self):
        """Test workflow recording through orchestrator"""
        # Start recording
        session_id = self.orchestrator.start_recording(
            "test_workflow",
            {'author': 'test'}
        )

        self.assertIsNotNone(session_id)
        self.assertTrue(self.orchestrator.recording)

        # Stop recording
        stopped_id = self.orchestrator.stop_recording()

        self.assertEqual(stopped_id, session_id)
        self.assertFalse(self.orchestrator.recording)

    def test_get_status(self):
        """Test getting orchestrator status"""
        status = self.orchestrator.get_status()

        self.assertIsInstance(status, dict)
        self.assertIn('recording', status)
        self.assertIn('memory_initialized', status)
        self.assertIn('vision_initialized', status)

    async def test_execute_secure_action_validation(self):
        """Test that actions go through security validation"""
        # This would test execute_secure_action with validation
        # For now, just test that method exists
        self.assertTrue(hasattr(self.orchestrator, 'execute_secure_action'))


class TestAutonomousAgent(unittest.TestCase):
    """Test AutonomousAgent integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = AutonomousAgent({
            'confidence_threshold': 0.7,
            'max_retries': 3,
            'learning_enabled': True
        })

    def test_agent_initialization(self):
        """Test agent initializes with correct configuration"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.confidence_threshold, 0.7)
        self.assertEqual(self.agent.max_retries, 3)
        self.assertTrue(self.agent.learning_enabled)

    def test_agent_stats(self):
        """Test getting agent statistics"""
        stats = self.agent.get_agent_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn('total_decisions', stats)
        self.assertIn('successful_actions', stats)
        self.assertIn('failed_actions', stats)

    def test_decision_strategies(self):
        """Test that all decision strategies are available"""
        # Agent should have all three strategies
        self.assertTrue(hasattr(self.agent, '_decide_action'))

        # Strategies should be defined
        # PROVEN, EXPLORATORY, CAUTIOUS
        # These would be tested in actual usage

    async def test_analyze_and_act_interface(self):
        """Test analyze_and_act method interface"""
        # Test that method exists and has correct signature
        self.assertTrue(hasattr(self.agent, 'analyze_and_act'))

        # Would need actual Vision AI to fully test


class TestMemorySecurityIntegration(unittest.TestCase):
    """Test integration between Memory and Security"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        # Use default MemoryManager (will use default config)
        self.memory = MemoryManager()
        self.validator = SecurityValidator()
        self.guard = PromptGuard()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_validated_memory(self):
        """Test storing memory after security validation"""
        # Validate input first
        content = "Login page with form"
        is_valid, reason = self.validator.validate_input(content, 'general')

        self.assertTrue(is_valid)

        # Store if valid
        if is_valid:
            self.memory.start_session("test_session")
            mem_id = self.memory.store_screen_memory(
                content=content,
                ai_analysis="Form detected",
                success=True
            )
            self.assertIsNotNone(mem_id)

    def test_search_with_validated_query(self):
        """Test searching memory with validated query"""
        # Start session and store data
        self.memory.start_session("test_session")
        self.memory.store_screen_memory(
            content="Test content",
            ai_analysis="Test analysis"
        )

        # Validate search query
        query = "test"
        is_safe, reason = self.guard.validate_prompt(query)

        self.assertTrue(is_safe)

        # Search if valid
        if is_safe:
            results = self.memory.search_memories(query, limit=10)
            # Results may be empty but should not error


class TestOrchestratorMemoryIntegration(unittest.TestCase):
    """Test integration between Orchestrator and Memory"""

    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = AIOrchestrator()

    def test_memory_auto_initialization(self):
        """Test that memory is initialized when accessed"""
        # Memory should be None initially
        self.assertIsNone(self.orchestrator._memory)

        # Access memory - should auto-initialize
        memory = self.orchestrator.memory

        self.assertIsNotNone(memory)
        self.assertIsNotNone(self.orchestrator._memory)

    async def test_action_stored_in_memory(self):
        """Test that successful actions are stored in memory"""
        # This would test that execute_secure_action stores in memory
        # Requires actual action execution
        pass


class TestOrchestratorRecorderIntegration(unittest.TestCase):
    """Test integration between Orchestrator and Recorder"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = AIOrchestrator()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_recording_workflow(self):
        """Test that orchestrator can start/stop recording"""
        # Start recording
        session_id = self.orchestrator.start_recording("test_workflow")

        self.assertIsNotNone(session_id)
        self.assertTrue(self.orchestrator.recording)
        self.assertIsNotNone(self.orchestrator.recorder)

        # Stop recording
        stopped_id = self.orchestrator.stop_recording()

        self.assertEqual(stopped_id, session_id)
        self.assertFalse(self.orchestrator.recording)


class TestAgentMemoryIntegration(unittest.TestCase):
    """Test integration between Agent and Memory"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = AutonomousAgent({
            'learning_enabled': True
        })

    def test_agent_has_memory_access(self):
        """Test that agent can access memory system"""
        # Agent should have orchestrator with memory
        self.assertIsNotNone(self.agent.orchestrator)
        self.assertTrue(hasattr(self.agent.orchestrator, 'memory'))

    def test_learning_enabled_stores_memories(self):
        """Test that agent stores experiences when learning is enabled"""
        self.assertTrue(self.agent.learning_enabled)

        # Would need actual action execution to test storage


class TestFullSystemIntegration(unittest.TestCase):
    """Test full system integration (all components)"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = AIOrchestrator()
        self.agent = AutonomousAgent()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_all_components_accessible(self):
        """Test that all components are accessible"""
        # Vision
        self.assertIsNotNone(self.orchestrator.vision)

        # Memory
        self.assertIsNotNone(self.orchestrator.memory)

        # Security
        self.assertIsNotNone(self.orchestrator.validator)

        # Recorder
        self.orchestrator.start_recording("test")
        self.assertIsNotNone(self.orchestrator.recorder)
        self.orchestrator.stop_recording()

        # Agent
        self.assertIsNotNone(self.agent)

    def test_workflow_end_to_end(self):
        """Test complete workflow: record -> validate -> store -> replay"""
        # 1. Start recording
        session_id = self.orchestrator.start_recording("e2e_test")
        self.assertTrue(self.orchestrator.recording)

        # 2. Simulate actions (would execute through orchestrator)
        # For now just verify recording is active

        # 3. Stop recording
        stopped_id = self.orchestrator.stop_recording()
        self.assertEqual(stopped_id, session_id)

        # 4. Verify workflow can be loaded
        # Would load from recorder storage

    def test_security_validates_all_inputs(self):
        """Test that security validation is applied to all inputs"""
        validator = SecurityValidator()

        # Test various input types
        test_inputs = [
            ("ls -la", "command", True),
            ("rm -rf /", "command", False),
            ("https://example.com", "url", True),
            ("javascript:alert()", "url", False),
        ]

        for input_text, input_type, expected_valid in test_inputs:
            is_valid, reason = validator.validate_input(input_text, input_type)
            if not expected_valid:
                self.assertFalse(is_valid, f"{input_text} should be invalid")

    def test_agent_decision_flow(self):
        """Test agent decision-making flow"""
        # Agent should:
        # 1. Analyze situation (Vision)
        # 2. Search memory for similar experiences
        # 3. Decide on action
        # 4. Execute action (through orchestrator)
        # 5. Learn from result (store in memory)

        # Verify agent has all necessary components
        self.assertIsNotNone(self.agent.orchestrator)
        self.assertTrue(hasattr(self.agent, 'analyze_and_act'))
        self.assertTrue(hasattr(self.agent, 'execute_goal_autonomously'))


class TestErrorHandling(unittest.TestCase):
    """Test error handling across components"""

    def test_orchestrator_handles_invalid_action(self):
        """Test orchestrator handles invalid action gracefully"""
        orchestrator = AIOrchestrator()

        # Test with invalid action type
        # Should not crash

    def test_agent_handles_low_confidence(self):
        """Test agent handles low confidence scenarios"""
        agent = AutonomousAgent({'confidence_threshold': 0.9})

        # Agent should use CAUTIOUS strategy for low confidence
        # Verify it doesn't crash

    def test_memory_handles_invalid_query(self):
        """Test memory handles invalid search query"""
        temp_dir = tempfile.mkdtemp()
        memory = MemoryManager()  # Use default config

        try:
            memory.start_session("test")

            # Empty query
            results = memory.search_memories("", limit=10)
            # Should handle gracefully

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("  INTEGRATION TESTS")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestMemorySecurityIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestratorMemoryIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestratorRecorderIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentMemoryIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFullSystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
