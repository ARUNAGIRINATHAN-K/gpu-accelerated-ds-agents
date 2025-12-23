"""Debug test for EDA visualizations - writes output to file."""

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
    'category': np.random.choice(['A', 'B', 'C'], 100),
})

# Run EDA
eda = EDAAgent()
_, report = eda.run(df)

# Write to file
output_file = Path(__file__).parent / "eda_test_output.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("EDA REPORT DEBUG OUTPUT\n")
    f.write("="*60 + "\n\n")
    
    f.write("📊 Summary:\n")
    f.write(report['summary'] + "\n\n")
    
    f.write(f"💡 Insights ({len(report['insights'])}):\n")
    for i, insight in enumerate(report['insights'], 1):
        f.write(f"{i}. {insight}\n")
    f.write("\n")
    
    f.write(f"📈 Visualizations ({len(report['visualizations'])}):\n")
    for i, viz in enumerate(report['visualizations'], 1):
        f.write(f"{i}. {viz}\n")
    f.write("\n")
    
    f.write(f"📋 Recommendations ({len(report['recommendations'])}):\n")
    for i, rec in enumerate(report['recommendations'], 1):
        f.write(f"{i}. {rec}\n")
    f.write("\n")
    
    f.write("="*60 + "\n")
    f.write("Full report dict:\n")
    f.write(str(report) + "\n")

print(f"✅ Output written to: {output_file}")
print(f"Visualizations count: {len(report['visualizations'])}")
print(f"Visualizations: {report['visualizations']}")
