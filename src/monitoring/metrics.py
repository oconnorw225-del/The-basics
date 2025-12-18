#!/usr/bin/env python3
"""
Performance and Business Metrics Collection
"""

import time
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Metric:
    """Represents a metric"""
    
    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Initialize metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            description: Metric description
            labels: Metric labels
        """
        self.name = name
        self.metric_type = metric_type
        self.description = description
        self.labels = labels or {}
        self.timestamp = datetime.utcnow()
        self.value = 0.0
        
        # For histograms
        self.values: deque = deque(maxlen=1000)


class MetricsCollector:
    """
    Performance and business metrics collection.
    Tracks system and application metrics for monitoring.
    """
    
    def __init__(
        self,
        logger=None,
        retention_seconds: int = 3600
    ):
        """
        Initialize metrics collector.
        
        Args:
            logger: Logger instance
            retention_seconds: How long to retain metrics
        """
        self.logger = logger
        self.retention_seconds = retention_seconds
        
        # Metrics storage
        self.metrics: Dict[str, Metric] = {}
        
        # Time series data
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # System metrics cache
        self.system_metrics_cache: Dict[str, Any] = {}
        self.last_system_update = 0
        self.system_update_interval = 1.0  # seconds
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Register a new metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            description: Description
            labels: Labels
        """
        metric = Metric(
            name=name,
            metric_type=metric_type,
            description=description,
            labels=labels
        )
        
        self.metrics[name] = metric
        
        if self.logger:
            self.logger.debug(f"Registered metric: {name} ({metric_type.value})")
    
    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Increment value
            labels: Optional labels
        """
        # Auto-register if not exists
        if name not in self.metrics:
            self.register_metric(name, MetricType.COUNTER, labels=labels)
        
        metric = self.metrics[name]
        metric.value += value
        metric.timestamp = datetime.utcnow()
        
        # Record in time series
        self._record_time_series(name, metric.value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name
            value: Gauge value
            labels: Optional labels
        """
        # Auto-register if not exists
        if name not in self.metrics:
            self.register_metric(name, MetricType.GAUGE, labels=labels)
        
        metric = self.metrics[name]
        metric.value = value
        metric.timestamp = datetime.utcnow()
        
        # Record in time series
        self._record_time_series(name, value)
    
    def observe(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Observe a value for histogram/summary.
        
        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels
        """
        # Auto-register if not exists
        if name not in self.metrics:
            self.register_metric(name, MetricType.HISTOGRAM, labels=labels)
        
        metric = self.metrics[name]
        metric.values.append(value)
        metric.timestamp = datetime.utcnow()
        
        # Update calculated value (mean)
        if metric.values:
            metric.value = sum(metric.values) / len(metric.values)
        
        # Record in time series
        self._record_time_series(name, value)
    
    def _record_time_series(self, name: str, value: float):
        """Record value in time series."""
        timestamp = datetime.utcnow()
        self.time_series[name].append({
            'timestamp': timestamp.isoformat(),
            'value': value
        })
    
    def collect_system_metrics(self, force: bool = False) -> Dict[str, float]:
        """
        Collect system metrics (CPU, memory, disk, etc.).
        
        Args:
            force: Force update even if cache is fresh
            
        Returns:
            System metrics dict
        """
        now = time.time()
        
        # Use cache if fresh
        if not force and (now - self.last_system_update) < self.system_update_interval:
            return self.system_metrics_cache
        
        metrics = {}
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        metrics['system.cpu.percent'] = cpu_percent
        metrics['system.cpu.count'] = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics['system.memory.percent'] = memory.percent
        metrics['system.memory.used_mb'] = memory.used / (1024 * 1024)
        metrics['system.memory.available_mb'] = memory.available / (1024 * 1024)
        metrics['system.memory.total_mb'] = memory.total / (1024 * 1024)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics['system.disk.percent'] = disk.percent
        metrics['system.disk.used_gb'] = disk.used / (1024 * 1024 * 1024)
        metrics['system.disk.free_gb'] = disk.free / (1024 * 1024 * 1024)
        
        # Network metrics (if available)
        try:
            net_io = psutil.net_io_counters()
            metrics['system.network.bytes_sent'] = net_io.bytes_sent
            metrics['system.network.bytes_recv'] = net_io.bytes_recv
        except:
            pass
        
        # Update cache
        self.system_metrics_cache = metrics
        self.last_system_update = now
        
        # Record as gauge metrics
        for name, value in metrics.items():
            self.set_gauge(name, value)
        
        return metrics
    
    def collect_process_metrics(self, pid: Optional[int] = None) -> Dict[str, float]:
        """
        Collect metrics for a specific process.
        
        Args:
            pid: Process ID (defaults to current process)
            
        Returns:
            Process metrics dict
        """
        metrics = {}
        
        try:
            if pid is None:
                process = psutil.Process()
            else:
                process = psutil.Process(pid)
            
            # CPU
            metrics['process.cpu.percent'] = process.cpu_percent(interval=0.1)
            
            # Memory
            mem_info = process.memory_info()
            metrics['process.memory.rss_mb'] = mem_info.rss / (1024 * 1024)
            metrics['process.memory.vms_mb'] = mem_info.vms / (1024 * 1024)
            
            # Threads
            metrics['process.threads'] = process.num_threads()
            
            # File descriptors (Unix only)
            try:
                metrics['process.file_descriptors'] = process.num_fds()
            except:
                pass
            
            # Record as gauge metrics
            for name, value in metrics.items():
                self.set_gauge(name, value)
            
        except psutil.NoSuchProcess:
            if self.logger:
                self.logger.warning(f"Process {pid} not found")
        
        return metrics
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """
        Get a metric by name.
        
        Args:
            name: Metric name
            
        Returns:
            Metric or None
        """
        return self.metrics.get(name)
    
    def get_metric_value(self, name: str) -> Optional[float]:
        """
        Get current metric value.
        
        Args:
            name: Metric name
            
        Returns:
            Metric value or None
        """
        metric = self.get_metric(name)
        return metric.value if metric else None
    
    def get_time_series(
        self,
        name: str,
        duration_seconds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for a metric.
        
        Args:
            name: Metric name
            duration_seconds: Time window (None for all)
            
        Returns:
            List of time series points
        """
        if name not in self.time_series:
            return []
        
        series = list(self.time_series[name])
        
        if duration_seconds:
            cutoff = datetime.utcnow() - timedelta(seconds=duration_seconds)
            cutoff_iso = cutoff.isoformat()
            
            series = [
                point for point in series
                if point['timestamp'] >= cutoff_iso
            ]
        
        return series
    
    def get_statistics(self, name: str) -> Optional[Dict[str, float]]:
        """
        Get statistics for a metric.
        
        Args:
            name: Metric name
            
        Returns:
            Statistics dict or None
        """
        metric = self.get_metric(name)
        if not metric:
            return None
        
        stats = {
            'current': metric.value,
            'last_updated': metric.timestamp.isoformat()
        }
        
        # For histograms, add additional stats
        if metric.metric_type == MetricType.HISTOGRAM and metric.values:
            values = list(metric.values)
            values.sort()
            
            stats['count'] = len(values)
            stats['min'] = min(values)
            stats['max'] = max(values)
            stats['mean'] = sum(values) / len(values)
            
            # Percentiles
            if len(values) >= 2:
                stats['p50'] = values[len(values) // 2]
                stats['p95'] = values[int(len(values) * 0.95)]
                stats['p99'] = values[int(len(values) * 0.99)]
        
        return stats
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics with current values.
        
        Returns:
            Dict of all metrics
        """
        return {
            name: {
                'type': metric.metric_type.value,
                'value': metric.value,
                'description': metric.description,
                'labels': metric.labels,
                'timestamp': metric.timestamp.isoformat()
            }
            for name, metric in self.metrics.items()
        }
    
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics
        """
        lines = []
        
        for name, metric in self.metrics.items():
            # Help line
            if metric.description:
                lines.append(f"# HELP {name} {metric.description}")
            
            # Type line
            lines.append(f"# TYPE {name} {metric.metric_type.value}")
            
            # Value line
            labels_str = ""
            if metric.labels:
                labels_parts = [f'{k}="{v}"' for k, v in metric.labels.items()]
                labels_str = "{" + ",".join(labels_parts) + "}"
            
            lines.append(f"{name}{labels_str} {metric.value}")
        
        return "\n".join(lines)


def create_metrics_collector(logger=None) -> MetricsCollector:
    """
    Factory function to create metrics collector.
    
    Args:
        logger: Logger instance
        
    Returns:
        MetricsCollector instance
    """
    return MetricsCollector(logger=logger)
