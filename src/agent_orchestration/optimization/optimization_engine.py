"""
Optimization algorithm engine for agent orchestration performance tuning.

This module provides adaptive algorithms that automatically adjust system
parameters based on performance metrics to optimize response times.
"""

from __future__ import annotations

import asyncio
import logging
import math
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable, Union
from uuid import uuid4
from enum import Enum

from .response_time_monitor import ResponseTimeCollector, ResponseTimeCategory, ResponseTimeStats

logger = logging.getLogger(__name__)


class OptimizationStrategy(str, Enum):
    """Available optimization strategies."""
    CONSERVATIVE = "conservative"  # Small, safe adjustments
    AGGRESSIVE = "aggressive"     # Larger adjustments for faster optimization
    ADAPTIVE = "adaptive"         # Adjusts strategy based on results
    STATISTICAL = "statistical"  # Uses statistical analysis for decisions


class OptimizationTarget(str, Enum):
    """Optimization targets."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    SUCCESS_RATE = "success_rate"
    RESOURCE_UTILIZATION = "resource_utilization"
    COST_EFFICIENCY = "cost_efficiency"


@dataclass
class OptimizationParameter:
    """Represents a system parameter that can be optimized."""
    name: str
    current_value: Union[int, float]
    min_value: Union[int, float]
    max_value: Union[int, float]
    step_size: Union[int, float]
    parameter_type: str  # 'int', 'float', 'bool'
    component: str  # Which component owns this parameter
    description: str = ""
    last_adjusted: float = field(default_factory=time.time)
    adjustment_count: int = 0
    
    def adjust(self, delta: Union[int, float]) -> Union[int, float]:
        """Adjust parameter value within bounds."""
        if self.parameter_type == 'int':
            new_value = int(self.current_value + delta)
            new_value = max(self.min_value, min(self.max_value, new_value))
        else:
            new_value = float(self.current_value + delta)
            new_value = max(self.min_value, min(self.max_value, new_value))
        
        self.current_value = new_value
        self.last_adjusted = time.time()
        self.adjustment_count += 1
        
        return new_value


@dataclass
class OptimizationResult:
    """Result of an optimization attempt."""
    optimization_id: str
    parameter_name: str
    old_value: Union[int, float]
    new_value: Union[int, float]
    strategy: OptimizationStrategy
    target: OptimizationTarget
    improvement_expected: float
    confidence_score: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OptimizationAlgorithm(ABC):
    """Base class for optimization algorithms."""
    
    @abstractmethod
    def analyze_performance(
        self,
        stats: Dict[str, ResponseTimeStats],
        parameters: Dict[str, OptimizationParameter],
    ) -> List[OptimizationResult]:
        """Analyze performance and suggest parameter adjustments."""
        pass
    
    @abstractmethod
    def get_strategy(self) -> OptimizationStrategy:
        """Get the optimization strategy."""
        pass


class ConservativeOptimizer(OptimizationAlgorithm):
    """Conservative optimization algorithm with small, safe adjustments."""
    
    def __init__(self, adjustment_factor: float = 0.1):
        self.adjustment_factor = adjustment_factor
    
    def get_strategy(self) -> OptimizationStrategy:
        return OptimizationStrategy.CONSERVATIVE
    
    def analyze_performance(
        self,
        stats: Dict[str, ResponseTimeStats],
        parameters: Dict[str, OptimizationParameter],
    ) -> List[OptimizationResult]:
        """Conservative analysis focusing on gradual improvements."""
        results = []
        
        # Analyze message processing performance
        message_stats = {k: v for k, v in stats.items() if v.category == ResponseTimeCategory.MESSAGE_PROCESSING}
        
        for stat_key, stat in message_stats.items():
            # If P95 response time is high, suggest reducing queue size or increasing timeout
            if stat.p95_duration > 5.0:  # 5 seconds threshold
                # Look for queue size parameter
                queue_param = parameters.get("message_queue_size")
                if queue_param and queue_param.current_value > queue_param.min_value:
                    adjustment = -max(1, int(queue_param.current_value * self.adjustment_factor))
                    
                    result = OptimizationResult(
                        optimization_id=uuid4().hex,
                        parameter_name="message_queue_size",
                        old_value=queue_param.current_value,
                        new_value=queue_param.current_value + adjustment,
                        strategy=self.get_strategy(),
                        target=OptimizationTarget.RESPONSE_TIME,
                        improvement_expected=0.1,  # 10% improvement expected
                        confidence_score=0.7,
                        metadata={
                            "reason": "High P95 response time in message processing",
                            "current_p95": stat.p95_duration,
                            "threshold": 5.0,
                        }
                    )
                    results.append(result)
        
        return results


class AggressiveOptimizer(OptimizationAlgorithm):
    """Aggressive optimization algorithm with larger adjustments."""
    
    def __init__(self, adjustment_factor: float = 0.25):
        self.adjustment_factor = adjustment_factor
    
    def get_strategy(self) -> OptimizationStrategy:
        return OptimizationStrategy.AGGRESSIVE
    
    def analyze_performance(
        self,
        stats: Dict[str, ResponseTimeStats],
        parameters: Dict[str, OptimizationParameter],
    ) -> List[OptimizationResult]:
        """Aggressive analysis with larger parameter adjustments."""
        results = []
        
        # More aggressive timeout adjustments
        for stat_key, stat in stats.items():
            if stat.success_rate < 0.9:  # Less than 90% success rate
                # Increase timeout parameters
                timeout_params = [p for p in parameters.values() if "timeout" in p.name.lower()]
                
                for param in timeout_params:
                    if param.current_value < param.max_value:
                        adjustment = max(param.step_size, param.current_value * self.adjustment_factor)
                        
                        result = OptimizationResult(
                            optimization_id=uuid4().hex,
                            parameter_name=param.name,
                            old_value=param.current_value,
                            new_value=min(param.max_value, param.current_value + adjustment),
                            strategy=self.get_strategy(),
                            target=OptimizationTarget.SUCCESS_RATE,
                            improvement_expected=0.2,  # 20% improvement expected
                            confidence_score=0.6,
                            metadata={
                                "reason": "Low success rate detected",
                                "current_success_rate": stat.success_rate,
                                "threshold": 0.9,
                            }
                        )
                        results.append(result)
        
        return results


class StatisticalOptimizer(OptimizationAlgorithm):
    """Statistical optimization algorithm using data analysis."""
    
    def __init__(self, min_samples: int = 50, confidence_threshold: float = 0.8):
        self.min_samples = min_samples
        self.confidence_threshold = confidence_threshold
    
    def get_strategy(self) -> OptimizationStrategy:
        return OptimizationStrategy.STATISTICAL
    
    def analyze_performance(
        self,
        stats: Dict[str, ResponseTimeStats],
        parameters: Dict[str, OptimizationParameter],
    ) -> List[OptimizationResult]:
        """Statistical analysis based on data trends."""
        results = []
        
        # Only make suggestions if we have enough data
        high_confidence_stats = {
            k: v for k, v in stats.items() 
            if v.sample_count >= self.min_samples
        }
        
        for stat_key, stat in high_confidence_stats.items():
            # Calculate coefficient of variation (CV) to assess consistency
            cv = (stat.p95_duration - stat.median_duration) / stat.median_duration if stat.median_duration > 0 else 0
            
            # High variability suggests need for optimization
            if cv > 0.5:  # High variability threshold
                # Suggest heartbeat interval adjustment for better monitoring
                heartbeat_param = parameters.get("heartbeat_interval")
                if heartbeat_param:
                    # Reduce heartbeat interval for better monitoring
                    adjustment = -max(heartbeat_param.step_size, heartbeat_param.current_value * 0.1)
                    
                    result = OptimizationResult(
                        optimization_id=uuid4().hex,
                        parameter_name="heartbeat_interval",
                        old_value=heartbeat_param.current_value,
                        new_value=max(heartbeat_param.min_value, heartbeat_param.current_value + adjustment),
                        strategy=self.get_strategy(),
                        target=OptimizationTarget.RESPONSE_TIME,
                        improvement_expected=0.15,
                        confidence_score=min(0.9, stat.sample_count / 100.0),
                        metadata={
                            "reason": "High response time variability detected",
                            "coefficient_of_variation": cv,
                            "sample_count": stat.sample_count,
                        }
                    )
                    results.append(result)
        
        return results


class OptimizationEngine:
    """Main optimization engine that coordinates different algorithms."""
    
    def __init__(
        self,
        response_time_collector: ResponseTimeCollector,
        event_publisher: Optional[Any] = None,
        optimization_interval: float = 300.0,  # 5 minutes
        enabled_strategies: Optional[List[OptimizationStrategy]] = None,
        max_adjustments_per_cycle: int = 3,
    ):
        self.response_time_collector = response_time_collector
        self.event_publisher = event_publisher
        self.optimization_interval = optimization_interval
        self.max_adjustments_per_cycle = max_adjustments_per_cycle
        
        # Available optimization algorithms
        self.algorithms: Dict[OptimizationStrategy, OptimizationAlgorithm] = {
            OptimizationStrategy.CONSERVATIVE: ConservativeOptimizer(),
            OptimizationStrategy.AGGRESSIVE: AggressiveOptimizer(),
            OptimizationStrategy.STATISTICAL: StatisticalOptimizer(),
        }
        
        # Enabled strategies
        self.enabled_strategies = enabled_strategies or [OptimizationStrategy.CONSERVATIVE]
        
        # System parameters that can be optimized
        self.parameters: Dict[str, OptimizationParameter] = {}
        
        # Optimization history
        self.optimization_history: List[OptimizationResult] = []
        
        # Component callbacks for parameter updates
        self.parameter_callbacks: Dict[str, Callable[[str, Any], None]] = {}
        
        # Background tasks
        self._optimization_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        logger.info("OptimizationEngine initialized")
    
    async def start(self) -> None:
        """Start the optimization engine."""
        if self._is_running:
            return
        
        self._is_running = True
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        logger.info("OptimizationEngine started")
    
    async def stop(self) -> None:
        """Stop the optimization engine."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("OptimizationEngine stopped")
    
    def register_parameter(
        self,
        name: str,
        current_value: Union[int, float],
        min_value: Union[int, float],
        max_value: Union[int, float],
        step_size: Union[int, float],
        parameter_type: str,
        component: str,
        description: str = "",
        callback: Optional[Callable[[str, Any], None]] = None,
    ) -> None:
        """Register a parameter for optimization."""
        parameter = OptimizationParameter(
            name=name,
            current_value=current_value,
            min_value=min_value,
            max_value=max_value,
            step_size=step_size,
            parameter_type=parameter_type,
            component=component,
            description=description,
        )
        
        self.parameters[name] = parameter
        
        if callback:
            self.parameter_callbacks[name] = callback
        
        logger.info(f"Registered optimization parameter: {name} ({component})")
    
    async def run_optimization_cycle(self) -> List[OptimizationResult]:
        """Run a single optimization cycle."""
        # Get current performance statistics
        stats = self.response_time_collector.get_all_stats(force_refresh=True)
        
        if not stats:
            logger.debug("No performance statistics available for optimization")
            return []
        
        # Run enabled optimization algorithms
        all_results = []
        
        for strategy in self.enabled_strategies:
            algorithm = self.algorithms.get(strategy)
            if algorithm:
                try:
                    results = algorithm.analyze_performance(stats, self.parameters)
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Error in {strategy} optimization algorithm: {e}")
        
        # Sort results by confidence score and limit adjustments
        all_results.sort(key=lambda r: r.confidence_score, reverse=True)
        selected_results = all_results[:self.max_adjustments_per_cycle]
        
        # Apply optimizations
        applied_results = []
        for result in selected_results:
            if await self._apply_optimization(result):
                applied_results.append(result)
                self.optimization_history.append(result)
        
        logger.info(f"Applied {len(applied_results)} optimizations out of {len(all_results)} suggestions")
        return applied_results
    
    async def _apply_optimization(self, result: OptimizationResult) -> bool:
        """Apply an optimization result."""
        parameter = self.parameters.get(result.parameter_name)
        if not parameter:
            logger.warning(f"Parameter not found: {result.parameter_name}")
            return False
        
        try:
            # Apply the parameter adjustment
            old_value = parameter.current_value
            new_value = parameter.adjust(result.new_value - result.old_value)
            
            # Call component callback if available
            callback = self.parameter_callbacks.get(result.parameter_name)
            if callback:
                callback(result.parameter_name, new_value)
            
            # Publish optimization event
            if self.event_publisher:
                await self.event_publisher.publish_optimization_event(
                    optimization_type=result.strategy.value,
                    parameter_name=result.parameter_name,
                    old_value=old_value,
                    new_value=new_value,
                    improvement_metric=result.target.value,
                    improvement_value=result.improvement_expected,
                    confidence_score=result.confidence_score,
                )
            
            logger.info(f"Applied optimization: {result.parameter_name} {old_value} -> {new_value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization for {result.parameter_name}: {e}")
            return False
    
    async def _optimization_loop(self) -> None:
        """Background optimization loop."""
        while self._is_running:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                if self._is_running:
                    await self.run_optimization_cycle()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get optimization engine statistics."""
        return {
            "is_running": self._is_running,
            "enabled_strategies": [s.value for s in self.enabled_strategies],
            "registered_parameters": len(self.parameters),
            "optimization_history": len(self.optimization_history),
            "recent_optimizations": len([r for r in self.optimization_history if time.time() - r.timestamp < 3600]),
            "configuration": {
                "optimization_interval": self.optimization_interval,
                "max_adjustments_per_cycle": self.max_adjustments_per_cycle,
            }
        }
