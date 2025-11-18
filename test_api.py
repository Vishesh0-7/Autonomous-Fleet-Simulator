"""
API Test Client
Simple script to test the Fleet Simulator API endpoints.
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_root():
    """Test the root endpoint."""
    print_header("Testing GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_get_robots():
    """Test getting all robots."""
    print_header("Testing GET /robots")
    response = requests.get(f"{BASE_URL}/robots")
    print(f"Status Code: {response.status_code}")
    robots = response.json()
    print(f"Number of robots: {len(robots)}\n")
    for robot in robots:
        print(f"Robot {robot['id']}: pos=({robot['x']},{robot['y']}), "
              f"status={robot['status']}, battery={robot['battery']}%")


def test_get_single_robot():
    """Test getting a single robot."""
    print_header("Testing GET /robots/1")
    response = requests.get(f"{BASE_URL}/robots/1")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_fleet_summary():
    """Test getting fleet summary."""
    print_header("Testing GET /fleet/summary")
    response = requests.get(f"{BASE_URL}/fleet/summary")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_reset():
    """Test resetting the fleet."""
    print_header("Testing POST /reset")
    response = requests.post(f"{BASE_URL}/reset")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Message: {data['message']}")
    print(f"Number of robots reset: {len(data['robots'])}")


def main():
    """Run all API tests."""
    print("\n🧪 Testing Warehouse Fleet Simulator API")
    print(f"🔗 Base URL: {BASE_URL}")
    
    try:
        # Test 1: Root endpoint
        test_root()
        time.sleep(1)
        
        # Test 2: Get all robots
        test_get_robots()
        time.sleep(1)
        
        # Test 3: Get single robot
        test_get_single_robot()
        time.sleep(1)
        
        # Test 4: Fleet summary
        test_fleet_summary()
        time.sleep(1)
        
        # Test 5: Wait for simulation update
        print_header("Waiting 3 seconds for simulation to update robots...")
        time.sleep(3)
        test_get_robots()
        time.sleep(1)
        
        # Test 6: Reset fleet
        test_reset()
        time.sleep(1)
        
        # Test 7: Verify reset
        print_header("Verifying robots after reset")
        test_get_robots()
        
        print("\n" + "="*60)
        print("✅ All API tests completed successfully!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the server is running: python app.py")
        print()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
