"""GPU-accelerated data preprocessing using cuDF and cuML."""

import logging
from typing import Any, List, Optional, Dict, Union
import warnings

logger = logging.getLogger(__name__)


class Preprocessor:
    """GPU-accelerated data preprocessing."""
    
    def __init__(self, use_gpu: bool = True):
        """
        Initialize Preprocessor.
        
        Args:
            use_gpu: Whether to use GPU acceleration
        """
        self.use_gpu = use_gpu
        self.cudf_available = False
        self.cuml_available = False
        
        if use_gpu:
            try:
                import cudf
                self.cudf_available = True
            except ImportError:
                logger.warning("cuDF not available")
            
            try:
                import cuml
                self.cuml_available = True
            except ImportError:
                logger.warning("cuML not available")
    
    def handle_missing_values(self,
                             df: Any,
                             strategy: str = "mean",
                             columns: Optional[List[str]] = None) -> Any:
        """
        Handle missing values in DataFrame.
        
        Args:
            df: DataFrame (cuDF or pandas)
            strategy: Strategy for imputation (mean, median, mode, drop, forward_fill)
            columns: Specific columns to process (None = all numeric columns)
        
        Returns:
            DataFrame with missing values handled
        """
        logger.info(f"Handling missing values with strategy: {strategy}")
        
        if columns is None:
            # Get numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            columns = numeric_cols
        
        if strategy == "drop":
            df = df.dropna(subset=columns)
        elif strategy == "mean":
            for col in columns:
                if col in df.columns:
                    df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median":
            for col in columns:
                if col in df.columns:
                    df[col] = df[col].fillna(df[col].median())
        elif strategy == "mode":
            for col in columns:
                if col in df.columns:
                    mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 0
                    df[col] = df[col].fillna(mode_val)
        elif strategy == "forward_fill":
            df[columns] = df[columns].fillna(method='ffill')
        
        logger.info(f"Missing values handled for {len(columns)} columns")
        return df
    
    def encode_categorical(self,
                          df: Any,
                          columns: Optional[List[str]] = None,
                          method: str = "label") -> tuple:
        """
        Encode categorical variables.
        
        Args:
            df: DataFrame
            columns: Categorical columns to encode (None = auto-detect)
            method: Encoding method (label, onehot)
        
        Returns:
            Tuple of (encoded_df, encoding_mappings)
        """
        logger.info(f"Encoding categorical variables with method: {method}")
        
        if columns is None:
            # Auto-detect categorical columns
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        encodings = {}
        
        if method == "label":
            for col in columns:
                if col in df.columns:
                    # Create mapping
                    unique_vals = df[col].unique()
                    mapping = {val: idx for idx, val in enumerate(unique_vals)}
                    encodings[col] = mapping
                    
                    # Apply encoding
                    df[col] = df[col].map(mapping)
        
        elif method == "onehot":
            if self.cudf_available:
                try:
                    import cudf
                    if isinstance(df, cudf.DataFrame):
                        df = cudf.get_dummies(df, columns=columns, prefix=columns)
                    else:
                        import pandas as pd
                        df = pd.get_dummies(df, columns=columns, prefix=columns)
                except:
                    import pandas as pd
                    df = pd.get_dummies(df, columns=columns, prefix=columns)
            else:
                import pandas as pd
                df = pd.get_dummies(df, columns=columns, prefix=columns)
        
        logger.info(f"Encoded {len(columns)} categorical columns")
        return df, encodings
    
    def scale_features(self,
                      df: Any,
                      columns: Optional[List[str]] = None,
                      method: str = "standard") -> tuple:
        """
        Scale numerical features.
        
        Args:
            df: DataFrame
            columns: Columns to scale (None = all numeric)
            method: Scaling method (standard, minmax, robust)
        
        Returns:
            Tuple of (scaled_df, scaler)
        """
        logger.info(f"Scaling features with method: {method}")
        
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        
        scaler = None
        
        try:
            if self.cuml_available and self.use_gpu:
                from cuml.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
                
                if method == "standard":
                    scaler = StandardScaler()
                elif method == "minmax":
                    scaler = MinMaxScaler()
                elif method == "robust":
                    scaler = RobustScaler()
                
                df[columns] = scaler.fit_transform(df[columns])
                logger.info(f"Scaled {len(columns)} columns (GPU)")
            
            else:
                from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
                
                if method == "standard":
                    scaler = StandardScaler()
                elif method == "minmax":
                    scaler = MinMaxScaler()
                elif method == "robust":
                    scaler = RobustScaler()
                
                df[columns] = scaler.fit_transform(df[columns])
                logger.info(f"Scaled {len(columns)} columns (CPU)")
        
        except Exception as e:
            logger.error(f"Error scaling features: {e}")
            raise
        
        return df, scaler
    
    def detect_outliers(self,
                       df: Any,
                       columns: Optional[List[str]] = None,
                       method: str = "iqr",
                       threshold: float = 3.0) -> Dict[str, Any]:
        """
        Detect outliers in numerical columns.
        
        Args:
            df: DataFrame
            columns: Columns to check (None = all numeric)
            method: Detection method (iqr, zscore)
            threshold: Threshold for outlier detection
        
        Returns:
            Dictionary with outlier information
        """
        logger.info(f"Detecting outliers with method: {method}")
        
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        
        outliers = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
            elif method == "zscore":
                mean = df[col].mean()
                std = df[col].std()
                z_scores = ((df[col] - mean) / std).abs()
                outlier_mask = z_scores > threshold
                outlier_count = outlier_mask.sum()
            
            outliers[col] = {
                "count": int(outlier_count),
                "percentage": float(outlier_count / len(df) * 100),
            }
        
        total_outliers = sum(info["count"] for info in outliers.values())
        logger.info(f"Detected {total_outliers} outliers across {len(columns)} columns")
        
        return outliers
    
    def remove_outliers(self,
                       df: Any,
                       columns: Optional[List[str]] = None,
                       method: str = "iqr",
                       threshold: float = 3.0) -> Any:
        """
        Remove outliers from DataFrame.
        
        Args:
            df: DataFrame
            columns: Columns to process (None = all numeric)
            method: Detection method (iqr, zscore)
            threshold: Threshold for outlier detection
        
        Returns:
            DataFrame with outliers removed
        """
        logger.info(f"Removing outliers with method: {method}, threshold: {threshold}")
        
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        
        original_len = len(df)
        mask = None
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                col_mask = (df[col] >= lower_bound) & (df[col] <= upper_bound)
                
            elif method == "zscore":
                mean = df[col].mean()
                std = df[col].std()
                z_scores = ((df[col] - mean) / std).abs()
                col_mask = z_scores <= threshold
            
            mask = col_mask if mask is None else mask & col_mask
        
        if mask is not None:
            df = df[mask]
        
        removed = original_len - len(df)
        logger.info(f"Removed {removed} rows ({removed/original_len*100:.2f}%)")
        
        return df
    
    def preprocess_pipeline(self,
                           df: Any,
                           missing_strategy: str = "mean",
                           encode_categoricals: bool = True,
                           scale_method: str = "standard",
                           remove_outliers: bool = False,
                           outlier_threshold: float = 3.0) -> tuple:
        """
        Run complete preprocessing pipeline.
        
        Args:
            df: Input DataFrame
            missing_strategy: Strategy for missing values
            encode_categoricals: Whether to encode categorical variables
            scale_method: Scaling method for numerical features
            remove_outliers: Whether to remove outliers
            outlier_threshold: Threshold for outlier removal
        
        Returns:
            Tuple of (processed_df, metadata)
        """
        logger.info("Running preprocessing pipeline")
        
        metadata = {
            "original_shape": df.shape,
            "encodings": {},
            "scaler": None,
        }
        
        # Handle missing values
        df = self.handle_missing_values(df, strategy=missing_strategy)
        
        # Remove outliers if requested
        if remove_outliers:
            df = self.remove_outliers(df, threshold=outlier_threshold)
        
        # Encode categorical variables
        if encode_categoricals:
            df, encodings = self.encode_categorical(df, method="label")
            metadata["encodings"] = encodings
        
        # Scale numerical features
        df, scaler = self.scale_features(df, method=scale_method)
        metadata["scaler"] = scaler
        
        metadata["final_shape"] = df.shape
        
        logger.info(f"Preprocessing complete: {metadata['original_shape']} → {metadata['final_shape']}")
        
        return df, metadata
