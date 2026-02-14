'use client';

import React, { useState, useEffect } from 'react';
import { BotGrid } from '../components/BotGrid';
import { useWebSocket } from '../hooks/useWebSocket';

interface Bot {
  bot_id: string;
  name: string;
  type: string;
  status?: string;
  capabilities?: string[];
  file_path?: string;
  metadata?: any;
}

interface Stats {
  bots?: {
    total_bots?: number;
    bots_by_type?: Record<string, number>;
  };
  credentials?: {
    total_credentials?: number;
    pending_requests?: number;
  };
  recovery?: {
    total_scans?: number;
    total_recovered?: number;
    total_value?: number;
  };
  notifications?: {
    pending?: number;
    sent_today?: number;
    recipient?: string;
  };
}

export default function DashboardPage() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [stats, setStats] = useState<Stats>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection
  const { isConnected, lastMessage } = useWebSocket('ws://localhost:8000/ws');

  // Fetch initial data
  useEffect(() => {
    fetchBots();
    fetchStats();
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'stats_update') {
        setStats(lastMessage.data);
      } else if (lastMessage.type === 'bot_status_update') {
        // Update specific bot status
        setBots((prevBots) =>
          prevBots.map((bot) =>
            bot.bot_id === lastMessage.bot_id
              ? { ...bot, status: lastMessage.status }
              : bot
          )
        );
      }
    }
  }, [lastMessage]);

  const fetchBots = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/bots');
      const data = await response.json();
      setBots(data.bots || []);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch bots');
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleBotAction = async (botId: string, action: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/bots/${botId}/${action}`,
        {
          method: 'POST',
        }
      );

      if (response.ok) {
        // Refresh bots
        await fetchBots();
      }
    } catch (err) {
      console.error(`Failed to ${action} bot:`, err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-600">❌ {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🚀 Autonomous Bot Dashboard
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Real-time monitoring and control
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Panel */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Bots</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.bots?.total_bots || 0}
                </p>
              </div>
              <div className="text-4xl">🤖</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Credentials</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.credentials?.total_credentials || 0}
                </p>
              </div>
              <div className="text-4xl">🔐</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Recovery Scans</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.recovery?.total_scans || 0}
                </p>
              </div>
              <div className="text-4xl">💰</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Notifications</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.notifications?.pending || 0}
                </p>
              </div>
              <div className="text-4xl">📧</div>
            </div>
          </div>
        </div>

        {/* Bot Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Bot Grid ({bots.length} bots)
            </h2>
            <button
              onClick={fetchBots}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              🔄 Refresh
            </button>
          </div>
          <BotGrid bots={bots} onBotAction={handleBotAction} />
        </div>

        {/* System Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            System Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Email Recipient</p>
              <p className="font-mono text-gray-900">
                {stats.notifications?.recipient || 'oconnorw225@gmail.com'}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Assets Recovered</p>
              <p className="font-mono text-gray-900">
                {stats.recovery?.total_recovered || 0} (${stats.recovery?.total_value || 0})
              </p>
            </div>
            <div>
              <p className="text-gray-500">Pending Credential Requests</p>
              <p className="font-mono text-gray-900">
                {stats.credentials?.pending_requests || 0}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Notifications Sent Today</p>
              <p className="font-mono text-gray-900">
                {stats.notifications?.sent_today || 0}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Autonomous Bot System v1.0 • Powered by Chimera V8 • Email:{' '}
            <span className="font-mono">oconnorw225@gmail.com</span>
          </p>
        </div>
      </main>
    </div>
  );
}
