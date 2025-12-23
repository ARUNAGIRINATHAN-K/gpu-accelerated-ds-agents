"""Modeling Agent for GPU-accelerated model training."""

import logging
from typing import Any, Dict, List, Optional, Tuple
import warnings
import numpy as np
import pandas as pd

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ModelingAgent(BaseAgent):
    """Autonomous agent for model training and evaluation."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Modeling Agent."""
        super().__init__(name="Modeling Agent", config=config)
        
        # Check for GPU availability
        self.use_gpu = True
        try:
            import cuml
            self.cuml_available = True
            logger.info("Modeling Agent: cuML available (GPU mode)")
        except ImportError:
            self.cuml_available = False
            self.use_gpu = False
            logger.info("Modeling Agent: Using sklearn (CPU mode)")
        
        self.models = {}
        self.best_model = None
        self.task_type = None  # 'classification' or 'regression'
    
    def analyze(self, data: Any, target_column: str = None, **kwargs) -> Dict[str, Any]:
        """
        Analyze data for modeling.
        
        Args:
            data: Input DataFrame
            target_column: Name of target column
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with analysis results
        """
        logger.info("Modeling Agent: Analyzing data for modeling")
        
        if target_column is None:
            # Try to infer target column (last column by default)
            target_column = data.columns[-1]
            logger.info(f"No target specified, using last column: {target_column}")
        
        # Determine task type
        self.task_type = self._determine_task_type(data, target_column)
        
        analysis = {
            "target_column": target_column,
            "task_type": self.task_type,
            "num_samples": len(data),
            "num_features": len(data.columns) - 1,
            "class_distribution": self._analyze_target(data, target_column),
            "recommended_models": self._recommend_models(),
        }
        
        return analysis
    
    def execute(self, data: Any, target_column: str = None, **kwargs) -> Any:
        """
        Execute model training.
        
        Args:
            data: Input DataFrame
            target_column: Name of target column
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with trained models and results
        """
        logger.info("Modeling Agent: Training models")
        
        if target_column is None:
            target_column = data.columns[-1]
        
        # Prepare data
        X, y = self._prepare_data(data, target_column)
        X_train, X_test, y_train, y_test = self._split_data(X, y)
        
        # Get algorithms to train
        algorithms = self.config.get("algorithms", ["xgboost_gpu", "random_forest_gpu"])
        
        # Train models
        results = {}
        for algo in algorithms:
            try:
                logger.info(f"Training {algo}...")
                model, metrics = self._train_model(algo, X_train, y_train, X_test, y_test)
                
                self.models[algo] = model
                results[algo] = {
                    "model": model,
                    "metrics": metrics,
                }
                
                logger.info(f"{algo} training complete: {metrics}")
            except Exception as e:
                logger.error(f"Error training {algo}: {e}")
                results[algo] = {"error": str(e)}
        
        # Select best model
        self.best_model = self._select_best_model(results)
        
        return {
            "models": results,
            "best_model": self.best_model,
            "X_test": X_test,
            "y_test": y_test,
        }
    
    def report(self) -> Dict[str, Any]:
        """
        Generate modeling report.
        
        Returns:
            Dictionary with report data
        """
        analysis = self.results.get("analysis", {})
        processed_data = self.results.get("processed_data", {})
        
        report = {
            "agent": self.name,
            "metadata": self.get_metadata(),
            "summary": self._generate_summary(analysis, processed_data),
            "model_comparison": self._compare_models(processed_data),
            "best_model_info": self._get_best_model_info(),
        }
        
        return report
    
    def _determine_task_type(self, df: Any, target_column: str) -> str:
        """Determine if task is classification or regression."""
        target_series = df[target_column]
        dtype = target_series.dtype
        unique_values = target_series.nunique()
        
        # Robust check for floating point (Regression)
        is_float = False
        if np.issubdtype(dtype, np.floating):
            is_float = True
        elif 'float' in str(dtype).lower() or 'double' in str(dtype).lower():
            is_float = True
        elif hasattr(dtype, 'kind') and dtype.kind in 'fc':
            is_float = True
            
        if is_float:
            task_type = "regression"
        # If object, category, or bool, it's classification
        elif dtype == 'object' or str(dtype) in ['category', 'bool', 'boolean']:
            task_type = "classification"
        # For integers, decide based on unique count
        else:
            if unique_values <= 20:
                task_type = "classification"
            else:
                task_type = "regression"
        
        logger.info(f"Modeling Agent: Detected task type '{task_type}' (target: '{target_column}', dtype: {dtype}, unique: {unique_values})")
        return task_type
    
    def _analyze_target(self, df: Any, target_column: str) -> Dict:
        """Analyze target variable."""
        if self.task_type == "classification":
            value_counts = df[target_column].value_counts()
            return {
                "num_classes": len(value_counts),
                "class_counts": value_counts.to_dict(),
            }
        else:
            return {
                "mean": float(df[target_column].mean()),
                "std": float(df[target_column].std()),
                "min": float(df[target_column].min()),
                "max": float(df[target_column].max()),
            }
    
    def _recommend_models(self) -> List[str]:
        """Recommend models based on task type."""
        if self.task_type == "classification":
            return ["xgboost_gpu", "random_forest_gpu", "logistic_regression"]
        else:
            return ["xgboost_gpu", "random_forest_gpu", "linear_regression"]
    
    def _prepare_data(self, df: Any, target_column: str) -> Tuple[Any, Any]:
        """Prepare features and target."""
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Handle categorical features (simple label encoding)
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            X[col] = X[col].astype('category').cat.codes
        
        return X, y
    
    def _split_data(self, X: Any, y: Any) -> Tuple[Any, Any, Any, Any]:
        """Split data into train and test sets."""
        test_size = self.config.get("test_size", 0.2)
        random_state = self.config.get("random_state", 42)
        
        try:
            if self.cuml_available:
                from cuml.model_selection import train_test_split
            else:
                from sklearn.model_selection import train_test_split
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            logger.info(f"Data split: {len(X_train)} train, {len(X_test)} test")
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            raise
    
    def _train_model(self, algorithm: str, X_train, y_train, X_test, y_test) -> Tuple[Any, Dict]:
        """Train a single model."""
        if algorithm == "xgboost_gpu":
            return self._train_xgboost(X_train, y_train, X_test, y_test)
        elif algorithm == "random_forest_gpu":
            return self._train_random_forest(X_train, y_train, X_test, y_test)
        elif algorithm == "logistic_regression":
            return self._train_logistic(X_train, y_train, X_test, y_test)
        elif algorithm == "linear_regression":
            return self._train_linear(X_train, y_train, X_test, y_test)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _train_xgboost(self, X_train, y_train, X_test, y_test) -> Tuple[Any, Dict]:
        """Train XGBoost model with GPU support."""
        import xgboost as xgb
        import numpy as np
        
        # Convert to numpy if needed
        if hasattr(X_train, 'to_pandas'):
            X_train = X_train.to_pandas().values
            X_test = X_test.to_pandas().values
            y_train = y_train.to_pandas().values
            y_test = y_test.to_pandas().values
        elif hasattr(X_train, 'values'):
            X_train = X_train.values
            X_test = X_test.values
            y_train = y_train.values
            y_test = y_test.values
        
        params = {
            'tree_method': 'hist',  # Use 'gpu_hist' if GPU available
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
        }
        
        if self.task_type == "classification":
            params['objective'] = 'binary:logistic' if len(np.unique(y_train)) == 2 else 'multi:softmax'
            model = xgb.XGBClassifier(**params)
        else:
            params['objective'] = 'reg:squarederror'
            model = xgb.XGBRegressor(**params)
        
        model.fit(X_train, y_train)
        
        # Evaluate
        metrics = self._evaluate_model(model, X_test, y_test)
        
        return model, metrics
    
    def _train_random_forest(self, X_train, y_train, X_test, y_test) -> Tuple[Any, Dict]:
        """Train Random Forest model."""
        if self.cuml_available:
            from cuml.ensemble import RandomForestClassifier, RandomForestRegressor
            logger.info("Using cuML Random Forest (GPU)")
        else:
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            logger.info("Using sklearn Random Forest (CPU)")
        
        if self.task_type == "classification":
            model = RandomForestClassifier(n_estimators=100, max_depth=10)
        else:
            model = RandomForestRegressor(n_estimators=100, max_depth=10)
        
        model.fit(X_train, y_train)
        metrics = self._evaluate_model(model, X_test, y_test)
        
        return model, metrics
    
    def _train_logistic(self, X_train, y_train, X_test, y_test) -> Tuple[Any, Dict]:
        """Train Logistic Regression."""
        if self.cuml_available:
            from cuml.linear_model import LogisticRegression
        else:
            from sklearn.linear_model import LogisticRegression
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
        metrics = self._evaluate_model(model, X_test, y_test)
        
        return model, metrics
    
    def _train_linear(self, X_train, y_train, X_test, y_test) -> Tuple[Any, Dict]:
        """Train Linear Regression."""
        if self.cuml_available:
            from cuml.linear_model import LinearRegression
        else:
            from sklearn.linear_model import LinearRegression
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        metrics = self._evaluate_model(model, X_test, y_test)
        
        return model, metrics
    
    def _evaluate_model(self, model, X_test, y_test) -> Dict:
        """Evaluate model performance."""
        y_pred = model.predict(X_test)
        
        if self.task_type == "classification":
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                "f1": float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            }
        else:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            import numpy as np
            
            metrics = {
                "mse": float(mean_squared_error(y_test, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "r2": float(r2_score(y_test, y_pred)),
            }
        
        return metrics
    
    def _select_best_model(self, results: Dict) -> str:
        """Select best model based on metrics."""
        best_model = None
        best_score = -float('inf')
        
        metric_key = "accuracy" if self.task_type == "classification" else "r2"
        
        for algo, result in results.items():
            if "error" in result:
                continue
            
            score = result["metrics"].get(metric_key, -float('inf'))
            if score > best_score:
                best_score = score
                best_model = algo
        
        logger.info(f"Best model: {best_model} ({metric_key}={best_score:.4f})")
        return best_model
    
    def _generate_summary(self, analysis: Dict, processed_data: Dict) -> str:
        """Generate text summary."""
        models_trained = len(processed_data.get("models", {}))
        best_model = processed_data.get("best_model", "None")
        
        summary = f"""
Modeling Summary:
- Task type: {analysis.get('task_type', 'unknown')}
- Models trained: {models_trained}
- Best model: {best_model}
- Training samples: {analysis.get('num_samples', 0)}
- Features: {analysis.get('num_features', 0)}
        """.strip()
        
        return summary
    
    def _compare_models(self, processed_data: Dict) -> Dict:
        """Compare model performance."""
        models = processed_data.get("models", {})
        
        comparison = {}
        for algo, result in models.items():
            if "error" not in result:
                comparison[algo] = result["metrics"]
        
        return comparison
    
    def _get_best_model_info(self) -> Dict:
        """Get information about best model."""
        if self.best_model is None:
            return {}
        
        return {
            "name": self.best_model,
            "model_object": self.models.get(self.best_model),
        }
    

