import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  BellIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import { performanceBaselineManager, PerformanceBaseline, PerformanceRegression, PerformanceAlert, PerformanceTrend } from '../../services/PerformanceBaselineManager';

export const PerformanceBaselineDashboard: React.FC = () => {
  const [baselines, setBaselines] = useState<PerformanceBaseline[]>([]);
  const [regressions, setRegressions] = useState<PerformanceRegression[]>([]);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [selectedInterface, setSelectedInterface] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [trends, setTrends] = useState<Map<string, PerformanceTrend>>(new Map());

  useEffect(() => {
    // Load initial data
    loadDashboardData();

    // Set up event listeners
    const handleMetricRecorded = () => {
      loadDashboardData();
    };

    const handleRegressionDetected = (regression: PerformanceRegression) => {
      setRegressions(prev => [...prev, regression]);
    };

    const handleAlertCreated = (alert: PerformanceAlert) => {
      setAlerts(prev => [...prev, alert]);
    };

    performanceBaselineManager.on('metric_recorded', handleMetricRecorded);
    performanceBaselineManager.on('regression_detected', handleRegressionDetected);
    performanceBaselineManager.on('alert_created', handleAlertCreated);

    return () => {
      performanceBaselineManager.off('metric_recorded', handleMetricRecorded);
      performanceBaselineManager.off('regression_detected', handleRegressionDetected);
      performanceBaselineManager.off('alert_created', handleAlertCreated);
    };
  }, []);

  useEffect(() => {
    // Generate trend analysis when time range changes
    generateTrendAnalysis();
  }, [selectedTimeRange, baselines]);

  const loadDashboardData = () => {
    setBaselines(performanceBaselineManager.getAllBaselines());
    setRegressions(performanceBaselineManager.getRegressions());
    setAlerts(performanceBaselineManager.getAlerts(false)); // Only unacknowledged alerts
  };

  const generateTrendAnalysis = () => {
    const newTrends = new Map<string, PerformanceTrend>();

    baselines.forEach(baseline => {
      Object.keys(baseline.metrics).forEach(metricName => {
        const trend = performanceBaselineManager.generateTrendAnalysis(
          baseline.interfaceId,
          metricName,
          selectedTimeRange
        );

        if (trend) {
          newTrends.set(`${baseline.interfaceId}_${metricName}`, trend);
        }
      });
    });

    setTrends(newTrends);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-red-500 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingDownIcon className="h-4 w-4 text-green-500" />;
      case 'degrading': return <TrendingUpIcon className="h-4 w-4 text-red-500" />;
      default: return <div className="h-4 w-4 bg-gray-400 rounded-full" />;
    }
  };

  const formatValue = (value: number, unit: string) => {
    if (unit === 'ms') {
      return `${value.toFixed(1)}ms`;
    } else if (unit === 'bytes') {
      return formatBytes(value);
    } else {
      return `${value.toFixed(2)} ${unit}`;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const acknowledgeAlert = (alertId: string) => {
    performanceBaselineManager.acknowledgeAlert(alertId, 'developer');
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const selectedBaseline = selectedInterface ? baselines.find(b => b.interfaceId === selectedInterface) : null;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Performance Baseline Dashboard</h3>
            <p className="text-sm text-gray-600">Monitor performance trends and detect regressions</p>
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-3 py-1"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>

            <div className="flex items-center space-x-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span className="text-gray-600">Recording Active</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="p-4 space-y-6">
          {/* Alerts Section */}
          {alerts.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-4">
                <BellIcon className="h-5 w-5 text-red-600" />
                <h4 className="font-medium text-gray-900">Active Alerts ({alerts.length})</h4>
              </div>

              <div className="space-y-2">
                {alerts.slice(0, 5).map(alert => (
                  <motion.div
                    key={alert.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      alert.severity === 'critical' ? 'border-red-200 bg-red-50' :
                      alert.severity === 'high' ? 'border-red-100 bg-red-25' :
                      alert.severity === 'medium' ? 'border-yellow-200 bg-yellow-50' :
                      'border-blue-200 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <ExclamationTriangleIcon className={`h-4 w-4 ${
                        alert.severity === 'critical' ? 'text-red-600' :
                        alert.severity === 'high' ? 'text-red-500' :
                        alert.severity === 'medium' ? 'text-yellow-600' :
                        'text-blue-600'
                      }`} />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{alert.message}</div>
                        <div className="text-xs text-gray-600">{new Date(alert.createdAt).toLocaleString()}</div>
                      </div>
                    </div>

                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Acknowledge
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Interface Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {baselines.map(baseline => {
              const interfaceRegressions = regressions.filter(r => r.interfaceId === baseline.interfaceId && !r.isResolved);
              const hasRegressions = interfaceRegressions.length > 0;

              return (
                <motion.div
                  key={baseline.interfaceId}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`bg-white rounded-lg border p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedInterface === baseline.interfaceId ? 'border-blue-500 shadow-md' : 'border-gray-200'
                  } ${hasRegressions ? 'border-l-4 border-l-red-500' : ''}`}
                  onClick={() => setSelectedInterface(baseline.interfaceId)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{baseline.interfaceName}</h4>
                    {hasRegressions ? (
                      <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
                    ) : (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Metrics:</span>
                      <span className="font-medium">{Object.keys(baseline.metrics).length}</span>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Regressions:</span>
                      <span className={`font-medium ${hasRegressions ? 'text-red-600' : 'text-green-600'}`}>
                        {interfaceRegressions.length}
                      </span>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Created:</span>
                      <span className="text-gray-500">{new Date(baseline.createdAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Detailed View */}
          {selectedBaseline && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium text-gray-900">{selectedBaseline.interfaceName} - Detailed Metrics</h4>
                <button
                  onClick={() => setSelectedInterface(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <EyeSlashIcon className="h-5 w-5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(selectedBaseline.metrics).map(([metricName, metricData]) => {
                  const trendKey = `${selectedBaseline.interfaceId}_${metricName}`;
                  const trend = trends.get(trendKey);
                  const regression = regressions.find(r =>
                    r.interfaceId === selectedBaseline.interfaceId &&
                    r.metricName === metricName &&
                    !r.isResolved
                  );

                  return (
                    <div
                      key={metricName}
                      className={`p-3 rounded-lg border ${
                        regression ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="text-sm font-medium text-gray-900 capitalize">
                          {metricName.replace('_', ' ')}
                        </h5>
                        {trend && getTrendIcon(trend.trend)}
                      </div>

                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Baseline:</span>
                          <span className="font-medium">{formatValue(metricData.baseline, metricData.unit)}</span>
                        </div>

                        <div className="flex justify-between">
                          <span className="text-gray-600">P95:</span>
                          <span className="text-gray-700">{formatValue(metricData.percentiles.p95, metricData.unit)}</span>
                        </div>

                        <div className="flex justify-between">
                          <span className="text-gray-600">Samples:</span>
                          <span className="text-gray-700">{metricData.samples}</span>
                        </div>

                        {regression && (
                          <div className="mt-2 p-2 bg-red-100 rounded text-xs">
                            <div className="font-medium text-red-800">Regression Detected</div>
                            <div className="text-red-700">+{regression.regressionPercentage.toFixed(1)}%</div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* No Data State */}
          {baselines.length === 0 && (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <div className="text-center">
                <ChartBarIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <div className="text-lg font-medium">No Performance Baselines</div>
                <div className="text-sm">Baselines will be created automatically as metrics are collected</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
