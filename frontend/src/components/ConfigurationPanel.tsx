import React, { useState } from 'react';
import { Eye, Key, ToggleLeft, Wifi, Archive } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';
import Alert from './ui/Alert';
import api from '../services/api';

const ConfigurationPanel: React.FC = () => {
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
    <Card title="Configuration Panel">
      {alert && (
        <Alert type={alert.type} className="mb-4" onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <Button
          variant="primary"
          onClick={() => handleAction('View Environment Variables', api.getEnvironmentVariables)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Eye className="w-4 h-4 mr-2" />
          View Environment Variables
        </Button>

        <Button
          variant="warning"
          onClick={() => {
            const credentials = prompt('Enter credentials (JSON):');
            if (credentials) {
              try {
                const creds = JSON.parse(credentials);
                confirmAction('update credentials', () =>
                  handleAction('Update Credentials', () => api.updateCredentials(creds))
                );
              } catch {
                setAlert({ type: 'error', message: 'Invalid JSON format' });
              }
            }
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Key className="w-4 h-4 mr-2" />
          Update Credentials
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('Feature Flags Management', api.getFeatureFlags)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <ToggleLeft className="w-4 h-4 mr-2" />
          Feature Flags Management
        </Button>

        <Button
          variant="primary"
          onClick={() => {
            const service = prompt('Enter service name to test (e.g., trading, ai, aws):');
            if (service) {
              handleAction('Test API Connection', () => api.testAPIConnection(service));
            }
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Wifi className="w-4 h-4 mr-2" />
          Test API Connections
        </Button>

        <Button
          variant="success"
          onClick={() =>
            confirmAction('backup configuration', () =>
              handleAction('Backup Configuration', api.backupConfiguration)
            )
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Archive className="w-4 h-4 mr-2" />
          Backup Configuration
        </Button>
      </div>
    </Card>
  );
};

export default ConfigurationPanel;
