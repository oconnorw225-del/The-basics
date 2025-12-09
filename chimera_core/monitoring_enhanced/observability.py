"""
Observability System - Critical Gap #4
Provides monitoring, health checks, metrics, and error tracking
Lightweight implementation without external dependencies
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict, deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not installed - system metrics unavailable")

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check system"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, tuple] = {}
    
    def register_component(self, name: str, check_func: Callable):
        """Register a health check"""
        self.checks[name] = check_func
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                is_healthy, message = await check_func()
                results[name] = {
                    'healthy': is_healthy,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                self.last_results[name] = (is_healthy, message)
            except Exception as e:
                results[name] = {
                    'healthy': False,
                    'message': f"Check failed: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }
        
        return results


class MetricsCollector:
    """Metrics collection system"""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter"""
        self.counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge value"""
        self.gauges[name] = value
    
    def record_histogram(self, name: str, value: float):
        """Record histogram value"""
        self.histograms[name].append(value)
    
    def record_trade(self, exchange: str, symbol: str, side: str, status: str, volume: float, pnl: float = 0):
        """Record trade metrics"""
        self.increment_counter(f'trades_total_{exchange}')
        self.increment_counter(f'trades_{status}')
        self.record_histogram(f'trade_volume_{symbol}', volume)
        if pnl != 0:
            self.record_histogram(f'trade_pnl_{symbol}', pnl)
    
    def update_solvency(self, ratio: float, risk_level: str):
        """Update solvency metrics"""
        self.set_gauge('solvency_ratio', ratio)
        self.set_gauge(f'risk_level_{risk_level}', 1.0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {
                name: {
                    'count': len(values),
                    'avg': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
                for name, values in self.histograms.items()
            }
        }


class ErrorTracker:
    """Error tracking system"""
    
    def __init__(self):
        self.errors: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
    
    def record_error(self, component: str, error: Exception, context: Optional[Dict] = None):
        """Record an error"""
        error_entry = {
            'component': component,
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.errors.append(error_entry)
        self.error_counts[component] += 1
        
        logger.error(f"❌ Error in {component}: {error}")
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict]:
        """Get recent errors"""
        return list(self.errors)[-limit:]
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error summary by component"""
        return dict(self.error_counts)


class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alerts: deque = deque(maxlen=100)
        self.alert_callbacks: List[Callable] = []
    
    def register_callback(self, callback: Callable):
        """Register alert callback"""
        self.alert_callbacks.append(callback)
    
    async def trigger_alert(self, severity: str, component: str, message: str, metadata: Optional[Dict] = None):
        """Trigger an alert"""
        alert = {
            'severity': severity,
            'component': component,
            'message': message,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        logger.warning(f"🚨 Alert [{severity}] {component}: {message}")
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """Get recent alerts"""
        return list(self.alerts)[-limit:]


class ObservabilitySystem:
    """Complete observability system"""
    
    def __init__(self, db=None):
        self.db = db
        self.health = HealthChecker()
        self.metrics = MetricsCollector()
        self.errors = ErrorTracker()
        self.alerts = AlertManager()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start(self):
        """Start monitoring"""
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("✅ Observability system started")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.is_running:
            try:
                # Collect system metrics if psutil available
                if PSUTIL_AVAILABLE:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    self.metrics.set_gauge('system_cpu_percent', cpu_percent)
                    self.metrics.set_gauge('system_memory_percent', memory.percent)
                    self.metrics.set_gauge('system_memory_available_mb', memory.available / (1024 * 1024))
                    
                    # Check if resources are critical
                    if cpu_percent > 90:
                        await self.alerts.trigger_alert(
                            'warning',
                            'system',
                            f'High CPU usage: {cpu_percent}%',
                            {'cpu_percent': cpu_percent}
                        )
                    
                    if memory.percent > 90:
                        await self.alerts.trigger_alert(
                            'warning',
                            'system',
                            f'High memory usage: {memory.percent}%',
                            {'memory_percent': memory.percent}
                        )
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop monitoring"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("✅ Observability system stopped")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            'health': self.health.last_results,
            'metrics': self.metrics.get_metrics(),
            'recent_errors': self.errors.get_recent_errors(10),
            'recent_alerts': self.alerts.get_recent_alerts(10),
            'error_summary': self.errors.get_error_summary(),
            'timestamp': datetime.now().isoformat()
        }
