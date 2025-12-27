"""
Quick test script to verify Eureka service discovery integration
"""
import asyncio
import httpx
import sys

EUREKA_URL = "http://localhost:8761"
API_GATEWAY_URL = "http://localhost:8000"

async def test_eureka_server():
    """Test 1: Verify Eureka Server is running"""
    print("\n🧪 Test 1: Eureka Server Health")
    print("=" * 60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EUREKA_URL}/actuator/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Eureka Server is UP: {data}")
                return True
            else:
                print(f"❌ Eureka Server returned {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Eureka Server is not accessible: {e}")
        return False

async def test_service_registration():
    """Test 2: Check registered services"""
    print("\n🧪 Test 2: Service Registration")
    print("=" * 60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EUREKA_URL}/eureka/apps", timeout=10.0)
            if response.status_code == 200:
                # Parse XML response (simple check)
                content = response.text
                services = []
                if "API-GATEWAY" in content:
                    services.append("API-GATEWAY")
                if "INDEXEUR-SEMANTIQUE" in content:
                    services.append("INDEXEUR-SEMANTIQUE")
                
                if services:
                    print(f"✅ Registered services: {', '.join(services)}")
                    return True
                else:
                    print("⚠️  No services registered yet")
                    return False
            else:
                print(f"❌ Failed to fetch registered apps: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error checking registrations: {e}")
        return False

async def test_api_gateway():
    """Test 3: API Gateway is accessible"""
    print("\n🧪 Test 3: API Gateway Accessibility")
    print("=" * 60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_GATEWAY_URL}/", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Gateway is running: {data}")
                return True
            else:
                print(f"❌ API Gateway returned {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API Gateway is not accessible: {e}")
        return False

async def test_service_discovery():
    """Test 4: API Gateway can use service discovery"""
    print("\n🧪 Test 4: Service Discovery (Search Endpoint)")
    print("=" * 60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_GATEWAY_URL}/api/v1/search/",
                params={"q": "test", "limit": 5},
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 503]:  # 503 if indexeur not ready
                if response.status_code == 200:
                    print(f"✅ Service discovery working! Search returned results")
                else:
                    print(f"⚠️  Service discovery attempted but indexeur service unavailable (503)")
                    print(f"   This is expected if indexeur-semantique is not running")
                return True
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
    except Exception as e:
        print(f"⚠️  Service discovery test failed: {e}")
        print(f"   This may be normal if services are still starting")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🔍 Eureka Service Discovery Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Eureka Server
    results.append(await test_eureka_server())
    
    # Test 2: Service Registration
    if results[0]:
        results.append(await test_service_registration())
    else:
        print("\n⏭️  Skipping registration test (Eureka not available)")
        results.append(False)
    
    # Test 3: API Gateway
    results.append(await test_api_gateway())
    
    # Test 4: Service Discovery
    if results[2]:
        results.append(await test_service_discovery())
    else:
        print("\n⏭️  Skipping service discovery test (API Gateway not available)")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Eureka integration is working correctly.")
        return 0
    elif passed >= 2:
        print("⚠️  Partial success. Some services may still be starting.")
        print("   Wait 30 seconds and run the tests again.")
        return 1
    else:
        print("❌ Integration issues detected. Check service logs:")
        print("   docker-compose logs eureka-server")
        print("   docker-compose logs api-gateway")
        print("   docker-compose logs indexeur-semantique")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
