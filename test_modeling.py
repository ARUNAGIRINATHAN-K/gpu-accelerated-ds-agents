"""Test Modeling Agent"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from agents import ModelingAgent

print("Testing Modeling Agent...")

# Create simple classification dataset
np.random.seed(42)
df = pd.DataFrame({
    'feature1': np.random.rand(500),
    'feature2': np.random.rand(500),
    'feature3': np.random.randint(0, 10, 500),
    'target': np.random.randint(0, 2, 500),
})

print(f"Dataset shape: {df.shape}")
print(f"Target distribution: {df['target'].value_counts().to_dict()}")

# Test agent
modeling_agent = ModelingAgent(config={
    'algorithms': ['xgboost_gpu', 'logistic_regression'],
    'test_size': 0.2,
})

try:
    results, report = modeling_agent.run(df, target_column='target')
    print(f"\n✅ Success!")
    print(f"Models trained: {len(results['models'])}")
    print(f"Best model: {results['best_model']}")
    print(f"Time: {modeling_agent.metadata['duration_seconds']:.2f}s")
    
    # Print metrics
    print("\nModel Performance:")
    for algo, result in results['models'].items():
        if 'error' not in result:
            metrics = result['metrics']
            print(f"  {algo}: Accuracy={metrics['accuracy']:.4f}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
