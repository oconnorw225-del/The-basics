const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    service: 'NDAX Quantum Engine',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// API proxy to Python backend (if running)
app.use('/api', (req, res) => {
  const pythonBackend = process.env.PYTHON_PORT || 8000;
  res.status(503).json({
    error: 'Python backend not available',
    message: `Start Python backend on port ${pythonBackend}`,
    endpoints: {
      frontend: `http://localhost:${PORT}`,
      backend: `http://localhost:${pythonBackend}`,
      bot: `http://localhost:${process.env.BOT_PORT || 9000}`
    }
  });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NDAX Quantum Engine running on port ${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}`);
  console.log(`❤️  Health check: http://localhost:${PORT}/health`);
});

