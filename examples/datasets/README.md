# Sample CSV Dataset for Testing

This file contains a sample dataset for testing the GPU-accelerated data science agents.

## Dataset: Customer Churn Prediction

**Description**: Synthetic customer data for predicting churn

**Features**:
- `customer_id`: Unique customer identifier
- `age`: Customer age (18-80)
- `tenure_months`: Months as customer (0-120)
- `monthly_charges`: Monthly bill amount ($20-$200)
- `total_charges`: Total amount charged
- `contract_type`: Month-to-month, One year, Two year
- `payment_method`: Electronic check, Mailed check, Bank transfer, Credit card
- `internet_service`: DSL, Fiber optic, No
- `tech_support`: Yes, No
- `churn`: Target variable (0 = No, 1 = Yes)

**Size**: 1,000 rows × 10 columns

**Usage**:
```python
import pandas as pd
df = pd.read_csv("examples/datasets/sample_churn.csv")
```

Or upload directly in the Streamlit dashboard.
