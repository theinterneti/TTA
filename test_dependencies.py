#!/usr/bin/env python3
"""
Test script to validate all dependencies and integration issues for Task 19.

This script tests:
1. Missing Python dependencies (huggingface_hub and related packages)
2. Import issues in data models and component integration
3. Neo4j database connection setup and validation
4. Redis caching layer connectivity issues
5. All component dependencies and imports
"""

import sys
import logging
import time
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_python_dependencies() -> Dict[str, Any]:
    """Test that all required Python packages are installed."""
    logger.info("Testing Python dependencies...")
    results = {"status": "success", "details": [], "errors": []}
    
    required_packages = [
        "huggingface_hub",
        "redis", 
        "neo4j",
        "transformers",
        "torch",
        "numpy",
        "pandas"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            results["details"].append(f"✓ {package} - OK")
            logger.info(f"Package {package} imported successfully")
        except ImportError as e:
            error_msg = f"✗ {package} - MISSING: {e}"
            results["errors"].append(error_msg)
            results["status"] = "error"
            logger.error(error_msg)
    
    return results

def test_huggingface_hub() -> Dict[str, Any]:
    """Test huggingface_hub specific functionality."""
    logger.info("Testing huggingface_hub functionality...")
    results = {"status": "success", "details": [], "errors": []}
    
    try:
        from huggingface_hub import HfFolder, login
        results["details"].append("✓ huggingface_hub imports - OK")
        
        # Test basic functionality (without actual login)
        folder = HfFolder()
        results["details"].append("✓ HfFolder instantiation - OK")
        
        logger.info("huggingface_hub functionality test passed")
    except Exception as e:
        error_msg = f"✗ huggingface_hub functionality - ERROR: {e}"
        results["errors"].append(error_msg)
        results["status"] = "error"
        logger.error(error_msg)
    
    return results

def test_redis_connectivity() -> Dict[str, Any]:
    """Test Redis connection and basic operations."""
    logger.info("Testing Redis connectivity...")
    results = {"status": "success", "details": [], "errors": []}
    
    try:
        import redis
        
        # Test connection to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Test ping
        r.ping()
        results["details"].append("✓ Redis connection - OK")
        
        # Test basic operations
        test_key = "test_dependency_check"
        test_value = "test_value"
        
        r.set(test_key, test_value)
        retrieved_value = r.get(test_key)
        
        if retrieved_value == test_value:
            results["details"].append("✓ Redis set/get operations - OK")
        else:
            raise Exception(f"Set/get mismatch: expected {test_value}, got {retrieved_value}")
        
        # Cleanup
        r.delete(test_key)
        results["details"].append("✓ Redis cleanup - OK")
        
        logger.info("Redis connectivity test passed")
        
    except Exception as e:
        error_msg = f"✗ Redis connectivity - ERROR: {e}"
        results["errors"].append(error_msg)
        results["status"] = "error"
        logger.error(error_msg)
    
    return results

def test_neo4j_connectivity() -> Dict[str, Any]:
    """Test Neo4j connection and basic operations."""
    logger.info("Testing Neo4j connectivity...")
    results = {"status": "success", "details": [], "errors": []}
    
    try:
        from neo4j import GraphDatabase
        
        # Test connection to Neo4j (port 7687 from tta.dev)
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "password"
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Test connection with a simple query
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                results["details"].append("✓ Neo4j connection - OK")
            else:
                raise Exception("Neo4j test query failed")
        
        driver.close()
        results["details"].append("✓ Neo4j basic operations - OK")
        
        logger.info("Neo4j connectivity test passed")
        
    except Exception as e:
        error_msg = f"✗ Neo4j connectivity - ERROR: {e}"
        results["errors"].append(error_msg)
        results["status"] = "error"
        logger.error(error_msg)
    
    return results

def test_data_model_imports() -> Dict[str, Any]:
    """Test imports of data models and components."""
    logger.info("Testing data model imports...")
    results = {"status": "success", "details": [], "errors": []}
    
    # Test imports from tta.prototype
    import_tests = [
        ("tta.prototype.database.neo4j_schema", "Neo4jManager"),
        ("tta.prototype.database.redis_cache_enhanced", "RedisCache"),
        ("tta.prototype.database.living_worlds_cache", "LivingWorldsCache"),
    ]
    
    for module_name, class_name in import_tests:
        try:
            # Add the current directory to Python path for imports
            sys.path.insert(0, '.')
            
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            results["details"].append(f"✓ {module_name}.{class_name} - OK")
            logger.info(f"Successfully imported {module_name}.{class_name}")
        except Exception as e:
            error_msg = f"✗ {module_name}.{class_name} - ERROR: {e}"
            results["errors"].append(error_msg)
            results["status"] = "error"
            logger.error(error_msg)
    
    return results

def test_neo4j_manager_integration() -> Dict[str, Any]:
    """Test Neo4jManager class functionality."""
    logger.info("Testing Neo4jManager integration...")
    results = {"status": "success", "details": [], "errors": []}
    
    try:
        sys.path.insert(0, '.')
        from tta.prototype.database.neo4j_schema import Neo4jManager
        
        # Test Neo4jManager instantiation
        manager = Neo4jManager(uri="bolt://localhost:7687", username="neo4j", password="password")
        results["details"].append("✓ Neo4jManager instantiation - OK")
        
        # Test connection
        manager.connect()
        results["details"].append("✓ Neo4jManager connection - OK")
        
        # Test schema validation
        if manager.validate_schema():
            results["details"].append("✓ Neo4jManager schema validation - OK")
        else:
            results["details"].append("⚠ Neo4jManager schema validation - Schema needs setup")
        
        # Test basic query
        result = manager.query("RETURN 1 as test")
        if result and len(result) > 0:
            results["details"].append("✓ Neo4jManager query execution - OK")
        
        manager.disconnect()
        results["details"].append("✓ Neo4jManager disconnection - OK")
        
        logger.info("Neo4jManager integration test passed")
        
    except Exception as e:
        error_msg = f"✗ Neo4jManager integration - ERROR: {e}"
        results["errors"].append(error_msg)
        results["status"] = "error"
        logger.error(error_msg)
    
    return results

def test_redis_cache_integration() -> Dict[str, Any]:
    """Test RedisCache class functionality."""
    logger.info("Testing RedisCache integration...")
    results = {"status": "success", "details": [], "errors": []}
    
    try:
        sys.path.insert(0, '.')
        from tta.prototype.database.redis_cache_enhanced import RedisCache
        
        # Test RedisCache instantiation
        cache = RedisCache(host="localhost", port=6379, db=0)
        results["details"].append("✓ RedisCache instantiation - OK")
        
        # Note: Full connection test would require more setup
        # For now, just test that the class can be imported and instantiated
        
        logger.info("RedisCache integration test passed")
        
    except Exception as e:
        error_msg = f"✗ RedisCache integration - ERROR: {e}"
        results["errors"].append(error_msg)
        results["status"] = "error"
        logger.error(error_msg)
    
    return results

def run_all_tests() -> Dict[str, Any]:
    """Run all dependency and integration tests."""
    logger.info("Starting comprehensive dependency and integration tests...")
    
    all_results = {
        "overall_status": "success",
        "test_results": {},
        "summary": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
    }
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("HuggingFace Hub", test_huggingface_hub),
        ("Redis Connectivity", test_redis_connectivity),
        ("Neo4j Connectivity", test_neo4j_connectivity),
        ("Data Model Imports", test_data_model_imports),
        ("Neo4jManager Integration", test_neo4j_manager_integration),
        ("RedisCache Integration", test_redis_cache_integration),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        try:
            result = test_func()
            all_results["test_results"][test_name] = result
            all_results["summary"]["total_tests"] += 1
            
            if result["status"] == "success":
                all_results["summary"]["passed_tests"] += 1
                logger.info(f"✓ {test_name} - PASSED")
            else:
                all_results["summary"]["failed_tests"] += 1
                all_results["overall_status"] = "partial"
                logger.warning(f"✗ {test_name} - FAILED")
                
        except Exception as e:
            error_result = {
                "status": "error",
                "details": [],
                "errors": [f"Test execution failed: {e}"]
            }
            all_results["test_results"][test_name] = error_result
            all_results["summary"]["total_tests"] += 1
            all_results["summary"]["failed_tests"] += 1
            all_results["overall_status"] = "partial"
            logger.error(f"✗ {test_name} - EXECUTION ERROR: {e}")
    
    return all_results

def print_summary(results: Dict[str, Any]):
    """Print a formatted summary of test results."""
    print("\n" + "="*80)
    print("DEPENDENCY AND INTEGRATION TEST SUMMARY")
    print("="*80)
    
    summary = results["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Overall Status: {results['overall_status'].upper()}")
    
    print("\nDETAILED RESULTS:")
    print("-"*80)
    
    for test_name, test_result in results["test_results"].items():
        status_symbol = "✓" if test_result["status"] == "success" else "✗"
        print(f"\n{status_symbol} {test_name}: {test_result['status'].upper()}")
        
        if test_result["details"]:
            for detail in test_result["details"]:
                print(f"  {detail}")
        
        if test_result["errors"]:
            for error in test_result["errors"]:
                print(f"  {error}")
    
    print("\n" + "="*80)
    
    if results["overall_status"] == "success":
        print("🎉 ALL TESTS PASSED! Dependencies and integration are working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the errors above and fix the issues.")
    
    print("="*80)

if __name__ == "__main__":
    print("TTA Dependency and Integration Test Suite")
    print("Task 19: Resolve critical dependency and integration issues")
    print("="*80)
    
    # Wait a moment for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(5)
    
    # Run all tests
    results = run_all_tests()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "success" else 1)