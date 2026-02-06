"""
This script demonstrates the EDA agent with minimal output.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from agents import EDAAgent

print("="*60)
print("GPU-Accelerated EDA Agent Demo")
print("="*60)

# Create sample data
print("\n1. Creating sample dataset...")
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.randint(18, 80, 1000),
    'income': np.random.normal(50000, 15000, 1000),
    'score': np.random.rand(1000) * 100,
    'category': np.random.choice(['A', 'B', 'C'], 1000),
})

# Add missing values
df.loc[np.random.choice(df.index, 50), 'income'] = np.nan

print(f"   Dataset shape: {df.shape}")
print(f"   Columns: {list(df.columns)}")

# Run EDA
print("\n2. Running EDA Agent...")
eda_agent = EDAAgent()
_, report = eda_agent.run(df)

# Print summary
print("\n3. Results:")
print("-"*60)
print(report['summary'])

print("\n4. Key Insights:")
for insight in report['insights'][:3]:  # Show first 3
    print(f"   • {insight}")

print("\n5. Recommendations:")
for rec in report['recommendations'][:3]:  # Show first 3
    print(f"   • {rec}")

print("\n" + "="*60)
print(f"✅ Analysis completed in {eda_agent.metadata['duration_seconds']:.2f}s")
print("="*60)
