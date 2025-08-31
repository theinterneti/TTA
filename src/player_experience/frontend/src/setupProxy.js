/**
 * Create React App Proxy Configuration
 *
 * This file configures the development server proxy to route API calls
 * to the TTA Player Experience API backend running on port 8080.
 */

const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API routes to the backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      onProxyReq: (proxyReq, req, res) => {
        // Log API requests in development
        console.log(`🔄 Proxying ${req.method} ${req.url} to backend`);
      },
      onProxyRes: (proxyRes, req, res) => {
        // Log API responses in development
        console.log(`✅ Backend responded with ${proxyRes.statusCode} for ${req.url}`);
      },
      onError: (err, req, res) => {
        console.error('❌ Proxy error:', err.message);
        res.status(500).json({
          error: 'Proxy Error',
          message: 'Failed to connect to backend API',
          details: err.message
        });
      }
    })
  );

  // Proxy health check endpoint
  app.use(
    '/health',
    createProxyMiddleware({
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      logLevel: 'info'
    })
  );

  // Proxy WebSocket connections for real-time features
  app.use(
    '/ws',
    createProxyMiddleware({
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      ws: true, // Enable WebSocket proxying
      logLevel: 'info',
      onProxyReqWs: (proxyReq, req, socket, options, head) => {
        console.log('🔌 WebSocket connection proxied to backend');
      },
      onError: (err, req, res) => {
        console.error('❌ WebSocket proxy error:', err.message);
      }
    })
  );

  // Proxy metrics endpoint (if available)
  app.use(
    '/metrics',
    createProxyMiddleware({
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      logLevel: 'info'
    })
  );

  // Development-only: Proxy docs endpoints
  if (process.env.NODE_ENV === 'development') {
    app.use(
      '/docs',
      createProxyMiddleware({
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        logLevel: 'info'
      })
    );

    app.use(
      '/openapi.json',
      createProxyMiddleware({
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        logLevel: 'info'
      })
    );
  }
};
