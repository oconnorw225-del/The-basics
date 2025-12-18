// Type definitions for the Production Control Dashboard

export type ServiceStatus = 'running' | 'stopped' | 'error' | 'unknown';

export interface SystemHealth {
  api: ServiceStatus;
  trading: ServiceStatus;
  ai: ServiceStatus;
  aws: ServiceStatus;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  activeProcesses: number;
  uptime: string;
}

export interface TradingPosition {
  id: string;
  pair: string;
  type: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: string;
  status: 'open' | 'closed';
}

export interface TradingMetrics {
  totalTrades: number;
  activePositions: number;
  profit: number;
  winRate: number;
}

export interface AITask {
  id: string;
  title: string;
  provider: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  priority: number;
  createdAt: string;
  updatedAt: string;
}

export interface AIProvider {
  name: string;
  enabled: boolean;
  apiKey?: string;
  balance?: number;
}

export interface AWSDeployment {
  id: string;
  status: 'pending' | 'deploying' | 'success' | 'failed';
  version: string;
  timestamp: string;
  logs?: string[];
}

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  service: string;
  message: string;
}

export interface FeatureFlag {
  name: string;
  enabled: boolean;
  description: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface WebSocketMessage {
  type: 'status' | 'log' | 'metric' | 'alert';
  data: any;
  timestamp: string;
}

export interface AuthUser {
  id: string;
  username: string;
  role: 'admin' | 'user';
  permissions: string[];
}

export interface AlertConfig {
  type: 'error' | 'warning' | 'info' | 'success';
  threshold?: number;
  enabled: boolean;
}
