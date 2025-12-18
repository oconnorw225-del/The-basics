import React, { useEffect, useState } from 'react';
import { Activity, Cpu, HardDrive } from 'lucide-react';
import Card from './ui/Card';
import Badge from './ui/Badge';
import api from '../services/api';
import type { SystemHealth, SystemMetrics, ServiceStatus } from '../types';

const SystemStatusPanel: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth>({
    api: 'unknown',
    trading: 'unknown',
    ai: 'unknown',
    aws: 'unknown',
  });
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    activeProcesses: 0,
    uptime: '00:00:00',
  });

  useEffect(() => {
    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const [healthRes, metricsRes] = await Promise.all([
        api.getSystemHealth(),
        api.getSystemMetrics(),
      ]);

      if (healthRes.success && healthRes.data) {
        setHealth(healthRes.data);
      }

      if (metricsRes.success && metricsRes.data) {
        setMetrics(metricsRes.data);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const getStatusColor = (status: ServiceStatus): 'running' | 'stopped' | 'error' | 'unknown' => {
    return status as any;
  };

  return (
    <Card title="System Status" className="mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">API Service</p>
            <Badge status={getStatusColor(health.api)} className="mt-1">
              {health.api}
            </Badge>
          </div>
          <Activity className="w-8 h-8 text-primary-500" />
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Trading Bot</p>
            <Badge status={getStatusColor(health.trading)} className="mt-1">
              {health.trading}
            </Badge>
          </div>
          <Activity className="w-8 h-8 text-success-500" />
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">AI Bot</p>
            <Badge status={getStatusColor(health.ai)} className="mt-1">
              {health.ai}
            </Badge>
          </div>
          <Activity className="w-8 h-8 text-warning-500" />
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">AWS Services</p>
            <Badge status={getStatusColor(health.aws)} className="mt-1">
              {health.aws}
            </Badge>
          </div>
          <Activity className="w-8 h-8 text-danger-500" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="flex items-center p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
          <Cpu className="w-6 h-6 text-primary-600 dark:text-primary-400 mr-3" />
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">CPU Usage</p>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{metrics.cpu}%</p>
          </div>
        </div>

        <div className="flex items-center p-3 bg-success-50 dark:bg-success-900/20 rounded-lg">
          <HardDrive className="w-6 h-6 text-success-600 dark:text-success-400 mr-3" />
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Memory</p>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{metrics.memory}%</p>
          </div>
        </div>

        <div className="flex items-center p-3 bg-warning-50 dark:bg-warning-900/20 rounded-lg">
          <Activity className="w-6 h-6 text-warning-600 dark:text-warning-400 mr-3" />
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Processes</p>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{metrics.activeProcesses}</p>
          </div>
        </div>

        <div className="flex items-center p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
          <Activity className="w-6 h-6 text-gray-600 dark:text-gray-400 mr-3" />
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Uptime</p>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{metrics.uptime}</p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default SystemStatusPanel;
