"""Exploratory Data Analysis (EDA) Agent."""

import logging
from typing import Any, Dict, List, Optional
import warnings

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EDAAgent(BaseAgent):
    """Autonomous agent for exploratory data analysis."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize EDA Agent."""
        super().__init__(name="EDA Agent", config=config)
        
        # Check for GPU availability
        self.use_gpu = True
        try:
            import cudf
            self.cudf_available = True
            logger.info("EDA Agent: cuDF available (GPU mode)")
        except ImportError:
            self.cudf_available = False
            self.use_gpu = False
            logger.info("EDA Agent: Using pandas (CPU mode)")
    
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Perform exploratory data analysis.
        
        Args:
            data: Input DataFrame (cuDF or pandas)
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with EDA results
        """
        logger.info("EDA Agent: Starting analysis")
        
        analysis = {
            "basic_info": self._get_basic_info(data),
            "statistical_summary": self._get_statistical_summary(data),
            "missing_values": self._analyze_missing_values(data),
            "correlations": self._compute_correlations(data),
            "distributions": self._analyze_distributions(data),
            "outliers": self._detect_outliers(data),
        }
        
        logger.info("EDA Agent: Analysis complete")
        return analysis
    
    def execute(self, data: Any, **kwargs) -> Any:
        """
        Execute EDA tasks (returns original data, EDA is non-destructive).
        
        Args:
            data: Input DataFrame
            **kwargs: Additional arguments
        
        Returns:
            Original DataFrame (unchanged)
        """
        # EDA doesn't modify data, just analyzes it
        return data
    
    def report(self) -> Dict[str, Any]:
        """
        Generate EDA report.
        
        Returns:
            Dictionary with report data
        """
        analysis = self.results.get("analysis", {})
        
        report = {
            "agent": self.name,
            "metadata": self.get_metadata(),
            "summary": self._generate_summary(analysis),
            "insights": self._generate_insights(analysis),
            "visualizations": self._suggest_visualizations(analysis),
        }
        
        return report
    
    def _get_basic_info(self, df: Any) -> Dict[str, Any]:
        """Get basic DataFrame information."""
        info = {
            "shape": df.shape,
            "num_rows": df.shape[0],
            "num_columns": df.shape[1],
            "column_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1e6,
        }
        
        # Categorize columns by type
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        info["numeric_columns"] = numeric_cols
        info["categorical_columns"] = categorical_cols
        info["num_numeric"] = len(numeric_cols)
        info["num_categorical"] = len(categorical_cols)
        
        return info
    
    def _get_statistical_summary(self, df: Any) -> Dict[str, Any]:
        """Get statistical summary of numerical columns."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_cols:
            return {}
        
        summary = {}
        
        for col in numeric_cols:
            try:
                summary[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "q25": float(df[col].quantile(0.25)),
                    "q75": float(df[col].quantile(0.75)),
                    "skew": float(df[col].skew()) if hasattr(df[col], 'skew') else None,
                    "kurtosis": float(df[col].kurtosis()) if hasattr(df[col], 'kurtosis') else None,
                }
            except Exception as e:
                logger.warning(f"Error computing stats for {col}: {e}")
                summary[col] = {"error": str(e)}
        
        return summary
    
    def _analyze_missing_values(self, df: Any) -> Dict[str, Any]:
        """Analyze missing values."""
        missing = df.isnull().sum()
        total_rows = len(df)
        
        missing_info = {}
        
        for col in df.columns:
            missing_count = int(missing[col])
            if missing_count > 0:
                missing_info[col] = {
                    "count": missing_count,
                    "percentage": float(missing_count / total_rows * 100),
                }
        
        total_missing = sum(info["count"] for info in missing_info.values())
        
        return {
            "columns_with_missing": missing_info,
            "total_missing_values": total_missing,
            "columns_affected": len(missing_info),
        }
    
    def _compute_correlations(self, df: Any) -> Dict[str, Any]:
        """Compute correlation matrix for numerical columns."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {}
        
        try:
            corr_matrix = df[numeric_cols].corr()
            
            # Find high correlations
            high_corr = []
            max_corr = self.config.get("max_correlations", 50)
            
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j:  # Avoid duplicates
                        corr_val = float(corr_matrix.iloc[i, j])
                        if abs(corr_val) > 0.5:  # Threshold for "high" correlation
                            high_corr.append({
                                "column1": col1,
                                "column2": col2,
                                "correlation": corr_val,
                            })
            
            # Sort by absolute correlation
            high_corr.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            high_corr = high_corr[:max_corr]
            
            return {
                "correlation_matrix": corr_matrix.to_dict(),
                "high_correlations": high_corr,
                "num_high_correlations": len(high_corr),
            }
            
        except Exception as e:
            logger.warning(f"Error computing correlations: {e}")
            return {"error": str(e)}
    
    def _analyze_distributions(self, df: Any) -> Dict[str, Any]:
        """Analyze distributions of numerical columns."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        distributions = {}
        
        for col in numeric_cols:
            try:
                unique_count = int(df[col].nunique())
                value_counts = df[col].value_counts().head(10)
                
                distributions[col] = {
                    "unique_values": unique_count,
                    "is_constant": unique_count == 1,
                    "is_binary": unique_count == 2,
                    "top_values": value_counts.to_dict() if unique_count <= 20 else {},
                }
            except Exception as e:
                logger.warning(f"Error analyzing distribution for {col}: {e}")
        
        return distributions
    
    def _detect_outliers(self, df: Any) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        threshold = self.config.get("outlier_threshold", 3.0)
        
        outliers = {}
        
        for col in numeric_cols:
            try:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_count = int(outlier_mask.sum())
                
                if outlier_count > 0:
                    outliers[col] = {
                        "count": outlier_count,
                        "percentage": float(outlier_count / len(df) * 100),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound),
                    }
            except Exception as e:
                logger.warning(f"Error detecting outliers for {col}: {e}")
        
        total_outliers = sum(info["count"] for info in outliers.values())
        
        return {
            "columns_with_outliers": outliers,
            "total_outliers": total_outliers,
            "threshold": threshold,
        }
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate text summary of EDA results."""
        basic = analysis.get("basic_info", {})
        missing = analysis.get("missing_values", {})
        outliers = analysis.get("outliers", {})
        
        summary = f"""
