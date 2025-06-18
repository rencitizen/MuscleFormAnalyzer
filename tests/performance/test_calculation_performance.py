"""
Performance tests for V3 calculation endpoints
Ensures response times meet requirements (<200ms for calculations)
"""
import pytest
import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


class TestPerformanceRequirements:
    """Test cases for performance requirements"""
    
    def test_bmr_calculation_response_time(self):
        """Test BMR calculation response time <200ms"""
        test_data = {
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        }
        
        # Warm-up request
        client.post("/api/v3/calculations/bmr", json=test_data)
        
        # Measure response times
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.post("/api/v3/calculations/bmr", json=test_data)
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            assert response.status_code == 200
            response_times.append(duration)
        
        # Check average response time
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"BMR Calculation - Avg: {avg_response_time:.2f}ms, Max: {max_response_time:.2f}ms")
        assert avg_response_time < 200, f"Average response time {avg_response_time:.2f}ms exceeds 200ms"
        assert max_response_time < 300, f"Max response time {max_response_time:.2f}ms exceeds 300ms"
    
    def test_tdee_calculation_response_time(self):
        """Test TDEE calculation response time <200ms"""
        test_data = {
            "bmr": 1642.5,
            "activity_level": "moderate"
        }
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.post("/api/v3/calculations/tdee", json=test_data)
            duration = (time.time() - start_time) * 1000
            
            assert response.status_code == 200
            response_times.append(duration)
        
        avg_response_time = statistics.mean(response_times)
        print(f"TDEE Calculation - Avg: {avg_response_time:.2f}ms")
        assert avg_response_time < 200
    
    def test_body_fat_calculation_response_time(self):
        """Test body fat estimation response time <200ms"""
        test_data = {
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        }
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.post("/api/v3/calculations/body-fat", json=test_data)
            duration = (time.time() - start_time) * 1000
            
            assert response.status_code == 200
            response_times.append(duration)
        
        avg_response_time = statistics.mean(response_times)
        print(f"Body Fat Calculation - Avg: {avg_response_time:.2f}ms")
        assert avg_response_time < 200
    
    def test_pfc_balance_response_time(self):
        """Test PFC balance calculation response time <200ms"""
        test_data = {
            "calories": 2500,
            "goal": "muscle_gain"
        }
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.post("/api/v3/nutrition/pfc-balance", json=test_data)
            duration = (time.time() - start_time) * 1000
            
            assert response.status_code == 200
            response_times.append(duration)
        
        avg_response_time = statistics.mean(response_times)
        print(f"PFC Balance Calculation - Avg: {avg_response_time:.2f}ms")
        assert avg_response_time < 200
    
    def test_calculation_chain_performance(self):
        """Test complete calculation chain performance"""
        start_time = time.time()
        
        # Step 1: BMR
        bmr_response = client.post("/api/v3/calculations/bmr", json={
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        })
        bmr = bmr_response.json()["bmr"]
        
        # Step 2: TDEE
        tdee_response = client.post("/api/v3/calculations/tdee", json={
            "bmr": bmr,
            "activity_level": "moderate"
        })
        tdee = tdee_response.json()["tdee"]
        
        # Step 3: Target calories
        target_response = client.post("/api/v3/calculations/target-calories", json={
            "tdee": tdee,
            "goal": "muscle_gain"
        })
        
        # Step 4: PFC balance
        pfc_response = client.post("/api/v3/nutrition/pfc-balance", json={
            "calories": target_response.json()["target_calories"],
            "goal": "muscle_gain"
        })
        
        total_duration = (time.time() - start_time) * 1000
        
        print(f"Complete calculation chain - Total: {total_duration:.2f}ms")
        assert total_duration < 800, f"Total chain time {total_duration:.2f}ms exceeds 800ms"


class TestConcurrentRequests:
    """Test concurrent request handling"""
    
    def test_concurrent_bmr_requests(self):
        """Test handling of concurrent BMR calculation requests"""
        test_data = {
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        }
        
        def make_request():
            start_time = time.time()
            response = client.post("/api/v3/calculations/bmr", json=test_data)
            duration = (time.time() - start_time) * 1000
            return response.status_code, duration
        
        # Test 50 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        status_codes = [r[0] for r in results]
        response_times = [r[1] for r in results]
        
        assert all(code == 200 for code in status_codes), "Some requests failed"
        
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        print(f"Concurrent requests - Avg: {avg_response_time:.2f}ms, P95: {p95_response_time:.2f}ms")
        assert p95_response_time < 500, f"P95 response time {p95_response_time:.2f}ms exceeds 500ms"
    
    def test_mixed_endpoint_concurrent_requests(self):
        """Test concurrent requests to different endpoints"""
        endpoints = [
            ("/api/v3/calculations/bmr", {
                "weight": 70.0,
                "height": 170.0,
                "age": 25,
                "gender": "male"
            }),
            ("/api/v3/calculations/tdee", {
                "bmr": 1642.5,
                "activity_level": "moderate"
            }),
            ("/api/v3/calculations/body-fat", {
                "weight": 70.0,
                "height": 170.0,
                "age": 25,
                "gender": "male"
            }),
            ("/api/v3/nutrition/pfc-balance", {
                "calories": 2500,
                "goal": "muscle_gain"
            })
        ]
        
        def make_request(endpoint, data):
            start_time = time.time()
            response = client.post(endpoint, json=data)
            duration = (time.time() - start_time) * 1000
            return response.status_code, duration, endpoint
        
        # Make 100 mixed requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(100):
                endpoint, data = endpoints[i % len(endpoints)]
                futures.append(executor.submit(make_request, endpoint, data))
            
            results = [future.result() for future in futures]
        
        # Check all succeeded
        failed_requests = [(r[2], r[0]) for r in results if r[0] != 200]
        assert len(failed_requests) == 0, f"Failed requests: {failed_requests}"
        
        # Check response times by endpoint
        by_endpoint = {}
        for status, duration, endpoint in results:
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = []
            by_endpoint[endpoint].append(duration)
        
        print("\nMixed endpoint performance:")
        for endpoint, times in by_endpoint.items():
            avg_time = statistics.mean(times)
            print(f"  {endpoint}: {avg_time:.2f}ms")
            assert avg_time < 300, f"{endpoint} avg time {avg_time:.2f}ms exceeds 300ms"


class TestMemoryUsage:
    """Test memory usage during calculations"""
    
    def test_memory_efficiency(self):
        """Test that calculations don't cause memory leaks"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many calculations
        for _ in range(1000):
            client.post("/api/v3/calculations/bmr", json={
                "weight": 70.0,
                "height": 170.0,
                "age": 25,
                "gender": "male"
            })
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage - Initial: {initial_memory:.2f}MB, Final: {final_memory:.2f}MB, Increase: {memory_increase:.2f}MB")
        assert memory_increase < 50, f"Memory increase {memory_increase:.2f}MB exceeds 50MB limit"


if __name__ == "__main__":
    # Run performance tests
    test = TestPerformanceRequirements()
    test.test_bmr_calculation_response_time()
    test.test_calculation_chain_performance()
    
    concurrent_test = TestConcurrentRequests()
    concurrent_test.test_concurrent_bmr_requests()
    concurrent_test.test_mixed_endpoint_concurrent_requests()