import React, { useState } from 'react';
import { PlayCircle, StopCircle, RotateCw, FileText, Activity, ToggleLeft } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';
import Alert from './ui/Alert';
import api from '../services/api';

const SystemManagementPanel: React.FC = () => {
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

  const confirmAction = (action: string, callback: () => void) => {
    if (window.confirm(`Are you sure you want to ${action}?`)) {
      callback();
    }
  };

  return (
    <Card title="System Management Panel">
      {alert && (
        <Alert type={alert.type} className="mb-4" onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <Button
          variant="success"
          onClick={() =>
            confirmAction('start all services', () =>
              handleAction('Start All Services', api.startAllServices)
            )
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <PlayCircle className="w-4 h-4 mr-2" />
          {loading === 'Start All Services' ? 'Starting...' : 'Start All Services'}
        </Button>

        <Button
          variant="danger"
          onClick={() =>
            confirmAction('stop all services', () =>
              handleAction('Stop All Services', api.stopAllServices)
            )
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <StopCircle className="w-4 h-4 mr-2" />
          {loading === 'Stop All Services' ? 'Stopping...' : 'Stop All Services'}
        </Button>

        <Button
          variant="warning"
          onClick={() =>
            confirmAction('restart system', () => handleAction('Restart System', api.restartSystem))
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <RotateCw className="w-4 h-4 mr-2" />
          {loading === 'Restart System' ? 'Restarting...' : 'Restart System'}
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View Logs', api.getSystemLogs)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <FileText className="w-4 h-4 mr-2" />
          View Logs
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('Health Check All', api.getSystemHealth)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Activity className="w-4 h-4 mr-2" />
          Health Check All
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('Feature Toggles', api.getFeatureFlags)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <ToggleLeft className="w-4 h-4 mr-2" />
          Feature Toggles
        </Button>
      </div>
    </Card>
  );
};

export default SystemManagementPanel;
