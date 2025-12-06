const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }));
        return;
    }
    
    if (req.url === '/' || req.url === '/index.html') {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end('<html><body><h1>Unified System</h1><p>System Operational</p></body></html>');
        return;
    }
    
    res.writeHead(404);
    res.end('Not Found');
});

server.listen(PORT, '0.0.0.0', () => {
    console.log('Server running on port ' + PORT);
});

// Set server timeout to 5 minutes for long-running operations
// (e.g., dashboard loading, Python system initialization)
server.setTimeout(300000);
