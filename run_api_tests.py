# 🧪 Automated API Testing Script
# Run all essential endpoints automatically

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10  # seconds

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.product_id = None
        self.user_id = None
        
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     data: Dict = None, params: Dict = None) -> Tuple[bool, Dict]:
        """Test single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = datetime.now()
            
            if method == "GET":
                response = requests.get(url, params=params, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=data, params=params, timeout=TIMEOUT)
            else:
                return False, {"error": "Unsupported method"}
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000  # ms
            
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time_ms": round(elapsed, 2),
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else None
            }
            
            return result["success"], result
            
        except Exception as e:
            return False, {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "error": str(e),
                "success": False
            }
    
    def print_result(self, success: bool, result: Dict):
        """Print test result with colors"""
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if success else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        name = result.get("name", "Unknown")
        endpoint = result.get("endpoint", "")
        
        print(f"\n{status} {Colors.BLUE}{name}{Colors.RESET}")
        print(f"  Method: {result.get('method', 'N/A')}")
        print(f"  Endpoint: {endpoint}")
        print(f"  Status: {result.get('status_code', 'N/A')}")
        
        if "response_time_ms" in result:
            rt = result["response_time_ms"]
            color = Colors.GREEN if rt < 2000 else Colors.YELLOW if rt < 5000 else Colors.RED
            print(f"  Response Time: {color}{rt}ms{Colors.RESET}")
        
        if "error" in result:
            print(f"  {Colors.RED}Error: {result['error']}{Colors.RESET}")
    
    def run_essential_tests(self):
        """Run essential API tests"""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}RCM PRICE API - Automated Testing{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
        
        # Test 1: Health Check
        print(f"\n{Colors.YELLOW}Module 1: Basic & Health{Colors.RESET}")
        success, result = self.test_endpoint(
            "Health Check",
            "GET",
            "/health"
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Test 2: Get Products
        print(f"\n{Colors.YELLOW}Module 2: Data Access{Colors.RESET}")
        success, result = self.test_endpoint(
            "Get Products",
            "GET",
            "/api/data/products",
            params={"limit": 5}
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Save product_id
        if success and result.get("response"):
            products = result["response"].get("products", [])
            if products:
                self.product_id = products[0].get("_id")
                print(f"  {Colors.GREEN}→ Saved product_id: {self.product_id}{Colors.RESET}")
        
        # Test 3: Get Users
        success, result = self.test_endpoint(
            "Get Users",
            "GET",
            "/api/data/users",
            params={"limit": 5}
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Save user_id
        if success and result.get("response"):
            users = result["response"].get("users", [])
            if users:
                self.user_id = users[0].get("_id")
                print(f"  {Colors.GREEN}→ Saved user_id: {self.user_id}{Colors.RESET}")
        
        # Test 4: Business Health
        print(f"\n{Colors.YELLOW}Module 3: Analytics{Colors.RESET}")
        success, result = self.test_endpoint(
            "Business Health Analysis",
            "GET",
            "/api/analytics/business-health"
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Test 5: Customer Segmentation
        print(f"\n{Colors.YELLOW}Module 4: Customer Segmentation{Colors.RESET}")
        success, result = self.test_endpoint(
            "Segment All Customers",
            "POST",
            "/api/customer-segmentation/segment",
            data={
                "min_orders_for_analysis": 1,
                "vip_threshold": 500000
            }
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Test 6: Price Elasticity Analysis
        print(f"\n{Colors.YELLOW}Module 5: Price Elasticity{Colors.RESET}")
        success, result = self.test_endpoint(
            "Analyze Price Elasticity",
            "POST",
            "/api/price-elasticity/analyze",
            data={
                "product_ids": [],
                "min_orders": 5
            }
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Test 7: Personalized Pricing (if we have user_id)
        if self.user_id:
            print(f"\n{Colors.YELLOW}Module 6: Personalized Pricing{Colors.RESET}")
            success, result = self.test_endpoint(
                "Get Personalized Catalog",
                "GET",
                f"/api/personalized-pricing/catalog/{self.user_id}",
                params={"limit": 5}
            )
            self.print_result(success, result)
            self.results.append(result)
        
        # Test 8: Smart Promotions
        print(f"\n{Colors.YELLOW}Module 8: Smart Promotions{Colors.RESET}")
        success, result = self.test_endpoint(
            "Generate Segment Promotion",
            "POST",
            "/api/smart-promotions/generate-segment-promotion",
            data={
                "segment": "NEW",
                "goal": "ACQUISITION",
                "validity_days": 30
            }
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Test 9: Event Promotions
        print(f"\n{Colors.YELLOW}Module 9: Event Promotions{Colors.RESET}")
        success, result = self.test_endpoint(
            "Analyze Products for Event",
            "GET",
            "/api/event-promotions/analyze-products",
            params={"top_n": 5}
        )
        self.print_result(success, result)
        self.results.append(result)
        
        # Test 10: Hybrid Recommender (if we have user_id)
        if self.user_id:
            print(f"\n{Colors.YELLOW}Module 10: Hybrid Recommender{Colors.RESET}")
            success, result = self.test_endpoint(
                "Get User Recommendations",
                "GET",
                f"/api/hybrid/user-recommendations/{self.user_id}",
                params={"top_k": 5}
            )
            self.print_result(success, result)
            self.results.append(result)
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success"))
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        # Average response time
        response_times = [r.get("response_time_ms", 0) for r in self.results if "response_time_ms" in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"Average Response Time: {avg_time:.2f}ms")
        
        # Failed tests detail
        if failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for r in self.results:
                if not r.get("success"):
                    print(f"  - {r.get('name')}: {r.get('error', 'Unknown error')}")
        
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to JSON file"""
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.get("success")),
            "failed": sum(1 for r in self.results if not r.get("success")),
            "results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Colors.GREEN}✓ Results saved to: {filename}{Colors.RESET}\n")


def main():
    """Main test runner"""
    print(f"\n{Colors.YELLOW}Starting API tests...{Colors.RESET}")
    print(f"Server: {BASE_URL}")
    print(f"Timeout: {TIMEOUT}s")
    
    # Check server availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"{Colors.RED}✗ Server not responding properly{Colors.RESET}")
            return
    except Exception as e:
        print(f"{Colors.RED}✗ Cannot connect to server: {e}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please start the server first:{Colors.RESET}")
        print(f"  python app/main.py")
        return
    
    # Run tests
    tester = APITester(BASE_URL)
    tester.run_essential_tests()


if __name__ == "__main__":
    main()
