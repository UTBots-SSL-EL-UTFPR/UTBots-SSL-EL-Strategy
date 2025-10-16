#!/usr/bin/env python3.11
"""
Quick validation test for the refactored wall system.
Tests the unified parameter calculation without requiring GrSim.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from Behaviour_tree.helpers import defense_helpers
from Behaviour_tree.core.World_State import World_State
from utils.pose2D import Pose2D
import py_trees

def test_unified_calculation():
    """Test the unified wall parameter calculation."""
    print("🧪 Testing Unified Wall Parameter Calculation")
    print("=" * 50)
    
    # Initialize World State (creates singleton)
    ws = World_State()
    
    # Test main wall calculation
    print("\n1. Testing Main Wall Calculation:")
    try:
        main_params = defense_helpers.calculate_unified_wall_parameters(
            robot_id=1, wall_type="main"
        )
        if main_params:
            print(f"   ✓ Main wall parameters calculated successfully")
            print(f"   ✓ Parameters: {list(main_params.keys())}")
            print(f"   ✓ Wall size: {main_params.get('n_wall', 'N/A')}")
        else:
            print(f"   ❌ Main wall calculation returned empty")
    except Exception as e:
        print(f"   ❌ Main wall calculation failed: {e}")
    
    # Test auxiliary wall calculation
    print("\n2. Testing Auxiliary Wall Calculation:")
    try:
        aux_params = defense_helpers.calculate_unified_wall_parameters(
            robot_id=3, wall_type="aux"
        )
        if aux_params:
            print(f"   ✓ Auxiliary wall parameters calculated successfully")
            print(f"   ✓ Parameters: {list(aux_params.keys())}")
            print(f"   ✓ Wall size: {aux_params.get('n_wall', 'N/A')}")
        else:
            print(f"   ❌ Auxiliary wall calculation returned empty")
    except Exception as e:
        print(f"   ❌ Auxiliary wall calculation failed: {e}")

def test_geometric_helpers():
    """Test geometric helper functions."""
    print("\n🔍 Testing Geometric Helper Functions")
    print("=" * 50)
    
    # Test basic geometric functions
    test_cases = [
        ("calculate_angle_bisector", [Pose2D(0, 0, 0), Pose2D(100, 0, 0), Pose2D(0, 100, 0)]),
        ("interpolate_position_along_line", [Pose2D(0, 0, 0), Pose2D(100, 100, 0), 50.0]),
        ("project_point_onto_line", [Pose2D(50, 50, 0), Pose2D(0, 0, 0), Pose2D(100, 0, 0)]),
    ]
    
    for func_name, args in test_cases:
        try:
            func = getattr(defense_helpers, func_name)
            result = func(*args)
            print(f"   ✓ {func_name}: {type(result).__name__}")
        except Exception as e:
            print(f"   ❌ {func_name}: {e}")

def test_wall_behavior_trees():
    """Test that wall behavior trees can be created."""
    print("\n🌳 Testing Wall Behavior Tree Creation")
    print("=" * 50)
    
    try:
        from Behaviour_tree.robot.bob import Bob
        from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import get_wall_subtree
        from Behaviour_tree.commom_behaviours.sub_trees.aux_wall_subtree import get_aux_wall_subtree
        
        # Test main wall tree creation
        bob1 = Bob(1)
        main_tree = get_wall_subtree(bob1)
        print(f"   ✓ Main wall tree created: {type(main_tree).__name__}")
        
        # Test auxiliary wall tree creation
        bob2 = Bob(2) 
        aux_tree = get_aux_wall_subtree(bob2)
        print(f"   ✓ Auxiliary wall tree created: {type(aux_tree).__name__}")
        
    except Exception as e:
        print(f"   ❌ Behavior tree creation failed: {e}")

def main():
    """Run all validation tests."""
    print("🤖 UTBots Wall System - Validation Test")
    print("This test validates the refactored wall system without GrSim")
    print()
    
    test_unified_calculation()
    test_geometric_helpers() 
    test_wall_behavior_trees()
    
    print("\n" + "=" * 50)
    print("✅ Validation test completed!")
    print("\nIf all tests passed, the system is ready for GrSim testing.")
    print("Run 'python3 test_wall_system.py' with GrSim running for full testing.")

if __name__ == "__main__":
    main()