Dataset Overview:
- Shape: {basic.get('num_rows', 0):,} rows × {basic.get('num_columns', 0)} columns
- Numeric columns: {basic.get('num_numeric', 0)}
- Categorical columns: {basic.get('num_categorical', 0)}
- Memory usage: {basic.get('memory_usage_mb', 0):.2f} MB

Data Quality:
- Missing values: {missing.get('total_missing_values', 0):,} across {missing.get('columns_affected', 0)} columns
- Outliers detected: {outliers.get('total_outliers', 0):,} across {len(outliers.get('columns_with_outliers', {}))} columns
        """.strip()
        
        return summary
    
    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate automated insights from analysis."""
        insights = []
        
        basic = analysis.get("basic_info", {})
        missing = analysis.get("missing_values", {})
        correlations = analysis.get("correlations", {})
        outliers = analysis.get("outliers", {})
        
        # Missing values insights
        if missing.get("total_missing_values", 0) > 0:
            pct = missing["total_missing_values"] / (basic["num_rows"] * basic["num_columns"]) * 100
            insights.append(f"Dataset has {pct:.2f}% missing values - consider imputation strategies")
        
        # Correlation insights
        high_corr = correlations.get("high_correlations", [])
        if len(high_corr) > 0:
            insights.append(f"Found {len(high_corr)} high correlations - potential multicollinearity")
        
        # Outlier insights
        if outliers.get("total_outliers", 0) > 0:
            insights.append(f"Detected {outliers['total_outliers']} outliers - may need treatment")
        
        # Imbalance insights
        if basic.get("num_rows", 0) < 1000:
            insights.append("Small dataset - consider data augmentation or simpler models")
        
        return insights
    
    def _suggest_visualizations(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest appropriate visualizations."""
        suggestions = [
            "Correlation heatmap for numerical features",
            "Distribution plots for key numerical columns",
            "Missing value heatmap",
            "Box plots for outlier visualization",
        ]
        
        basic = analysis.get("basic_info", {})
        if basic.get("num_categorical", 0) > 0:
            suggestions.append("Bar charts for categorical variables")
        
        return suggestions
    

