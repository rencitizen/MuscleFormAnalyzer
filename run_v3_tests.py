#!/usr/bin/env python
"""
Test runner for TENAX FIT v3.0 tests
Runs unit tests, integration tests, and performance tests
"""
import subprocess
import sys
import os
from datetime import datetime


def run_tests():
    """Run all v3 tests and generate report"""
    print("=" * 60)
    print(f"TENAX FIT v3.0 Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = {}
    
    # Unit tests
    print("\n1. Running Unit Tests (Scientific Calculations)...")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/test_scientific_calculations.py", "-v"],
        capture_output=True,
        text=True
    )
    test_results['unit'] = {
        'passed': result.returncode == 0,
        'output': result.stdout + result.stderr
    }
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Integration tests
    print("\n2. Running Integration Tests (V3 API)...")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/test_v3_api.py", "-v"],
        capture_output=True,
        text=True
    )
    test_results['integration'] = {
        'passed': result.returncode == 0,
        'output': result.stdout + result.stderr
    }
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Performance tests
    print("\n3. Running Performance Tests...")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/performance/test_calculation_performance.py", 
         "-v", "-s"],  # -s to show print statements
        capture_output=True,
        text=True
    )
    test_results['performance'] = {
        'passed': result.returncode == 0,
        'output': result.stdout + result.stderr
    }
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_type, result in test_results.items():
        status = "PASSED ✓" if result['passed'] else "FAILED ✗"
        print(f"{test_type.capitalize():15} {status}")
        if not result['passed']:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests PASSED! ✅")
        print("Scientific calculations are accurate and performant.")
    else:
        print("Some tests FAILED! ❌")
        print("Please review the errors above.")
    print("=" * 60)
    
    return all_passed


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pytest
        import fastapi
        import psutil
        print("✓ All test dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install pytest psutil")
        return False


if __name__ == "__main__":
    print("TENAX FIT v3.0 - Scientific Calculation Engine Test Suite")
    print()
    
    if not check_dependencies():
        sys.exit(1)
    
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)