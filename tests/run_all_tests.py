#!/usr/bin/env python3
"""
Master Test Runner
Runs all test suites (security, recorder, integration)
"""

import sys
import unittest
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

# Import test modules
import test_security
import test_recorder
import test_integration


def run_all_tests():
    """Run all test suites"""
    print("=" * 70)
    print("  CLAUDE VISION & HANDS - COMPLETE TEST SUITE")
    print("=" * 70)
    print()

    # Create master test suite
    loader = unittest.TestLoader()
    master_suite = unittest.TestSuite()

    # Add security tests
    print("📋 Loading security tests...")
    security_suite = loader.loadTestsFromModule(test_security)
    master_suite.addTests(security_suite)

    # Add recorder tests
    print("📋 Loading recorder tests...")
    recorder_suite = loader.loadTestsFromModule(test_recorder)
    master_suite.addTests(recorder_suite)

    # Add integration tests
    print("📋 Loading integration tests...")
    integration_suite = loader.loadTestsFromModule(test_integration)
    master_suite.addTests(integration_suite)

    print()
    print("=" * 70)
    print(f"  Total test cases loaded: {master_suite.countTestCases()}")
    print("=" * 70)
    print()

    # Run all tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(master_suite)

    # Print comprehensive summary
    print()
    print("=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print(f"  Total Tests Run:     {result.testsRun}")
    print(f"  Passed:              {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed:              {len(result.failures)}")
    print(f"  Errors:              {len(result.errors)}")
    print(f"  Success Rate:        {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)

    # Print failures if any
    if result.failures:
        print()
        print("FAILURES:")
        print("-" * 70)
        for test, traceback in result.failures:
            print(f"\n❌ {test}")
            print(traceback)

    # Print errors if any
    if result.errors:
        print()
        print("ERRORS:")
        print("-" * 70)
        for test, traceback in result.errors:
            print(f"\n❌ {test}")
            print(traceback)

    # Final status
    print()
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")

    print()
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
