#!/usr/bin/env python3
"""
Error Handling and Performance Optimization System

This module provides comprehensive error handling, progress tracking,
and performance optimization for the map conversion process.
"""

import os
import sys
import time
import logging
import traceback
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import psutil
import threading

class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ProcessingStage(Enum):
    """Processing stages for progress tracking."""
    PARSING = "parsing"
    VALIDATION = "validation"
    GEOMETRY_GENERATION = "geometry_generation"
    MATERIAL_ASSIGNMENT = "material_assignment"
    OPTIMIZATION = "optimization"
    EXPORT = "export"
    DATABASE_STORAGE = "database_storage"

@dataclass
class ErrorInfo:
    """Information about an error."""
    stage: ProcessingStage
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    stage: ProcessingStage
    start_time: float
    end_time: Optional[float] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    items_processed: int = 0
    total_items: int = 0
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def progress_percent(self) -> float:
        """Get progress as percentage."""
        if self.total_items > 0:
            return (self.items_processed / self.total_items) * 100
        return 0.0

class ProgressTracker:
    """Tracks progress of long-running operations."""
    
    def __init__(self, total_items: int, stage: ProcessingStage, verbose: bool = True):
        self.total_items = total_items
        self.stage = stage
        self.verbose = verbose
        self.current_item = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 1.0  # Update every second
        
        if self.verbose:
            self.logger = logging.getLogger(__name__)
    
    def update(self, items_processed: int = 1):
        """Update progress."""
        self.current_item += items_processed
        current_time = time.time()
        
        if current_time - self.last_update_time >= self.update_interval:
            self._log_progress()
            self.last_update_time = current_time
    
    def _log_progress(self):
        """Log current progress."""
        if not self.verbose:
            return
        
        elapsed = time.time() - self.start_time
        progress = (self.current_item / self.total_items) * 100
        
        if self.current_item > 0:
            items_per_sec = self.current_item / elapsed
            eta = (self.total_items - self.current_item) / items_per_sec
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: calculating..."
        
        self.logger.info(f"{self.stage.value}: {progress:.1f}% ({self.current_item}/{self.total_items}) - {eta_str}")
    
    def complete(self):
        """Mark operation as complete."""
        self.current_item = self.total_items
        if self.verbose:
            self._log_progress()
            total_time = time.time() - self.start_time
            self.logger.info(f"{self.stage.value}: Complete in {total_time:.2f}s")

class ErrorHandler:
    """Comprehensive error handling system."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.errors: List[ErrorInfo] = []
        self.logger = logging.getLogger(__name__)
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
    
    def handle_error(self, stage: ProcessingStage, message: str, 
                    exception: Optional[Exception] = None, 
                    context: Optional[Dict[str, Any]] = None,
                    severity: ErrorSeverity = ErrorSeverity.ERROR) -> ErrorInfo:
        """
        Handle an error with comprehensive logging and recovery options.
        
        Args:
            stage: Processing stage where error occurred
            message: Error message
            exception: Exception object if available
            context: Additional context information
            severity: Error severity level
            
        Returns:
            ErrorInfo object
        """
        error_info = ErrorInfo(
            stage=stage,
            severity=severity,
            message=message,
            exception=exception,
            context=context or {}
        )
        
        self.errors.append(error_info)
        
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"[{stage.value}] {message}")
            if exception:
                self.logger.critical(f"Exception: {exception}")
                self.logger.critical(f"Traceback: {traceback.format_exc()}")
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(f"[{stage.value}] {message}")
            if exception:
                self.logger.error(f"Exception: {exception}")
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(f"[{stage.value}] {message}")
        else:
            self.logger.info(f"[{stage.value}] {message}")
        
        return error_info
    
    def get_errors_by_stage(self, stage: ProcessingStage) -> List[ErrorInfo]:
        """Get all errors for a specific stage."""
        return [error for error in self.errors if error.stage == stage]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorInfo]:
        """Get all errors of a specific severity."""
        return [error for error in self.errors if error.severity == severity]
    
    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of errors by severity."""
        summary = {}
        for severity in ErrorSeverity:
            count = len(self.get_errors_by_severity(severity))
            if count > 0:
                summary[severity.value] = count
        return summary

