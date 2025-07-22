#!/usr/bin/env python3
"""
Comprehensive Test Runner for Subscription System

Runs all subscription system tests with proper organization and reporting.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class TestRunner:
    """Manages and executes subscription system tests"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_test_suite(self, suite_name: str, test_path: str, timeout: int = 300) -> Tuple[bool, str, float]:
        """Run a test suite and return results"""
        print(f"\n{'='*60}")
        print(f"Running {suite_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Run pytest with appropriate flags
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                "--durations=10",
                "--strict-markers",
                "-x"  # Stop on first failure for faster feedback
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.test_dir.parent),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                print(f"✅ {suite_name} PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {suite_name} FAILED ({duration:.2f}s)")
                print(f"Error output:\n{result.stderr}")
            
            return success, output, duration
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {suite_name} TIMEOUT after {timeout}s")
            return False, f"Test suite timed out after {timeout} seconds", timeout
        except Exception as e:
            print(f"💥 {suite_name} ERROR: {e}")
            return False, str(e), 0
    
    def run_all_tests(self, test_types: List[str] = None) -> Dict[str, Tuple[bool, str, float]]:
        """Run all or specified test types"""
        self.start_time = time.time()
        
        # Define test suites
        test_suites = {
            "unit": {
                "name": "Unit Tests",
                "path": "tests/unit/test_subscription_service.py",
                "timeout": 120
            },
            "unit_payment": {
                "name": "Payment Service Unit Tests", 
                "path": "tests/unit/test_payment_service.py",
                "timeout": 120
            },
            "integration": {
                "name": "Integration Tests",
                "path": "tests/integration/test_subscription_integration.py",
                "timeout": 180
            },
            "integration_payment": {
                "name": "Payment Integration Tests",
                "path": "tests/integration/test_subscription_payment_integration.py", 
                "timeout": 180
            },
            "integration_webhook": {
                "name": "Webhook Integration Tests",
                "path": "tests/integration/test_webhook_integration.py",
                "timeout": 120
            },
            "e2e": {
                "name": "End-to-End Tests",
                "path": "tests/integration/test_subscription_e2e.py",
                "timeout": 300
            },
            "performance": {
                "name": "Performance Tests",
                "path": "tests/performance/test_subscription_performance.py",
                "timeout": 600
            },
            "security": {
                "name": "Security Tests", 
                "path": "tests/security/test_subscription_security.py",
                "timeout": 300
            },
            "validation": {
                "name": "Validation Tests",
                "path": "tests/validation/validate_subscription_service.py",
                "timeout": 120,
                "is_script": True
            }
        }
        
        # Filter test suites if specific types requested
        if test_types:
            test_suites = {k: v for k, v in test_suites.items() if k in test_types}
        
        print(f"🚀 Starting Subscription System Test Suite")
        print(f"Running {len(test_suites)} test suite(s)")
        
        # Run each test suite
        for suite_key, suite_config in test_suites.items():
            if suite_config.get("is_script"):
                # Run as Python script
                success, output, duration = self.run_validation_script(
                    suite_config["name"],
                    suite_config["path"],
                    suite_config["timeout"]
                )
            else:
                # Run as pytest
                success, output, duration = self.run_test_suite(
                    suite_config["name"],
                    suite_config["path"],
                    suite_config["timeout"]
                )
            
            self.results[suite_key] = (success, output, duration)
        
        self.end_time = time.time()
        return self.results
    
    def run_validation_script(self, suite_name: str, script_path: str, timeout: int) -> Tuple[bool, str, float]:
        """Run a validation script"""
        print(f"\n{'='*60}")
        print(f"Running {suite_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            cmd = [sys.executable, str(script_path)]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.test_dir.parent),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                print(f"✅ {suite_name} PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {suite_name} FAILED ({duration:.2f}s)")
                print(f"Output:\n{output}")
            
            return success, output, duration
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {suite_name} TIMEOUT after {timeout}s")
            return False, f"Validation script timed out after {timeout} seconds", timeout
        except Exception as e:
            print(f"💥 {suite_name} ERROR: {e}")
            return False, str(e), 0
    
    def generate_report(self) -> str:
        """Generate test results report"""
        if not self.results:
            return "No test results available"
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        report = []
        report.append("\n" + "="*80)
        report.append("SUBSCRIPTION SYSTEM TEST RESULTS")
        report.append("="*80)
        
        # Summary
        total_suites = len(self.results)
        passed_suites = sum(1 for success, _, _ in self.results.values() if success)
        failed_suites = total_suites - passed_suites
        
        report.append(f"\nSUMMARY:")
        report.append(f"  Total Test Suites: {total_suites}")
        report.append(f"  Passed: {passed_suites}")
        report.append(f"  Failed: {failed_suites}")
        report.append(f"  Success Rate: {(passed_suites/total_suites)*100:.1f}%")
        report.append(f"  Total Duration: {total_duration:.2f}s")
        
        # Detailed results
        report.append(f"\nDETAILED RESULTS:")
        for suite_key, (success, output, duration) in self.results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            report.append(f"  {suite_key:20} {status:8} ({duration:6.2f}s)")
        
        # Failed tests details
        failed_tests = [(k, v) for k, v in self.results.items() if not v[0]]
        if failed_tests:
            report.append(f"\nFAILED TEST DETAILS:")
            for suite_key, (_, output, _) in failed_tests:
                report.append(f"\n{suite_key.upper()}:")
                report.append("-" * 40)
                # Show last 20 lines of output for failed tests
                output_lines = output.split('\n')
                relevant_output = '\n'.join(output_lines[-20:]) if len(output_lines) > 20 else output
                report.append(relevant_output)
        
        # Recommendations
        report.append(f"\nRECOMMENDations:")
        if failed_suites == 0:
            report.append("  🎉 All tests passed! The subscription system is ready for production.")
        else:
            report.append(f"  🔧 {failed_suites} test suite(s) failed. Review the failures above.")
            report.append("  📋 Fix failing tests before deploying to production.")
            
            if any("performance" in k for k, (success, _, _) in self.results.items() if not success):
                report.append("  ⚡ Performance tests failed - review system performance.")
            
            if any("security" in k for k, (success, _, _) in self.results.items() if not success):
                report.append("  🔒 Security tests failed - address security issues immediately.")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None) -> str:
        """Save test report to file"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"subscription_test_report_{timestamp}.txt"
        
        report_content = self.generate_report()
        
        report_path = self.test_dir / filename
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return str(report_path)


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run subscription system tests")
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "unit_payment", "integration", "integration_payment", 
                "integration_webhook", "e2e", "performance", "security", "validation"],
        help="Specific test types to run"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Save detailed report to file"
    )
    parser.add_argument(
        "--quick",
        action="store_true", 
        help="Run only essential tests (unit + integration)"
    )
    
    args = parser.parse_args()
    
    # Determine which tests to run
    test_types = None
    if args.quick:
        test_types = ["unit", "unit_payment", "integration", "validation"]
    elif args.types:
        test_types = args.types
    
    # Run tests
    runner = TestRunner()
    results = runner.run_all_tests(test_types)
    
    # Generate and display report
    report = runner.generate_report()
    print(report)
    
    # Save report if requested
    if args.report:
        report_path = runner.save_report()
        print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Exit with appropriate code
    all_passed = all(success for success, _, _ in results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()