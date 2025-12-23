"""Test EDA agent to verify visualizations are generated."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from agents import EDAAgent

# Create sample data
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.randint(18, 80, 100),
    'income': np.random.rand(100) * 100000,
    'score': np.random.rand(100) * 100,
})

# Run EDA
eda = EDAAgent()
_, report = eda.run(df)

print("="*60)
print("EDA REPORT TEST")
print("="*60)

print("\n📊 Summary:")
print(report['summary'])

print("\n💡 Insights:")
print(f"Count: {len(report['insights'])}")
for i, insight in enumerate(report['insights'], 1):
    print(f"{i}. {insight}")

print("\n📈 Visualizations:")
print(f"Count: {len(report['visualizations'])}")
for i, viz in enumerate(report['visualizations'], 1):
    print(f"{i}. {viz}")

print("\n📋 Recommendations:")
print(f"Count: {len(report['recommendations'])}")
for i, rec in enumerate(report['recommendations'], 1):
    print(f"{i}. {rec}")

print("\n" + "="*60)
print("✅ Test complete!")
