import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { validateSystem, SystemValidationReport } from '../../utils/systemValidator';
import { performanceOptimizer } from '../../utils/performanceOptimizer';

interface SystemValidationDashboardProps {
  className?: string;
  autoRun?: boolean;
}

const SystemValidationDashboard: React.FC<SystemValidationDashboardProps> = ({
  className = '',
  autoRun = false,
}) => {
  const [validationReport, setValidationReport] = useState<SystemValidationReport | null>(null);
  const [performanceReport, setPerformanceReport] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (autoRun) {
      runValidation();
    }
  }, [autoRun]);

  const runValidation = async () => {
    setIsRunning(true);
    try {
      console.log('🚀 Starting comprehensive system validation...');

      // Run system validation
      const systemReport = await validateSystem();
      setValidationReport(systemReport);

      // Generate performance report
      const perfReport = performanceOptimizer.generateReport();
      setPerformanceReport(perfReport);

      console.log('✅ System validation completed');
      console.log('📊 Validation Report:', systemReport);
      console.log('⚡ Performance Report:', perfReport);

    } catch (error) {
      console.error('❌ Validation failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'degraded':
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical':
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return '✅';
      case 'degraded':
      case 'warning':
        return '⚠️';
      case 'critical':
      case 'error':
        return '🚨';
      default:
        return '❓';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">System Validation Dashboard</h2>
            <p className="text-gray-600 mt-1">
              Comprehensive end-to-end functionality and performance testing
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              {showDetails ? 'Hide Details' : 'Show Details'}
            </button>

            <button
              onClick={runValidation}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isRunning ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Running...</span>
                </>
              ) : (
                <>
                  <span>🔍</span>
                  <span>Run Validation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isRunning && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Running comprehensive system validation...</p>
            <p className="text-sm text-gray-500 mt-2">
              Testing API endpoints, performance metrics, and system capabilities
            </p>
          </motion.div>
        )}

        {/* Results */}
        {!isRunning && (validationReport || performanceReport) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overall Status */}
            {validationReport && (
              <div className={`p-6 rounded-lg border-2 ${
                validationReport.overall_status === 'healthy'
                  ? 'border-green-200 bg-green-50'
                  : validationReport.overall_status === 'degraded'
                  ? 'border-yellow-200 bg-yellow-50'
                  : 'border-red-200 bg-red-50'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl">
                      {getStatusIcon(validationReport.overall_status)}
                    </div>
                    <div>
                      <h3 className={`text-xl font-semibold ${
                        validationReport.overall_status === 'healthy'
                          ? 'text-green-800'
                          : validationReport.overall_status === 'degraded'
                          ? 'text-yellow-800'
                          : 'text-red-800'
                      }`}>
                        System Status: {validationReport.overall_status.toUpperCase()}
                      </h3>
                      <p className={`text-sm ${
                        validationReport.overall_status === 'healthy'
                          ? 'text-green-600'
                          : validationReport.overall_status === 'degraded'
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}>
                        {validationReport.passed_tests}/{validationReport.total_tests} tests passed
                        {validationReport.failed_tests > 0 && ` • ${validationReport.failed_tests} failed`}
                        {validationReport.warning_tests > 0 && ` • ${validationReport.warning_tests} warnings`}
                      </p>
                    </div>
                  </div>

                  {performanceReport && (
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${getScoreColor(performanceReport.score)}`}>
                        {performanceReport.score}
                      </div>
                      <div className="text-sm text-gray-600">Performance Score</div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Quick Stats */}
            {validationReport && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-blue-600">
                    {validationReport.total_tests}
                  </div>
                  <div className="text-sm text-blue-800">Total Tests</div>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-green-600">
                    {validationReport.passed_tests}
                  </div>
                  <div className="text-sm text-green-800">Passed</div>
                </div>

                <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-yellow-600">
                    {validationReport.warning_tests}
                  </div>
                  <div className="text-sm text-yellow-800">Warnings</div>
                </div>

                <div className="bg-red-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-red-600">
                    {validationReport.failed_tests}
                  </div>
                  <div className="text-sm text-red-800">Failed</div>
                </div>
              </div>
            )}

            {/* Performance Metrics */}
            {performanceReport && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Performance Metrics</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">
                      {performanceReport.metrics.fps?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">FPS</div>
                  </div>

                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">
                      {performanceReport.metrics.memory_usage
                        ? `${(performanceReport.metrics.memory_usage * 100).toFixed(1)}%`
                        : 'N/A'
                      }
                    </div>
                    <div className="text-sm text-gray-600">Memory Usage</div>
                  </div>

                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">
                      {validationReport?.average_response_time || 'N/A'}ms
                    </div>
                    <div className="text-sm text-gray-600">Avg Response Time</div>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {validationReport && validationReport.recommendations.length > 0 && (
              <div className="bg-blue-50 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Recommendations</h4>
                <div className="space-y-2">
                  {validationReport.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <span className="text-blue-600 mt-0.5">💡</span>
                      <span className="text-sm text-gray-700">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Performance Recommendations */}
            {performanceReport && performanceReport.recommendations.length > 0 && (
              <div className="bg-purple-50 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Performance Recommendations</h4>
                <div className="space-y-3">
                  {performanceReport.recommendations.map((rec: any, index: number) => (
                    <div key={index} className="border-l-4 border-purple-400 pl-4">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                          rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {rec.priority.toUpperCase()}
                        </span>
                        <span className="font-medium text-gray-900">{rec.title}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                      <p className="text-xs text-gray-500 mt-1">{rec.implementation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Results */}
            <AnimatePresence>
              {showDetails && validationReport && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-gray-50 rounded-lg p-6"
                >
                  <h4 className="font-semibold text-gray-900 mb-4">Detailed Test Results</h4>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {validationReport.results.map((result, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">{getStatusIcon(result.status)}</span>
                          <div>
                            <div className="font-medium text-gray-900">{result.endpoint}</div>
                            <div className="text-sm text-gray-600">{result.message}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900">
                            {result.responseTime}ms
                          </div>
                          {result.error && (
                            <div className="text-xs text-red-600">{result.error}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Timestamp */}
            {validationReport && (
              <div className="text-center text-xs text-gray-500">
                Last validated: {new Date(validationReport.timestamp).toLocaleString()}
              </div>
            )}
          </motion.div>
        )}

        {/* Initial State */}
        {!isRunning && !validationReport && !performanceReport && (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Ready to Validate System
            </h3>
            <p className="text-gray-600 mb-6">
              Run comprehensive tests to validate all API endpoints, performance metrics, and system capabilities.
            </p>
            <button
              onClick={runValidation}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Validation
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemValidationDashboard;
