import React, { useState } from 'react';
import { Play, Square, History, TrendingUp, AlertOctagon, Eye } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';
import Alert from './ui/Alert';
import api from '../services/api';

const TradingControlPanel: React.FC = () => {
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
    <Card title="Trading Control Panel">
      {alert && (
        <Alert type={alert.type} className="mb-4" onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <Button
          variant="success"
          onClick={() => handleAction('Start Trading Bot', api.startTrading)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Play className="w-4 h-4 mr-2" />
          {loading === 'Start Trading Bot' ? 'Starting...' : 'Start Trading Bot'}
        </Button>

        <Button
          variant="danger"
          onClick={() => confirmAction('stop trading bot', () => handleAction('Stop Trading Bot', api.stopTrading))}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Square className="w-4 h-4 mr-2" />
          {loading === 'Stop Trading Bot' ? 'Stopping...' : 'Stop Trading Bot'}
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View Trading History', api.getTradingHistory)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <History className="w-4 h-4 mr-2" />
          View Trading History
        </Button>

        <Button
          variant="primary"
          onClick={() => {
            const pair = prompt('Enter trading pair (e.g., BTC/USD):');
            const type = prompt('Enter trade type (buy/sell):');
            const amount = prompt('Enter amount:');
            if (pair && type && amount) {
              handleAction('Manual Trade Entry', () =>
                api.executeTrade({ pair, type, amount: parseFloat(amount) })
              );
            }
          }}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          Manual Trade Entry
        </Button>

        <Button
          variant="primary"
          onClick={() => handleAction('View Open Positions', api.getTradingPositions)}
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <Eye className="w-4 h-4 mr-2" />
          View Open Positions
        </Button>

        <Button
          variant="danger"
          onClick={() =>
            confirmAction('emergency stop all trading', () =>
              handleAction('Emergency Stop All', api.emergencyStopAll)
            )
          }
          disabled={loading !== null}
          className="flex items-center justify-center"
        >
          <AlertOctagon className="w-4 h-4 mr-2" />
          Emergency Stop All
        </Button>
      </div>
    </Card>
  );
};

export default TradingControlPanel;
