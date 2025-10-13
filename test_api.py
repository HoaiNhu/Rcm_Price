"""
API Testing Script cho AI Promotion System
Test tất cả các endpoints và functionality
"""
import requests
import json
import time
from typing import Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITester:
    """API Tester cho AI Promotion System"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
        logger.info(f"🚀 API Tester initialized with base URL: {base_url}")
    
    def test_endpoint(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Test một endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "response_time": response.elapsed.total_seconds(),
                "response_size": len(response.content)
            }
            
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text
            
            return result
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "response_time": 0,
                "response_size": 0
            }
    
    def test_basic_endpoints(self):
        """Test basic endpoints"""
        logger.info("🔍 Testing Basic Endpoints...")
        
        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
        ]
        
        results = []
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {method} {endpoint} - {result['status_code']} ({result['response_time']:.2f}s)")
            else:
                logger.error(f"❌ {method} {endpoint} - {result['status_code']} - {result.get('error', 'Unknown error')}")
        
        self.test_results["basic_endpoints"] = results
        return results
    
    def test_hybrid_endpoints(self):
        """Test hybrid recommendation system endpoints"""
        logger.info("🤖 Testing Hybrid Recommendation System...")
        
        # First initialize the system
        init_result = self.test_endpoint("POST", "/api/hybrid/initialize")
        logger.info(f"🔄 System initialization: {init_result['status_code']}")
        
        # Wait a bit for initialization
        time.sleep(2)
        
        endpoints = [
            ("GET", "/api/hybrid/promotion-strategy"),
            ("POST", "/api/hybrid/generate-complete-strategy"),
        ]
        
        results = [init_result]
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {method} {endpoint} - {result['status_code']} ({result['response_time']:.2f}s)")
            else:
                logger.error(f"❌ {method} {endpoint} - {result['status_code']}")
        
        self.test_results["hybrid_endpoints"] = results
        return results
    
    def test_individual_model_endpoints(self):
        """Test individual model endpoints"""
        logger.info("🧠 Testing Individual Model Endpoints...")
        
        # Get some sample IDs first
        products_response = self.test_endpoint("GET", "/api/data/products")
        users_response = self.test_endpoint("GET", "/api/data/users")
        
        sample_product_id = None
        sample_user_id = None
        
        if products_response["success"] and products_response["data"].get("products"):
            sample_product_id = products_response["data"]["products"][0]["_id"]
        
        if users_response["success"] and users_response["data"].get("users"):
            sample_user_id = users_response["data"]["users"][0]["_id"]
        
        endpoints = []
        
        if sample_user_id:
            endpoints.extend([
                ("GET", f"/api/tf-recommenders/recommendations/{sample_user_id}"),
                ("GET", f"/api/hybrid/user-recommendations/{sample_user_id}"),
            ])
        
        if sample_product_id:
            endpoints.extend([
                ("GET", f"/api/huggingface/similar-products/{sample_product_id}"),
                ("GET", f"/api/hybrid/product-recommendations/{sample_product_id}"),
                ("GET", f"/api/pricing/optimize/{sample_product_id}"),
            ])
        
        endpoints.extend([
            ("GET", "/api/huggingface/search-products?query=bánh sinh nhật"),
            ("GET", "/api/pricing/strategy"),
        ])
        
        results = []
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {method} {endpoint} - {result['status_code']} ({result['response_time']:.2f}s)")
            else:
                logger.error(f"❌ {method} {endpoint} - {result['status_code']}")
        
        self.test_results["individual_model_endpoints"] = results
        return results
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        logger.info("📊 Testing Analytics Endpoints...")
        
        endpoints = [
            ("GET", "/api/analytics/business-health"),
            ("GET", "/api/analytics/product-performance"),
            ("GET", "/api/analytics/customer-insights"),
            ("GET", "/api/analytics/trends"),
        ]
        
        results = []
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {method} {endpoint} - {result['status_code']} ({result['response_time']:.2f}s)")
            else:
                logger.error(f"❌ {method} {endpoint} - {result['status_code']}")
        
        self.test_results["analytics_endpoints"] = results
        return results
    
    def test_data_endpoints(self):
        """Test data access endpoints"""
        logger.info("💾 Testing Data Access Endpoints...")
        
        endpoints = [
            ("GET", "/api/data/products"),
            ("GET", "/api/data/users"),
            ("GET", "/api/data/orders?limit=10"),
            ("GET", "/api/data/ratings"),
            ("GET", "/api/data/discounts"),
            ("GET", "/api/data/search-histories"),
        ]
        
        results = []
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            results.append(result)
            
            if result["success"]:
                data_count = result["data"].get("count", 0)
                logger.info(f"✅ {method} {endpoint} - {result['status_code']} ({data_count} records)")
            else:
                logger.error(f"❌ {method} {endpoint} - {result['status_code']}")
        
        self.test_results["data_endpoints"] = results
        return results
    
    def test_legacy_endpoints(self):
        """Test legacy endpoints for backward compatibility"""
        logger.info("🔄 Testing Legacy Endpoints...")
        
        endpoints = [
            ("GET", "/api/business-health"),
            ("GET", "/api/product-combos"),
            ("GET", "/api/recommendations"),
            ("POST", "/api/generate-strategy"),
            ("GET", "/api/recent-strategies"),
        ]
        
        results = []
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {method} {endpoint} - {result['status_code']} ({result['response_time']:.2f}s)")
            else:
                logger.error(f"❌ {method} {endpoint} - {result['status_code']}")
        
        self.test_results["legacy_endpoints"] = results
        return results
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting comprehensive API testing...")
        start_time = time.time()
        
        # Run all test suites
        self.test_basic_endpoints()
        self.test_hybrid_endpoints()
        self.test_individual_model_endpoints()
        self.test_analytics_endpoints()
        self.test_data_endpoints()
        self.test_legacy_endpoints()
        
        total_time = time.time() - start_time
        
        # Generate summary
        self.generate_summary(total_time)
        
        logger.info(f"🎉 All tests completed in {total_time:.2f} seconds")
    
    def generate_summary(self, total_time: float):
        """Generate test summary"""
        logger.info("📊 Generating Test Summary...")
        
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        
        for category, results in self.test_results.items():
            for result in results:
                total_tests += 1
                if result["success"]:
                    successful_tests += 1
                else:
                    failed_tests += 1
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_time": total_time,
            "categories": {}
        }
        
        # Category breakdown
        for category, results in self.test_results.items():
            cat_success = sum(1 for r in results if r["success"])
            cat_total = len(results)
            summary["categories"][category] = {
                "total": cat_total,
                "successful": cat_success,
                "failed": cat_total - cat_success,
                "success_rate": (cat_success / cat_total * 100) if cat_total > 0 else 0
            }
        
        # Print summary
        print("\n" + "="*60)
        print("📊 API TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print("\n📋 Category Breakdown:")
        
        for category, stats in summary["categories"].items():
            print(f"  {category}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        print("="*60)
        
        # Save detailed results
        self.save_results(summary)
    
    def save_results(self, summary: Dict[str, Any]):
        """Save test results to file"""
        try:
            results_data = {
                "summary": summary,
                "detailed_results": self.test_results,
                "timestamp": time.time()
            }
            
            with open("api_test_results.json", "w", encoding="utf-8") as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 Test results saved to api_test_results.json")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")

def main():
    """Main function to run API tests"""
    print("🚀 AI Promotion System API Tester")
    print("="*50)
    
    # Initialize tester
    tester = APITester()
    
    # Run all tests
    tester.run_all_tests()
    
    print("\n🎉 Testing completed!")
    print("Check 'api_test_results.json' for detailed results.")

if __name__ == "__main__":
    main()
