"""Base agent class for all autonomous agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all autonomous agents."""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            config: Agent configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.results = {}
        self.metadata = {
            "agent_name": name,
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "status": "initialized",
        }
        
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Analyze the data and generate insights.
        
        Args:
            data: Input data (DataFrame)
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with analysis results
        """
        pass
    
    @abstractmethod
    def execute(self, data: Any, **kwargs) -> Any:
        """
        Execute the agent's main task.
        
        Args:
            data: Input data
            **kwargs: Additional arguments
        
        Returns:
            Processed data or results
        """
        pass
    
    @abstractmethod
    def report(self) -> Dict[str, Any]:
        """
        Generate a report of the agent's work.
        
        Returns:
            Dictionary with report data
        """
        pass
    
    def run(self, data: Any, **kwargs) -> tuple:
        """
        Run the complete agent workflow: analyze → execute → report.
        
        Args:
            data: Input data
            **kwargs: Additional arguments
        
        Returns:
            Tuple of (processed_data, report)
        """
        logger.info(f"Running {self.name}")
        self.metadata["start_time"] = datetime.now()
        self.metadata["status"] = "running"
        
        try:
            # Analyze
            logger.info(f"{self.name}: Analyzing data")
            analysis = self.analyze(data, **kwargs)
            self.results["analysis"] = analysis
            
            # Execute
            logger.info(f"{self.name}: Executing main task")
            processed_data = self.execute(data, **kwargs)
            self.results["processed_data"] = processed_data
            
            # Report
            logger.info(f"{self.name}: Generating report")
            report = self.report()
            
            self.metadata["status"] = "completed"
            self.metadata["end_time"] = datetime.now()
            self.metadata["duration_seconds"] = (
                self.metadata["end_time"] - self.metadata["start_time"]
            ).total_seconds()
            
            logger.info(f"{self.name} completed in {self.metadata['duration_seconds']:.2f}s")
            
            return processed_data, report
            
        except Exception as e:
            self.metadata["status"] = "failed"
            self.metadata["error"] = str(e)
            logger.error(f"{self.name} failed: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return self.metadata.copy()
    
    def get_results(self) -> Dict[str, Any]:
        """Get agent results."""
        return self.results.copy()
    
    def reset(self):
        """Reset agent state."""
        self.results = {}
        self.metadata.update({
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "status": "initialized",
        })
        logger.info(f"{self.name} reset")
