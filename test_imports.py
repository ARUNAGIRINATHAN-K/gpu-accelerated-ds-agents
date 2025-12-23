"""Simple test to verify imports work correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("Testing imports...")

try:
    from gpu_pipeline import load_csv, gpu_utils, DataLoader, Preprocessor
    print("✅ gpu_pipeline imports successful")
except ImportError as e:
    print(f"❌ gpu_pipeline import failed: {e}")
    sys.exit(1)

try:
    from agents import BaseAgent, EDAAgent
    print("✅ agents imports successful")
except ImportError as e:
    print(f"❌ agents import failed: {e}")
    sys.exit(1)

# Test GPU utils
print("\nGPU Information:")
print(f"Device: {gpu_utils.device}")
print(f"GPU Available: {gpu_utils.gpu_available}")

# Test creating agents
print("\nTesting agent creation:")
try:
    eda = EDAAgent()
    print(f"✅ EDA Agent created: {eda.name}")
except Exception as e:
    print(f"❌ EDA Agent creation failed: {e}")
    sys.exit(1)

print("\n✅ All tests passed!")
