import React, { useState } from 'react';
import { FileText, AlertTriangle, BarChart, Download, Bell } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';
import Alert from './ui/Alert';
import api from '../services/api';

const MonitoringPanel: React.FC = () => {
  const [loading, setLoading] = useState<string | null>(null);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleAction = async (action: string, apiCall: () => Promise<any>) => {
    setLoading(action);
    setAlert(null);
    try {
      const response = await apiCall();
      if (response.success) {
        setAlert({ type: 'success', message: response.message || `${action} completed successfully` });
      } else {
        setAlert({ type: 'error', message: response.error || `${action} failed` });
      }
    } catch (error) {
      setAlert({ type: 'error', message: `Failed to ${action}: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  return (
    <Card title="Monitoring Panel">
      {alert && (
        <Alert type={alert.type} className="mb-4" onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <Button
          variant="primary"
          onClick={() => handleAction('View System Logs', api.getSystemLogs)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <FileText className="w-4 h-4 mr-2" />
          View System Logs
        </Button>

        <Button
          variant="warning"
          onClick={() => handleAction('Error Dashboard', api.getErrors)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <AlertTriangle className="w-4 h-4 mr-2" />
          Error Dashboard
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('Performance Metrics', api.getSystemMetrics)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <BarChart className="w-4 h-4 mr-2" />
          Performance Metrics
        </Button>

        <Button
          variant="success"
          onClick={() => {
            const format = confirm('Export as JSON? (Cancel for CSV)') ? 'json' : 'csv';
            handleAction('Export Metrics', () => api.exportMetrics(format));
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Download className="w-4 h-4 mr-2" />
          Export Metrics
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('Alert Configuration', api.getAlertConfig)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Bell className="w-4 h-4 mr-2" />
          Alert Configuration
        </Button>
      </div>
    </Card>
  );
};

export default MonitoringPanel;
