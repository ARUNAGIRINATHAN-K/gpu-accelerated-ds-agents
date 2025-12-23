"""
Example: Basic EDA workflow with GPU acceleration

This script demonstrates how to use the EDA Agent for exploratory data analysis.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gpu_pipeline import load_csv, gpu_utils
from agents import EDAAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run basic EDA workflow."""
    
    # Check GPU availability
    logger.info("Checking GPU availability...")
    gpu_info = gpu_utils.get_device_info()
    logger.info(f"Device: {gpu_info['device']}")
    
    if gpu_info['gpu_available']:
        logger.info(f"GPU: {gpu_info['device_name']}")
        logger.info(f"Total Memory: {gpu_info['memory_total_gb']:.2f} GB")
    
    # Load sample data (replace with your CSV file)
    logger.info("Loading data...")
    
    # Example: Create sample data if no file provided
    try:
        df = load_csv("examples/datasets/sample_data.csv", use_gpu=True)
    except FileNotFoundError:
        logger.warning("Sample data not found, creating synthetic data...")
        import pandas as pd
        import numpy as np
        
        # Create synthetic dataset
        np.random.seed(42)
        df = pd.DataFrame({
            'feature1': np.random.randn(10000),
            'feature2': np.random.randn(10000),
            'feature3': np.random.randint(0, 100, 10000),
            'feature4': np.random.choice(['A', 'B', 'C'], 10000),
            'target': np.random.randint(0, 2, 10000)
        })
        
        # Add some missing values
        df.loc[np.random.choice(df.index, 500), 'feature1'] = np.nan
        df.loc[np.random.choice(df.index, 300), 'feature2'] = np.nan
        
        logger.info(f"Created synthetic dataset: {df.shape}")
    
    # Initialize EDA Agent
    logger.info("Initializing EDA Agent...")
    eda_agent = EDAAgent(config={
        'outlier_threshold': 3.0,
        'max_correlations': 50,
    })
    
    # Run EDA
    logger.info("Running EDA analysis...")
    processed_data, report = eda_agent.run(df)
    
    # Print results
    print("\n" + "="*80)
    print("EDA REPORT")
    print("="*80)
    print(report['summary'])
    print("\n" + "-"*80)
    print("INSIGHTS:")
    for i, insight in enumerate(report['insights'], 1):
        print(f"{i}. {insight}")
    
    print("\n" + "-"*80)
    print("RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "-"*80)
    print("SUGGESTED VISUALIZATIONS:")
    for i, viz in enumerate(report['visualizations'], 1):
        print(f"{i}. {viz}")
    
    print("\n" + "="*80)
    
    # Print metadata
    metadata = eda_agent.get_metadata()
    print(f"\nExecution time: {metadata['duration_seconds']:.2f} seconds")
    print(f"Status: {metadata['status']}")
    
    # GPU stats
    if gpu_info['gpu_available']:
        logger.info(gpu_utils.monitor_gpu_usage())


if __name__ == "__main__":
    main()
