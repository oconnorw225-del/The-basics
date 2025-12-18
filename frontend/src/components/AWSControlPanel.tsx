import React, { useState } from 'react';
import { Cloud, Activity, Heart, FileText, TrendingUp, RotateCcw } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';
import Alert from './ui/Alert';
import api from '../services/api';

const AWSControlPanel: React.FC = () => {
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
    <Card title="AWS Deployment Panel">
      {alert && (
        <Alert type={alert.type} className="mb-4" onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <Button
          variant="primary"
          onClick={() =>
            confirmAction('deploy to AWS', () => handleAction('Deploy to AWS', api.deployToAWS))
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Cloud className="w-4 h-4 mr-2" />
          {loading === 'Deploy to AWS' ? 'Deploying...' : 'Deploy to AWS'}
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View Deployment Status', api.getDeploymentStatus)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Activity className="w-4 h-4 mr-2" />
          View Deployment Status
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('Health Check AWS', api.healthCheckAWS)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Heart className="w-4 h-4 mr-2" />
          Health Check AWS
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View CloudWatch Logs', api.getCloudWatchLogs)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <FileText className="w-4 h-4 mr-2" />
          View CloudWatch Logs
        </Button>

        <Button
          variant="warning"
          onClick={() => {
            const count = prompt('Enter desired task count:');
            if (count) {
              handleAction('Scale ECS Services', () =>
                api.scaleECSServices({ desiredCount: parseInt(count) })
              );
            }
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          Scale ECS Services
        </Button>

        <Button
          variant="danger"
          onClick={() =>
            confirmAction('rollback deployment', () =>
              handleAction('Rollback Deployment', api.rollbackDeployment)
            )
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Rollback Deployment
        </Button>
      </div>
    </Card>
  );
};

export default AWSControlPanel;