class PerformanceMonitor:
    """Monitors performance metrics during operations."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.metrics: List[PerformanceMetrics] = []
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._monitor_thread = None
    
    @contextmanager
    def monitor_stage(self, stage: ProcessingStage, total_items: int = 0):
        """Context manager for monitoring a processing stage."""
        metric = PerformanceMetrics(
            stage=stage,
            start_time=time.time(),
            total_items=total_items
        )
        
        try:
            if self.verbose:
                self.logger.info(f"Starting {stage.value}...")
            
            yield metric
            
        finally:
            metric.end_time = time.time()
            metric.memory_usage_mb = self._get_memory_usage()
            metric.cpu_usage_percent = self._get_cpu_usage()
            
            self.metrics.append(metric)
            
            if self.verbose:
                duration = metric.duration
                memory = metric.memory_usage_mb
                self.logger.info(f"Completed {stage.value} in {duration:.2f}s (Memory: {memory:.1f}MB)")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_stage_metrics(self, stage: ProcessingStage) -> Optional[PerformanceMetrics]:
        """Get metrics for a specific stage."""
        for metric in self.metrics:
            if metric.stage == stage:
                return metric
        return None
    
    def get_total_duration(self) -> float:
        """Get total duration of all monitored stages."""
        if not self.metrics:
            return 0.0
        
        start_time = min(metric.start_time for metric in self.metrics)
        end_time = max(metric.end_time or time.time() for metric in self.metrics)
        return end_time - start_time
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {}
        
        total_duration = self.get_total_duration()
        total_memory = sum(metric.memory_usage_mb for metric in self.metrics)
        avg_cpu = sum(metric.cpu_usage_percent for metric in self.metrics) / len(self.metrics)
        
        stage_durations = {}
        for metric in self.metrics:
            stage_durations[metric.stage.value] = metric.duration
        
        return {
            "total_duration": total_duration,
            "total_memory_mb": total_memory,
            "average_cpu_percent": avg_cpu,
            "stage_durations": stage_durations,
            "stages_completed": len(self.metrics)
        }

class BatchProcessor:
    """Handles batch processing of multiple zones with error recovery."""
    
    def __init__(self, error_handler: ErrorHandler, performance_monitor: PerformanceMonitor):
        self.error_handler = error_handler
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(__name__)
    
    def process_zones(self, zones: List[str], processor_func: Callable, 
                     max_retries: int = 2, continue_on_error: bool = True) -> Dict[str, Any]:
        """
        Process multiple zones with error handling and recovery.
        
        Args:
            zones: List of zone names to process
            processor_func: Function to process each zone
            max_retries: Maximum number of retries per zone
            continue_on_error: Whether to continue processing other zones if one fails
            
        Returns:
            Dictionary with processing results
        """
        results = {
            "successful": [],
            "failed": [],
            "skipped": [],
            "total_processed": 0,
            "total_duration": 0.0
        }
        
        start_time = time.time()
        
        for zone_name in zones:
            zone_success = False
            retry_count = 0
            
            while retry_count <= max_retries and not zone_success:
                try:
                    with self.performance_monitor.monitor_stage(
                        ProcessingStage.PARSING, total_items=1
                    ) as metric:
                        result = processor_func(zone_name)
                        metric.items_processed = 1
                        zone_success = True
                        results["successful"].append(zone_name)
                        self.logger.info(f"Successfully processed zone: {zone_name}")
                
                except Exception as e:
                    retry_count += 1
                    error_msg = f"Failed to process zone {zone_name} (attempt {retry_count})"
                    
                    if retry_count > max_retries:
                        self.error_handler.handle_error(
                            ProcessingStage.PARSING,
                            error_msg,
                            exception=e,
                            context={"zone": zone_name, "retry_count": retry_count},
                            severity=ErrorSeverity.ERROR
                        )
                        results["failed"].append(zone_name)
                        
                        if not continue_on_error:
                            raise
                    else:
                        self.error_handler.handle_error(
                            ProcessingStage.PARSING,
                            error_msg,
                            exception=e,
                            context={"zone": zone_name, "retry_count": retry_count},
                            severity=ErrorSeverity.WARNING
                        )
                        self.logger.warning(f"Retrying zone {zone_name} (attempt {retry_count + 1})")
                        time.sleep(1)  # Brief pause before retry
            
            results["total_processed"] += 1
        
        results["total_duration"] = time.time() - start_time
        
        # Log summary
        self.logger.info(f"Batch processing complete:")
        self.logger.info(f"  - Successful: {len(results['successful'])}")
        self.logger.info(f"  - Failed: {len(results['failed'])}")
        self.logger.info(f"  - Total duration: {results['total_duration']:.2f}s")
        
        return results

class MemoryManager:
    """Manages memory usage during large operations."""
    
    def __init__(self, max_memory_mb: float = 1024, verbose: bool = True):
        self.max_memory_mb = max_memory_mb
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
    
    def check_memory_usage(self) -> float:
        """Check current memory usage and return MB used."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if self.verbose and memory_mb > self.max_memory_mb * 0.8:
                self.logger.warning(f"High memory usage: {memory_mb:.1f}MB (limit: {self.max_memory_mb}MB)")
            
            return memory_mb
        except:
            return 0.0
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory."""
        import gc
        gc.collect()
        
        if self.verbose:
            memory_after = self.check_memory_usage()
            self.logger.info(f"Garbage collection completed. Memory usage: {memory_after:.1f}MB")
    
    @contextmanager
    def memory_monitor(self, operation_name: str):
        """Context manager for monitoring memory during operations."""
        memory_before = self.check_memory_usage()
        
        try:
            yield
            
        finally:
            memory_after = self.check_memory_usage()
            memory_delta = memory_after - memory_before
            
            if self.verbose:
                self.logger.info(f"{operation_name}: Memory delta: {memory_delta:+.1f}MB "
                               f"(Before: {memory_before:.1f}MB, After: {memory_after:.1f}MB)") 