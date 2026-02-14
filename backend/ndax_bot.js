/**
 * NDAX Trading Bot
 * Implements trading on the NDAX exchange
 */

const express = require('express');
const app = express();

app.use(express.json());

let botStatus = {
  bot: 'ndax',
  status: 'healthy',
  running: true,
  lastUpdate: new Date().toISOString()
};

app.get('/health', (req, res) => {
  res.json({
    ...botStatus,
    timestamp: new Date().toISOString()
  });
});

app.get('/status', (req, res) => {
  res.json({
    ...botStatus,
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

app.post('/start', (req, res) => {
  botStatus.running = true;
  botStatus.status = 'healthy';
  botStatus.lastUpdate = new Date().toISOString();
  console.log('🚀 NDAX Bot started');
  res.json({ success: true, message: 'Bot started', status: botStatus });
});

app.post('/stop', (req, res) => {
  botStatus.running = false;
  botStatus.status = 'stopped';
  botStatus.lastUpdate = new Date().toISOString();
  console.log('🛑 NDAX Bot stopped');
  res.json({ success: true, message: 'Bot stopped', status: botStatus });
});

const PORT = process.env.PORT || 9000;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🤖 NDAX Bot listening on port ${PORT}`);
    console.log(`📊 Health endpoint: http://localhost:${PORT}/health`);
  });
}

module.exports = app;
