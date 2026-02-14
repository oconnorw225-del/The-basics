'use client';

import React from 'react';

interface BotCardProps {
  bot: {
    bot_id: string;
    name: string;
    type: string;
    status?: string;
    capabilities?: string[];
    file_path?: string;
    metadata?: any;
  };
  onAction: (botId: string, action: string) => void;
}

export const BotCard: React.FC<BotCardProps> = ({ bot, onAction }) => {
  const statusColors: Record<string, string> = {
    active: 'bg-green-500',
    inactive: 'bg-gray-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
  };

  const typeColors: Record<string, string> = {
    trading: 'bg-blue-100 text-blue-800',
    ai_trader: 'bg-purple-100 text-purple-800',
    monitoring: 'bg-green-100 text-green-800',
    recovery: 'bg-yellow-100 text-yellow-800',
    orchestrator: 'bg-red-100 text-red-800',
    freelance: 'bg-indigo-100 text-indigo-800',
    autonomous: 'bg-gray-100 text-gray-800',
  };

  const status = bot.status || 'inactive';
  const botType = bot.type || 'autonomous';

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-900 truncate">
            {bot.name}
          </h3>
          <p className="text-xs text-gray-500 truncate mt-1">
            {bot.bot_id}
          </p>
        </div>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            typeColors[botType] || typeColors.autonomous
          }`}
        >
          {botType}
        </span>
      </div>

      {/* Status */}
      <div className="flex items-center gap-2 mb-3">
        <div
          className={`w-3 h-3 rounded-full ${
            statusColors[status] || statusColors.inactive
          }`}
        />
        <span className="text-sm text-gray-600 capitalize">{status}</span>
      </div>

      {/* Capabilities */}
      {bot.capabilities && bot.capabilities.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {bot.capabilities.slice(0, 3).map((capability) => (
              <span
                key={capability}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
              >
                {capability}
              </span>
            ))}
            {bot.capabilities.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                +{bot.capabilities.length - 3}
              </span>
            )}
          </div>
        </div>
      )}

      {/* File Path */}
      {bot.file_path && (
        <p className="text-xs text-gray-400 mb-3 truncate">
          📁 {bot.file_path}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => onAction(bot.bot_id, 'start')}
          className="flex-1 px-3 py-1.5 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors"
          disabled={status === 'active'}
        >
          Start
        </button>
        <button
          onClick={() => onAction(bot.bot_id, 'stop')}
          className="flex-1 px-3 py-1.5 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
          disabled={status === 'inactive'}
        >
          Stop
        </button>
        <button
          onClick={() => onAction(bot.bot_id, 'restart')}
          className="flex-1 px-3 py-1.5 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
        >
          Restart
        </button>
      </div>
    </div>
  );
};

export default BotCard;
