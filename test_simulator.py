"""
Test script to verify the Fleet Simulator installation and functionality.
Run this to test the simulator without starting the API server.
"""

import sys
import time
from fleet.fleet_manager import FleetManager


def test_fleet_simulator():
    """Test the fleet simulator components."""
    print("="*60)
    print("🧪 Testing Warehouse Fleet Simulator")
    print("="*60)
    
    # Test 1: Initialize fleet manager
    print("\n✓ Test 1: Initializing FleetManager...")
    fleet = FleetManager(num_robots=5, grid_size=20, update_interval=1)
    print(f"  Created fleet with {len(fleet.robots)} robots")
    
    # Test 2: Display initial robot states
    print("\n✓ Test 2: Initial robot states:")
    for robot in fleet.robots:
        print(f"  {robot}")
    
    # Test 3: Manual fleet update
    print("\n✓ Test 3: Updating fleet manually...")
    fleet.update_fleet()
    print("  Fleet updated successfully")
    
    # Test 4: Get fleet status (JSON format)
    print("\n✓ Test 4: Fleet status (API format):")
    status = fleet.get_fleet_status()
    for robot_data in status[:2]:  # Show first 2 robots
        print(f"  {robot_data}")
    print(f"  ... and {len(status) - 2} more robots")
    
    # Test 5: Get fleet summary
    print("\n✓ Test 5: Fleet summary:")
    summary = fleet.get_fleet_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test 6: Reset fleet
    print("\n✓ Test 6: Resetting fleet...")
    fleet.reset_fleet()
    print("  All robots reset to full battery")
    
    # Test 7: Simulation loop (3 updates)
    print("\n✓ Test 7: Running simulation for 3 seconds...")
    fleet.start_simulation()
    
    for i in range(3):
        time.sleep(1)
        summary = fleet.get_fleet_summary()
        print(f"  Update {i+1}/3 - Avg Battery: {summary['average_battery']}%")
    
    fleet.stop_simulation()
    
    print("\n" + "="*60)
    print("✅ All tests passed! Simulator is working correctly.")
    print("="*60)
    print("\n💡 To start the API server, run: python app.py")
    print()


if __name__ == "__main__":
    try:
        test_fleet_simulator()
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
