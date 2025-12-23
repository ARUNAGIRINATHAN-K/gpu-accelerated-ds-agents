"""Data loader for CSV files with GPU acceleration using cuDF."""

import logging
from pathlib import Path
from typing import Union, Optional, List, Any
import warnings

logger = logging.getLogger(__name__)


class DataLoader:
    """Load CSV data with GPU acceleration when available."""
    
    def __init__(self, use_gpu: bool = True):
        """
        Initialize DataLoader.
        
        Args:
            use_gpu: Whether to use GPU acceleration (cuDF) if available
        """
        self.use_gpu = use_gpu
        self.cudf_available = False
        
        if use_gpu:
            try:
                import cudf
                self.cudf_available = True
                logger.info("cuDF available - using GPU acceleration")
            except ImportError:
                logger.warning("cuDF not available - falling back to pandas")
    
    def load_csv(self,
                 filepath: Union[str, Path],
                 **kwargs) -> Any:
        """
        Load CSV file into DataFrame (cuDF if GPU available, else pandas).
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional arguments passed to read_csv
        
        Returns:
            DataFrame (cuDF or pandas)
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        logger.info(f"Loading CSV: {filepath}")
        
        try:
            if self.cudf_available and self.use_gpu:
                import cudf
                df = cudf.read_csv(filepath, **kwargs)
                logger.info(f"Loaded {len(df):,} rows × {len(df.columns)} columns (GPU)")
            else:
                import pandas as pd
                df = pd.read_csv(filepath, **kwargs)
                logger.info(f"Loaded {len(df):,} rows × {len(df.columns)} columns (CPU)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_csv_chunked(self,
                        filepath: Union[str, Path],
                        chunksize: int = 100000,
                        **kwargs) -> Any:
        """
        Load large CSV file in chunks.
        
        Args:
            filepath: Path to CSV file
            chunksize: Number of rows per chunk
            **kwargs: Additional arguments passed to read_csv
        
        Yields:
            DataFrame chunks
        """
        filepath = Path(filepath)
        logger.info(f"Loading CSV in chunks: {filepath} (chunksize={chunksize:,})")
        
        try:
            if self.cudf_available and self.use_gpu:
                import cudf
                # cuDF doesn't have native chunking, so we use pandas then convert
                import pandas as pd
                for chunk in pd.read_csv(filepath, chunksize=chunksize, **kwargs):
                    yield cudf.from_pandas(chunk)
            else:
                import pandas as pd
                for chunk in pd.read_csv(filepath, chunksize=chunksize, **kwargs):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error loading CSV chunks: {e}")
            raise
    
    def to_pandas(self, df: Any) -> Any:
        """
        Convert DataFrame to pandas (if it's cuDF).
        
        Args:
            df: DataFrame (cuDF or pandas)
        
        Returns:
            pandas DataFrame
        """
        if self.cudf_available:
            try:
                import cudf
                if isinstance(df, cudf.DataFrame):
                    return df.to_pandas()
            except Exception as e:
                logger.warning(f"Error converting to pandas: {e}")
        
        return df
    
    def to_cudf(self, df: Any) -> Any:
        """
        Convert DataFrame to cuDF (if available).
        
        Args:
            df: pandas DataFrame
        
        Returns:
            cuDF DataFrame (or original if cuDF unavailable)
        """
        if not self.cudf_available:
            return df
        
        try:
            import cudf
            import pandas as pd
            
            if isinstance(df, pd.DataFrame):
                return cudf.from_pandas(df)
            return df
            
        except Exception as e:
            logger.warning(f"Error converting to cuDF: {e}")
            return df
    
    def get_dataframe_info(self, df: Any) -> dict:
        """
        Get information about the DataFrame.
        
        Args:
            df: DataFrame (cuDF or pandas)
        
        Returns:
            Dictionary with DataFrame info
        """
        info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1e6,
            "is_gpu": False,
        }
        
        if self.cudf_available:
            try:
                import cudf
                info["is_gpu"] = isinstance(df, cudf.DataFrame)
            except:
                pass
        
        # Missing values
        info["missing_values"] = df.isnull().sum().to_dict()
        info["total_missing"] = sum(info["missing_values"].values())
        
        return info
    
    def save_csv(self,
                 df: Any,
                 filepath: Union[str, Path],
                 **kwargs):
        """
        Save DataFrame to CSV.
        
        Args:
            df: DataFrame (cuDF or pandas)
            filepath: Output file path
            **kwargs: Additional arguments passed to to_csv
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving CSV: {filepath}")
        
        try:
            df.to_csv(filepath, index=False, **kwargs)
            logger.info(f"Saved {len(df):,} rows to {filepath}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise


# Convenience function
def load_csv(filepath: Union[str, Path], 
             use_gpu: bool = True,
             **kwargs) -> Any:
    """
    Load CSV file with optional GPU acceleration.
    
    Args:
        filepath: Path to CSV file
        use_gpu: Whether to use GPU acceleration
        **kwargs: Additional arguments passed to read_csv
    
    Returns:
        DataFrame (cuDF or pandas)
    """
    loader = DataLoader(use_gpu=use_gpu)
    return loader.load_csv(filepath, **kwargs)
