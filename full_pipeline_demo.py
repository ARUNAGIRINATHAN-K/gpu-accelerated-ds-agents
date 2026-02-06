"""
This script demonstrates the full autonomous data science pipeline:
1. EDA Agent
2. Modeling Agent
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np
from agents import EDAAgent, ModelingAgent

print("="*70)
print("🚀 GPU-Accelerated Autonomous Data Science Pipeline")
print("="*70)

# 1. Create sample dataset
print("\n📊 Step 1: Creating sample dataset...")
np.random.seed(42)
n_samples = 5000

df = pd.DataFrame({
    'age': np.random.randint(18, 80, n_samples),
    'income': np.random.normal(50000, 15000, n_samples),
    'credit_score': np.random.randint(300, 850, n_samples),
    'years_employed': np.random.randint(0, 40, n_samples),
    'debt_ratio': np.random.rand(n_samples),
    'approved': np.random.randint(0, 2, n_samples),  # Target variable
})

# Add some missing values
df.loc[np.random.choice(df.index, 200), 'income'] = np.nan
df.loc[np.random.choice(df.index, 100), 'credit_score'] = np.nan

print(f"   ✓ Dataset created: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"   ✓ Target: 'approved' (binary classification)")

# 2. EDA Agent
print("\n🔍 Step 2: Running EDA Agent...")
eda_agent = EDAAgent()
df_eda, eda_report = eda_agent.run(df)

print(f"   ✓ EDA completed in {eda_agent.metadata['duration_seconds']:.2f}s")
print(f"   ✓ Missing values: {eda_report['summary'].split('Missing values: ')[1].split(' across')[0]}")
print(f"   ✓ Insights generated: {len(eda_report['insights'])}")

# 3. Preprocessing (handle missing values)
print("\n🛠️  Step 3: Preprocessing data...")
from gpu_pipeline import Preprocessor

preprocessor = Preprocessor(use_gpu=False)  # Use CPU for local demo
df_clean, metadata = preprocessor.preprocess_pipeline(
    df,
    missing_strategy='mean',
    encode_categoricals=False,
    scale_method='standard',
    remove_outliers=False
)

print(f"   ✓ Preprocessing complete")
print(f"   ✓ Shape: {metadata['original_shape']} → {metadata['final_shape']}")

# 4. Modeling Agent
print("\n🤖 Step 4: Running Modeling Agent...")
modeling_agent = ModelingAgent(config={
    'algorithms': ['xgboost_gpu', 'random_forest_gpu', 'logistic_regression'],
    'test_size': 0.2,
    'random_state': 42,
})

model_results, model_report = modeling_agent.run(
    df_clean,
    target_column='approved'
)

print(f"   ✓ Model training completed in {modeling_agent.metadata['duration_seconds']:.2f}s")
print(f"   ✓ Models trained: {len(model_results['models'])}")
print(f"   ✓ Best model: {model_results['best_model']}")

# 6. Results Summary
print("\n" + "="*70)
print("📈 PIPELINE RESULTS")
print("="*70)

print("\n🔍 EDA Insights:")
for i, insight in enumerate(eda_report['insights'][:3], 1):
    print(f"   {i}. {insight}")



print("\n🤖 Model Performance:")
models = model_results['models']
for algo, result in models.items():
    if 'error' not in result:
        metrics = result['metrics']
        if 'accuracy' in metrics:
            print(f"   • {algo}: Accuracy={metrics['accuracy']:.4f}, F1={metrics['f1']:.4f}")
        else:
            print(f"   • {algo}: R²={metrics['r2']:.4f}, RMSE={metrics['rmse']:.4f}")

print("\n🏆 Best Model: " + model_results['best_model'])

# 6. Total Time
total_time = (
    eda_agent.metadata['duration_seconds'] +
    modeling_agent.metadata['duration_seconds']
)

print("\n" + "="*70)
print(f"✅ Complete pipeline executed in {total_time:.2f} seconds")
print("="*70)

print("\n💡 Next Steps:")
print("   1. Deploy best model to production")
print("   2. Set up monitoring and retraining pipeline")
print("   3. Run on Google Colab with GPU for 10-50× speedup")
print("   4. Try with your own CSV datasets")
