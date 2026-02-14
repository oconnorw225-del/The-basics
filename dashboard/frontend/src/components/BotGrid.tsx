'use client';

import React from 'react';
import { BotCard } from './BotCard';

interface Bot {
  bot_id: string;
  name: string;
  type: string;
  status?: string;
  capabilities?: string[];
  file_path?: string;
  metadata?: any;
}

interface BotGridProps {
  bots: Bot[];
  onBotAction: (botId: string, action: string) => void;
}

export const BotGrid: React.FC<BotGridProps> = ({ bots, onBotAction }) => {
  if (!bots || bots.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-6xl mb-4">🤖</div>
          <p className="text-gray-500 text-lg">No bots discovered yet</p>
          <p className="text-gray-400 text-sm mt-2">
            Chimera V8 is scanning for bots...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {bots.map((bot) => (
        <BotCard key={bot.bot_id} bot={bot} onAction={onBotAction} />
      ))}
      
      {/* Placeholder for new bots */}
      <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-4 flex items-center justify-center min-h-[200px]">
        <div className="text-center">
          <div className="text-4xl mb-2">➕</div>
          <p className="text-gray-500 text-sm">Space for new bots</p>
          <p className="text-gray-400 text-xs mt-1">
            Auto-discovered bots appear here
          </p>
        </div>
      </div>
    </div>
  );
};

export default BotGrid;
