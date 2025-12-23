"""GPU utilities for CUDA device management and monitoring."""

import logging
from typing import Optional, Dict, Any
import warnings

logger = logging.getLogger(__name__)


class GPUUtils:
    """Utility class for GPU operations and monitoring."""
    
    def __init__(self):
        self.device = None
        self.gpu_available = self._check_gpu_availability()
        
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
                return True
            else:
                self.device = "cpu"
                logger.warning("No GPU available, falling back to CPU")
                return False
        except ImportError:
            logger.warning("PyTorch not available, cannot check GPU")
            self.device = "cpu"
            return False
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get detailed GPU device information."""
        info = {"device": self.device, "gpu_available": self.gpu_available}
        
        if self.gpu_available:
            try:
                import torch
                info.update({
                    "device_name": torch.cuda.get_device_name(0),
                    "device_count": torch.cuda.device_count(),
                    "cuda_version": torch.version.cuda,
                    "memory_allocated_gb": torch.cuda.memory_allocated(0) / 1e9,
                    "memory_reserved_gb": torch.cuda.memory_reserved(0) / 1e9,
                    "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                })
            except Exception as e:
                logger.error(f"Error getting GPU info: {e}")
        
        return info
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get current GPU memory statistics."""
        if not self.gpu_available:
            return {}
        
        try:
            import torch
            return {
                "allocated_gb": torch.cuda.memory_allocated(0) / 1e9,
                "reserved_gb": torch.cuda.memory_reserved(0) / 1e9,
                "max_allocated_gb": torch.cuda.max_memory_allocated(0) / 1e9,
                "max_reserved_gb": torch.cuda.max_memory_reserved(0) / 1e9,
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {}
    
    def clear_cache(self):
        """Clear GPU cache to free memory."""
        if self.gpu_available:
            try:
                import torch
                torch.cuda.empty_cache()
                logger.info("GPU cache cleared")
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
    
    def check_cudf_available(self) -> bool:
        """Check if cuDF (RAPIDS) is available."""
        try:
            import cudf
            logger.info(f"cuDF available: version {cudf.__version__}")
            return True
        except ImportError:
            logger.warning("cuDF not available - install RAPIDS for GPU acceleration")
            return False
    
    def check_cuml_available(self) -> bool:
        """Check if cuML (RAPIDS) is available."""
        try:
            import cuml
            logger.info(f"cuML available: version {cuml.__version__}")
            return True
        except ImportError:
            logger.warning("cuML not available - install RAPIDS for GPU acceleration")
            return False
    
    def get_optimal_batch_size(self, 
                               total_samples: int,
                               feature_dim: int,
                               available_memory_gb: Optional[float] = None) -> int:
        """
        Calculate optimal batch size based on available GPU memory.
        
        Args:
            total_samples: Total number of samples
            feature_dim: Feature dimensionality
            available_memory_gb: Available GPU memory in GB (auto-detect if None)
        
        Returns:
            Optimal batch size
        """
        if not self.gpu_available:
            return min(1024, total_samples)  # CPU fallback
        
        try:
            import torch
            
            if available_memory_gb is None:
                props = torch.cuda.get_device_properties(0)
                total_memory = props.total_memory / 1e9
                allocated = torch.cuda.memory_allocated(0) / 1e9
                available_memory_gb = total_memory - allocated - 2  # Leave 2GB buffer
            
            # Rough estimate: 4 bytes per float32 value
            bytes_per_sample = feature_dim * 4
            max_samples = int((available_memory_gb * 1e9) / bytes_per_sample * 0.5)  # Use 50% for safety
            
            batch_size = min(max_samples, total_samples, 4096)  # Cap at 4096
            batch_size = max(batch_size, 32)  # Minimum 32
            
            logger.info(f"Calculated optimal batch size: {batch_size}")
            return batch_size
            
        except Exception as e:
            logger.error(f"Error calculating batch size: {e}")
            return 256  # Safe default
    
    def monitor_gpu_usage(self) -> str:
        """Get formatted GPU usage string for logging."""
        if not self.gpu_available:
            return "GPU not available"
        
        stats = self.get_memory_stats()
        return (f"GPU Memory: {stats.get('allocated_gb', 0):.2f}GB allocated, "
                f"{stats.get('reserved_gb', 0):.2f}GB reserved")


# Global GPU utilities instance
gpu_utils = GPUUtils()


def get_device() -> str:
    """Get the current device (cuda or cpu)."""
    return gpu_utils.device


def is_gpu_available() -> bool:
    """Check if GPU is available."""
    return gpu_utils.gpu_available


def get_gpu_info() -> Dict[str, Any]:
    """Get GPU device information."""
    return gpu_utils.get_device_info()


def clear_gpu_cache():
    """Clear GPU cache."""
    gpu_utils.clear_cache()


def log_gpu_stats():
    """Log current GPU statistics."""
    logger.info(gpu_utils.monitor_gpu_usage())
