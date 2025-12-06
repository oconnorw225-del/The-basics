const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  // Set timeout and handle errors
  req.setTimeout(30000); // 30 second timeout
  
  if (req.url === '/' || req.url === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Basics - Repository Consolidation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 20px;
        }
        ul {
            list-style-type: none;
            padding-left: 0;
        }
        li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        li:before {
            content: "✓ ";
            color: #4CAF50;
            font-weight: bold;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            background: #4CAF50;
            color: white;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 The Basics</h1>
        <div class="status">Railway Deployment Active</div>
        
        <h2>Automated Consolidation System</h2>
        <p>This repository consolidates the best parts from:</p>
        <ul>
            <li>ndax-quantum-engine</li>
            <li>quantum-engine-dashb</li>
            <li>shadowforge-ai-trader</li>
            <li>repository-web-app</li>
            <li>The-new-ones</li>
        </ul>

        <h2>How To Use</h2>
        <ol>
            <li>Go to your repository's <strong>Actions</strong> tab</li>
            <li>Select <strong>Consolidate Best Parts</strong> from the workflows list</li>
            <li>Click <strong>Run workflow</strong> to consolidate your code</li>
            <li>Review and use your unified repo!</li>
        </ol>

        <h2>Repository Contents</h2>
        <ul>
            <li><code>/api</code> — consolidated APIs</li>
            <li><code>/backend</code> — backend logic</li>
            <li><code>/frontend</code> — UI components</li>
            <li><code>/docs</code> — documentation</li>
            <li><code>/tests</code> — test suites</li>
            <li><code>/automation</code> — scripts for consolidation</li>
        </ul>
    </div>
</body>
</html>
    `);
  } else if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }));
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Application is ready to accept connections`);
});
