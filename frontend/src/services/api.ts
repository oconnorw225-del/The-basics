import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiResponse } from '../types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Trading APIs
  async startTrading(): Promise<ApiResponse> {
    const { data } = await this.client.post('/trading/start');
    return data;
  }

  async stopTrading(): Promise<ApiResponse> {
    const { data } = await this.client.post('/trading/stop');
    return data;
  }

  async getTradingPositions(): Promise<ApiResponse> {
    const { data } = await this.client.get('/trading/positions');
    return data;
  }

  async executeTrade(tradeData: any): Promise<ApiResponse> {
    const { data } = await this.client.post('/trading/execute', tradeData);
    return data;
  }

  async getTradingHistory(): Promise<ApiResponse> {
    const { data } = await this.client.get('/trading/history');
    return data;
  }

  async emergencyStopAll(): Promise<ApiResponse> {
    const { data } = await this.client.post('/trading/emergency-stop');
    return data;
  }

  // AI/Freelance APIs
  async startAI(): Promise<ApiResponse> {
    const { data } = await this.client.post('/ai/start');
    return data;
  }

  async stopAI(): Promise<ApiResponse> {
    const { data } = await this.client.post('/ai/stop');
    return data;
  }

  async getActiveTasks(): Promise<ApiResponse> {
    const { data } = await this.client.get('/ai/tasks/active');
    return data;
  }

  async submitTask(taskData: any): Promise<ApiResponse> {
    const { data } = await this.client.post('/ai/tasks', taskData);
    return data;
  }

  async getTaskQueue(): Promise<ApiResponse> {
    const { data } = await this.client.get('/ai/queue');
    return data;
  }

  async configureProviders(providers: any): Promise<ApiResponse> {
    const { data } = await this.client.put('/ai/providers', providers);
    return data;
  }

  // AWS APIs
  async deployToAWS(): Promise<ApiResponse> {
    const { data } = await this.client.post('/aws/deploy');
    return data;
  }

  async getDeploymentStatus(): Promise<ApiResponse> {
    const { data } = await this.client.get('/aws/status');
    return data;
  }

  async healthCheckAWS(): Promise<ApiResponse> {
    const { data } = await this.client.get('/aws/health');
    return data;
  }

  async getCloudWatchLogs(): Promise<ApiResponse> {
    const { data } = await this.client.get('/aws/logs');
    return data;
  }

  async scaleECSServices(config: any): Promise<ApiResponse> {
    const { data } = await this.client.post('/aws/scale', config);
    return data;
  }

  async rollbackDeployment(): Promise<ApiResponse> {
    const { data } = await this.client.post('/aws/rollback');
    return data;
  }

  // System Management APIs
  async startAllServices(): Promise<ApiResponse> {
    const { data } = await this.client.post('/system/start');
    return data;
  }

  async stopAllServices(): Promise<ApiResponse> {
    const { data } = await this.client.post('/system/stop');
    return data;
  }

  async restartSystem(): Promise<ApiResponse> {
    const { data } = await this.client.post('/system/restart');
    return data;
  }

  async getSystemHealth(): Promise<ApiResponse> {
    const { data } = await this.client.get('/system/health');
    return data;
  }

  async getSystemLogs(filters?: any): Promise<ApiResponse> {
    const { data } = await this.client.get('/system/logs', { params: filters });
    return data;
  }

  async getFeatureFlags(): Promise<ApiResponse> {
    const { data } = await this.client.get('/system/features');
    return data;
  }

  async toggleFeature(featureName: string, enabled: boolean): Promise<ApiResponse> {
    const { data } = await this.client.put(`/system/features/${featureName}`, { enabled });
    return data;
  }

  // Monitoring APIs
  async getSystemMetrics(): Promise<ApiResponse> {
    const { data } = await this.client.get('/monitoring/metrics');
    return data;
  }

  async getErrors(): Promise<ApiResponse> {
    const { data } = await this.client.get('/monitoring/errors');
    return data;
  }

  async exportMetrics(format: 'json' | 'csv'): Promise<ApiResponse> {
    const { data } = await this.client.get(`/monitoring/export?format=${format}`);
    return data;
  }

  async getAlertConfig(): Promise<ApiResponse> {
    const { data } = await this.client.get('/monitoring/alerts');
    return data;
  }

  async updateAlertConfig(config: any): Promise<ApiResponse> {
    const { data } = await this.client.put('/monitoring/alerts', config);
    return data;
  }

  // Configuration APIs
  async getEnvironmentVariables(): Promise<ApiResponse> {
    const { data } = await this.client.get('/config/env');
    return data;
  }

  async updateCredentials(credentials: any): Promise<ApiResponse> {
    const { data } = await this.client.put('/config/credentials', credentials);
    return data;
  }

  async testAPIConnection(service: string): Promise<ApiResponse> {
    const { data } = await this.client.post(`/config/test/${service}`);
    return data;
  }

  async backupConfiguration(): Promise<ApiResponse> {
    const { data } = await this.client.post('/config/backup');
    return data;
  }
}

export default new ApiClient();
