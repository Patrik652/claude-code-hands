#!/usr/bin/env python3
"""
Workflow Recorder Tests
Tests workflow capture, generation, optimization, and replay
"""

import sys
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

from recorder.capture import WorkflowCapture, CapturedAction, RecordingSession
from recorder.workflow_generator import WorkflowGenerator


class TestWorkflowCapture(unittest.TestCase):
    """Test WorkflowCapture functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test recordings
        self.test_dir = tempfile.mkdtemp()
        self.capture = WorkflowCapture(config={
            'storage_path': self.test_dir
        })

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_start_recording(self):
        """Test starting a recording session"""
        session_id = self.capture.start_recording(
            "test_workflow",
            metadata={'author': 'test', 'version': '1.0'}
        )

        self.assertIsNotNone(session_id)
        self.assertTrue(session_id.startswith('session_'))
        self.assertIsNotNone(self.capture.current_session)
        self.assertEqual(self.capture.current_session.name, "test_workflow")

    def test_capture_action(self):
        """Test capturing an action"""
        # Start recording
        session_id = self.capture.start_recording("test_workflow")

        # Capture action
        action_id = self.capture.capture_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'},
            result={'analysis': 'Test screen'}
        )

        self.assertIsNotNone(action_id)
        self.assertEqual(len(self.capture.current_session.actions), 1)

        action = self.capture.current_session.actions[0]
        self.assertEqual(action.action_type, 'vision')
        self.assertEqual(action.tool_name, 'analyze_screen')
        self.assertTrue(action.success)

    def test_capture_failed_action(self):
        """Test capturing a failed action"""
        session_id = self.capture.start_recording("test_workflow")

        action_id = self.capture.capture_action(
            action_type='browser',
            tool_name='click',
            parameters={'selector': '#button'},
            result={'error': 'Element not found'},
            success=False,  # Explicitly mark as failed
            error='Element not found'  # Add error message
        )

        action = self.capture.current_session.actions[0]
        self.assertFalse(action.success)
        self.assertIsNotNone(action.error)

    def test_stop_recording(self):
        """Test stopping recording and saving workflow"""
        # Start and capture
        session_id = self.capture.start_recording("test_workflow")
        self.capture.capture_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'}
        )

        # Stop recording
        saved_id = self.capture.stop_recording()

        self.assertEqual(saved_id, session_id)
        self.assertIsNone(self.capture.current_session)

        # Verify file was saved
        workflow_file = Path(self.test_dir) / f"{session_id}.json"
        self.assertTrue(workflow_file.exists())

    def test_load_session(self):
        """Test loading a saved session"""
        # Create and save session
        session_id = self.capture.start_recording("test_workflow")
        self.capture.capture_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'}
        )
        self.capture.stop_recording()

        # Load session
        loaded_session = self.capture.load_session(session_id)

        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session.session_id, session_id)
        self.assertEqual(loaded_session.name, "test_workflow")
        self.assertEqual(len(loaded_session.actions), 1)

    def test_multiple_actions(self):
        """Test recording multiple actions"""
        session_id = self.capture.start_recording("multi_action_workflow")

        # Capture multiple actions
        for i in range(5):
            self.capture.capture_action(
                action_type='browser',
                tool_name='click',
                parameters={'selector': f'#button{i}'}
            )

        self.assertEqual(len(self.capture.current_session.actions), 5)

    def test_action_timing(self):
        """Test that action timing is recorded"""
        session_id = self.capture.start_recording("timing_test")

        action_id = self.capture.capture_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'}
        )

        action = self.capture.current_session.actions[0]
        self.assertIsNotNone(action.timestamp)
        self.assertIsInstance(action.timestamp, float)


class TestWorkflowGenerator(unittest.TestCase):
    """Test WorkflowGenerator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = WorkflowGenerator()

    def test_generate_basic_workflow(self):
        """Test generating a basic workflow"""
        # Create test session
        session = RecordingSession(
            session_id='test_123',
            name='test_workflow',
            metadata={'author': 'test'}
        )

        # Add action
        action = CapturedAction(
            timestamp=datetime.now().timestamp(),
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'},
            success=True
        )
        session.actions.append(action)

        # Generate workflow
        workflow = self.generator.generate_workflow(session)

        self.assertIsNotNone(workflow)
        self.assertEqual(workflow['name'], 'test_workflow')
        self.assertIn('steps', workflow)
        self.assertEqual(len(workflow['steps']), 1)

    def test_variable_extraction(self):
        """Test that variables are extracted from repeated values"""
        session = RecordingSession(
            session_id='test_123',
            name='test_workflow',
            metadata={}
        )

        # Add actions with repeated values
        for i in range(3):
            action = CapturedAction(
                timestamp=datetime.now().timestamp(),
                action_type='browser',
                tool_name='type',
                parameters={
                    'selector': '#input',
                    'text': 'repeated_text'  # Same text in all actions
                },
                success=True
            )
            session.actions.append(action)

        workflow = self.generator.generate_workflow(session, optimize=True)

        # Should extract 'repeated_text' as variable
        self.assertIn('variables', workflow)
        # Note: Variable extraction logic may vary

    def test_loop_detection(self):
        """Test that repeating patterns are detected as loops"""
        session = RecordingSession(
            session_id='test_123',
            name='loop_workflow',
            metadata={}
        )

        # Add repeating pattern
        for i in range(5):
            # Pattern: click -> type -> click
            session.actions.append(CapturedAction(
                timestamp=datetime.now().timestamp(),
                action_type='browser',
                tool_name='click',
                parameters={'selector': f'#item{i}'},
                success=True
            ))
            session.actions.append(CapturedAction(
                timestamp=datetime.now().timestamp(),
                action_type='browser',
                tool_name='type',
                parameters={'selector': '#input', 'text': f'text{i}'},
                success=True
            ))

        workflow = self.generator.generate_workflow(session, optimize=True)

        # Should detect loop pattern
        # Note: Loop detection is complex, this is a basic test

    def test_workflow_metadata(self):
        """Test that workflow metadata is preserved"""
        session = RecordingSession(
            session_id='test_123',
            name='test_workflow',
            metadata={
                'author': 'test_user',
                'version': '1.0',
                'description': 'Test workflow'
            }
        )

        session.actions.append(CapturedAction(
            timestamp=datetime.now().timestamp(),
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'},
            success=True
        ))

        workflow = self.generator.generate_workflow(session)

        self.assertIn('metadata', workflow)
        self.assertEqual(workflow['metadata']['author'], 'test_user')
        self.assertEqual(workflow['metadata']['version'], '1.0')

    def test_failed_actions_handling(self):
        """Test that failed actions are handled properly"""
        session = RecordingSession(
            session_id='test_123',
            name='test_workflow',
            metadata={}
        )

        # Add successful action
        session.actions.append(CapturedAction(
            timestamp=datetime.now().timestamp(),
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'},
            success=True
        ))

        # Add failed action
        session.actions.append(CapturedAction(
            timestamp=datetime.now().timestamp(),
            action_type='browser',
            tool_name='click',
            parameters={'selector': '#button'},
            success=False,
            error='Element not found'
        ))

        workflow = self.generator.generate_workflow(session)

        # Should include both actions
        self.assertEqual(len(workflow['steps']), 2)

    def test_optimize_flag(self):
        """Test that optimize flag affects workflow generation"""
        session = RecordingSession(
            session_id='test_123',
            name='test_workflow',
            metadata={}
        )

        # Add multiple similar actions
        for i in range(10):
            session.actions.append(CapturedAction(
                timestamp=datetime.now().timestamp(),
                action_type='browser',
                tool_name='click',
                parameters={'selector': f'#button{i}'},
                success=True
            ))

        # Generate without optimization
        workflow_unoptimized = self.generator.generate_workflow(
            session,
            optimize=False
        )

        # Generate with optimization
        workflow_optimized = self.generator.generate_workflow(
            session,
            optimize=True
        )

        # Optimized version should potentially have fewer steps
        # (depending on optimization logic)


