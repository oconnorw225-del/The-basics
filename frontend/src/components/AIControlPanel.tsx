import React, { useState } from 'react';
import { Play, Square, ListTodo, Plus, Clock, Settings } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';
import Alert from './ui/Alert';
import api from '../services/api';

const AIControlPanel: React.FC = () => {
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
    <Card title="AI/Freelance Control Panel">
      {alert && (
        <Alert type={alert.type} className="mb-4" onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <Button
          variant="success"
          onClick={() => handleAction('Start AI Bot', api.startAI)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Play className="w-4 h-4 mr-2" />
          {loading === 'Start AI Bot' ? 'Starting...' : 'Start AI Bot'}
        </Button>

        <Button
          variant="danger"
          onClick={() => handleAction('Stop AI Bot', api.stopAI)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Square className="w-4 h-4 mr-2" />
          {loading === 'Stop AI Bot' ? 'Stopping...' : 'Stop AI Bot'}
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View Active Tasks', api.getActiveTasks)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <ListTodo className="w-4 h-4 mr-2" />
          View Active Tasks
        </Button>

        <Button
          variant="primary"
          onClick={() => {
            const title = prompt('Enter task title:');
            const provider = prompt('Enter provider (MTurk, Appen, etc.):');
            if (title && provider) {
              handleAction('Submit New Task', () =>
                api.submitTask({ title, provider, priority: 1 })
              );
            }
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Submit New Task
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View Task Queue', api.getTaskQueue)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Clock className="w-4 h-4 mr-2" />
          View Task Queue
        </Button>

        <Button
          variant="primary"
          onClick={() => {
            const providers = prompt('Enter providers config (JSON):');
            if (providers) {
              try {
                const config = JSON.parse(providers);
                handleAction('Configure Providers', () => api.configureProviders(config));
              } catch {
                setAlert({ type: 'error', message: 'Invalid JSON format' });
              }
            }
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Settings className="w-4 h-4 mr-2" />
          Configure Providers
        </Button>
      </div>
    </Card>
  );
};

export default AIControlPanel;
