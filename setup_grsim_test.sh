#!/bin/bash
# setup_grsim_test.sh
# Setup script for testing the refactored wall system with GrSim

echo "🤖 UTBots Wall System - GrSim Test Setup"
echo "========================================"

# Check if GrSim is installed
if ! command -v grSim &> /dev/null; then
    echo "⚠ GrSim not found in PATH"
    echo "Please install GrSim first:"
    echo "  sudo apt install grsim"
    echo "  Or build from source: https://github.com/RoboCup-SSL/grSim"
    exit 1
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."

python3.11 -c "import py_trees" 2>/dev/null || {
    echo "⚠ py_trees not installed. Installing..."
    pip3 install py-trees
}

python3.11 -c "import protobuf" 2>/dev/null || {
    echo "⚠ protobuf not installed. Installing..."
    pip3 install protobuf
}

# Create a simple GrSim configuration for testing
echo "⚙️ Creating test configuration..."

cat > grsim_test_config.txt << EOF
# GrSim Test Configuration for Wall System Testing

Recommended GrSim setup:
1. Field: SSL Division A (12m x 9m)
2. Team colors: Blue (your team), Yellow (opponents)
3. Number of robots: 6 per team

Test scenarios to try:
1. Place 1-2 yellow robots near your goal
2. Position ball to create threatening angles
3. Run the wall test script to see adaptive behavior

The test will show:
- Main wall: Single robot using bisector positioning
- Auxiliary wall: Multiple robots on optimal side
- Unified parameter calculation for both types
EOF

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start GrSim: grSim"
echo "2. Load a field and place some robots"
echo "3. Run the test: python3.11 test_wall_system.py"
echo ""
echo "💡 Tips:"
echo "- Move opponent robots around to test threat detection"
echo "- Change ball position to see wall adaptation"
echo "- Watch console output for detailed behavior analysis"
echo ""
echo "📄 See grsim_test_config.txt for detailed setup instructions"
