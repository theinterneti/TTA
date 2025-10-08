/**
 * CRACO Configuration for TTA Player Experience Frontend
 *
 * This configuration overrides Create React App's webpack-dev-server settings
 * to fix compatibility issues between react-scripts 5.0.1 and webpack-dev-server 5.2.1.
 *
 * Issues Fixed:
 * 1. react-scripts uses deprecated `onBeforeSetupMiddleware` and `onAfterSetupMiddleware`
 *    which were removed in webpack-dev-server v5 in favor of `setupMiddlewares`.
 * 2. react-scripts uses deprecated `https` option which was moved to `server` option in v5.
 *
 * Solution: This config intercepts the devServer configuration and migrates both the middleware
 * setup and HTTPS configuration to use the new webpack-dev-server v5 API.
 *
 * References:
 * - webpack-dev-server v5 migration guide: https://github.com/webpack/webpack-dev-server/blob/master/migration-v5.md
 * - CRACO devServer docs: https://craco.js.org/docs/configuration/devserver/
 */

const fs = require('fs');
const evalSourceMapMiddleware = require('react-dev-utils/evalSourceMapMiddleware');
const noopServiceWorkerMiddleware = require('react-dev-utils/noopServiceWorkerMiddleware');
const redirectServedPath = require('react-dev-utils/redirectServedPathMiddleware');
const paths = require('react-scripts/config/paths');

module.exports = {
  devServer: (devServerConfig, { env, paths: cracoPath, proxy, allowedHost }) => {
    // Store the original middleware functions before we delete them
    const onBeforeSetupMiddleware = devServerConfig.onBeforeSetupMiddleware;
    const onAfterSetupMiddleware = devServerConfig.onAfterSetupMiddleware;

    // Remove the deprecated properties
    delete devServerConfig.onBeforeSetupMiddleware;
    delete devServerConfig.onAfterSetupMiddleware;

    // Migrate 'https' option to 'server' option (webpack-dev-server v5 change)
    // In v4: { https: true } or { https: { key, cert } }
    // In v5: { server: 'https' } or { server: { type: 'https', options: { key, cert } } }
    if (devServerConfig.https !== undefined) {
      const httpsValue = devServerConfig.https;
      delete devServerConfig.https;

      if (typeof httpsValue === 'boolean') {
        // Simple boolean case: https: true -> server: 'https'
        devServerConfig.server = httpsValue ? 'https' : 'http';
      } else if (typeof httpsValue === 'object') {
        // Object case with cert/key: https: { key, cert } -> server: { type: 'https', options: { key, cert } }
        devServerConfig.server = {
          type: 'https',
          options: httpsValue
        };
      }
    }

    // Add the new setupMiddlewares function that replicates the original behavior
    devServerConfig.setupMiddlewares = (middlewares, devServer) => {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }

      // Replicate onBeforeSetupMiddleware behavior
      // Use devServer.app.use() for middleware that needs to run before webpack-dev-server's middleware
      // This is the correct approach for middleware that doesn't fit the middleware array pattern

      // Keep `evalSourceMapMiddleware` before `redirectServedPath`
      // This lets us fetch source contents from webpack for the error overlay
      devServer.app.use(evalSourceMapMiddleware(devServer));

      // Load custom proxy setup if it exists
      if (fs.existsSync(paths.proxySetup)) {
        // This registers user provided middleware for proxy reasons
        require(paths.proxySetup)(devServer.app);
      }

      // The default webpack-dev-server middlewares run here (in the middle)
      // This includes static file serving, HMR, etc.

      // Replicate onAfterSetupMiddleware behavior
      // Use devServer.app.use() for middleware that needs to run after webpack-dev-server's middleware
      devServer.app.use(redirectServedPath(paths.publicUrlOrPath));
      devServer.app.use(noopServiceWorkerMiddleware(paths.publicUrlOrPath));

      return middlewares;
    };

    return devServerConfig;
  },
};