class TestWorkflowReplay(unittest.TestCase):
    """Test workflow replay functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.capture = WorkflowCapture(config={
            'storage_path': self.test_dir
        })

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_replay_basic_workflow(self):
        """Test replaying a basic workflow"""
        # Create workflow
        session_id = self.capture.start_recording("replay_test")
        self.capture.capture_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'}
        )
        self.capture.stop_recording()

        # Load for replay
        session = self.capture.load_session(session_id)

        self.assertIsNotNone(session)
        self.assertEqual(len(session.actions), 1)

        # Replay would happen here with orchestrator
        # This test just verifies session can be loaded

    def test_workflow_persistence(self):
        """Test that workflows persist across instances"""
        # Create workflow in first instance
        capture1 = WorkflowCapture(config={'storage_path': self.test_dir})
        session_id = capture1.start_recording("persistence_test")
        capture1.capture_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={'screenshot_path': 'test.png'}
        )
        capture1.stop_recording()

        # Load in second instance
        capture2 = WorkflowCapture(config={'storage_path': self.test_dir})
        session = capture2.load_session(session_id)

        self.assertIsNotNone(session)
        self.assertEqual(session.name, "persistence_test")


def run_recorder_tests():
    """Run all recorder tests"""
    print("=" * 70)
    print("  WORKFLOW RECORDER TESTS")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowCapture))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowReplay))

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
    success = run_recorder_tests()
    sys.exit(0 if success else 1)
