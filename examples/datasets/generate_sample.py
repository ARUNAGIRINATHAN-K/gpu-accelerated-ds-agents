"""Generate sample dataset for testing."""

import pandas as pd
import numpy as np
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

# Generate sample customer churn dataset
n_samples = 1000

data = {
    'customer_id': range(1, n_samples + 1),
    'age': np.random.randint(18, 80, n_samples),
    'tenure_months': np.random.randint(0, 121, n_samples),
    'monthly_charges': np.random.uniform(20, 200, n_samples).round(2),
    'total_charges': np.random.uniform(100, 10000, n_samples).round(2),
    'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples),
    'payment_method': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], n_samples),
    'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples),
    'tech_support': np.random.choice(['Yes', 'No'], n_samples),
    'churn': np.random.randint(0, 2, n_samples)
}

df = pd.DataFrame(data)

# Add some missing values
df.loc[np.random.choice(df.index, 50), 'monthly_charges'] = np.nan
df.loc[np.random.choice(df.index, 30), 'total_charges'] = np.nan

# Save to CSV
output_path = Path(__file__).parent / "sample_churn.csv"
df.to_csv(output_path, index=False)

print(f"✅ Sample dataset created: {output_path}")
print(f"   Shape: {df.shape}")
print(f"   Missing values: {df.isnull().sum().sum()}")
