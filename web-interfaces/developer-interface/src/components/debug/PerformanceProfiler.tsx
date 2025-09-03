import React, { useState, useMemo, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  ClockIcon,
  CpuChipIcon,
  CircleStackIcon,
  ArrowPathIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useAppSelector, useAppDispatch } from '../../store/store';
import { addPerformanceMetric, addMemoryUsage } from '../../store/slices/debugSlice';

export const PerformanceProfiler: React.FC = () => {
  const dispatch = useAppDispatch();
  const { performanceMetrics, memoryUsage } = useAppSelector(state => state.debug);
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(true);

  // Collect performance metrics
  useEffect(() => {
    if (!isRecording) return;

    const collectMetrics = () => {
      // Memory usage
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        dispatch(addMemoryUsage({
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit,
          timestamp: new Date().toISOString(),
        }));
      }

      // Navigation timing
      if ('getEntriesByType' in performance) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          dispatch(addPerformanceMetric({
            name: 'Page Load Time',
            value: navigation.loadEventEnd - navigation.navigationStart,
            unit: 'ms',
            timestamp: new Date().toISOString(),
            interfaceId: 'developer',
          }));

          dispatch(addPerformanceMetric({
            name: 'DOM Content Loaded',
            value: navigation.domContentLoadedEventEnd - navigation.navigationStart,
            unit: 'ms',
            timestamp: new Date().toISOString(),
            interfaceId: 'developer',
          }));
        }

        // Resource timing
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        resources.slice(-5).forEach(resource => {
          dispatch(addPerformanceMetric({
            name: `Resource: ${resource.name.split('/').pop() || 'Unknown'}`,
            value: resource.responseEnd - resource.requestStart,
            unit: 'ms',
            timestamp: new Date().toISOString(),
            interfaceId: 'developer',
          }));
        });
      }
    };

    const interval = setInterval(collectMetrics, 5000);
    collectMetrics(); // Initial collection

    return () => clearInterval(interval);
  }, [dispatch, isRecording]);

  const latestMemory = memoryUsage[0];
  const memoryTrend = useMemo(() => {
    if (memoryUsage.length < 2) return 'stable';
    const latest = memoryUsage[0].usedJSHeapSize;
    const previous = memoryUsage[1].usedJSHeapSize;
    const change = ((latest - previous) / previous) * 100;

    if (change > 5) return 'increasing';
    if (change < -5) return 'decreasing';
    return 'stable';
  }, [memoryUsage]);

  const metricsByCategory = useMemo(() => {
    const categories: { [key: string]: typeof performanceMetrics } = {};
    performanceMetrics.forEach(metric => {
      const category = metric.name.includes('Resource') ? 'Resources' :
                      metric.name.includes('Load') || metric.name.includes('DOM') ? 'Navigation' :
                      'General';
      if (!categories[category]) categories[category] = [];
      categories[category].push(metric);
    });
    return categories;
  }, [performanceMetrics]);

  const getPerformanceScore = () => {
    if (performanceMetrics.length === 0) return 0;

    const loadTimeMetrics = performanceMetrics.filter(m =>
      m.name.includes('Load') || m.name.includes('DOM')
    );

    if (loadTimeMetrics.length === 0) return 0;

    const avgLoadTime = loadTimeMetrics.reduce((sum, m) => sum + m.value, 0) / loadTimeMetrics.length;

    // Score based on load time (lower is better)
    if (avgLoadTime < 1000) return 95;
    if (avgLoadTime < 2000) return 85;
    if (avgLoadTime < 3000) return 75;
    if (avgLoadTime < 5000) return 65;
    return 50;
  };

  const performanceScore = getPerformanceScore();

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getMemoryUsagePercentage = () => {
    if (!latestMemory) return 0;
    return (latestMemory.usedJSHeapSize / latestMemory.jsHeapSizeLimit) * 100;
  };

  return (
    <div className="h-full flex flex-col">
      {/* Controls */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h3 className="font-medium text-gray-900">Performance Monitor</h3>
            <button
              onClick={() => setIsRecording(!isRecording)}
              className={`flex items-center space-x-2 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                isRecording
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : 'bg-green-100 text-green-700 hover:bg-green-200'
              }`}
            >
              <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500' : 'bg-gray-400'}`} />
              <span>{isRecording ? 'Recording' : 'Paused'}</span>
            </button>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Performance Score:
              <span className={`ml-1 font-semibold ${
                performanceScore >= 90 ? 'text-green-600' :
                performanceScore >= 70 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {performanceScore}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="p-4 space-y-6">
          {/* Memory Usage */}
          {latestMemory && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium text-gray-900 flex items-center space-x-2">
                  <CircleStackIcon className="h-5 w-5 text-purple-600" />
                  <span>Memory Usage</span>
                </h4>
                <span className={`text-sm font-medium ${
                  memoryTrend === 'increasing' ? 'text-red-600' :
                  memoryTrend === 'decreasing' ? 'text-green-600' :
                  'text-gray-600'
                }`}>
                  {memoryTrend}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="text-sm text-gray-600">Used Heap</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatBytes(latestMemory.usedJSHeapSize)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Total Heap</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatBytes(latestMemory.totalJSHeapSize)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Heap Limit</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatBytes(latestMemory.jsHeapSizeLimit)}
                  </div>
                </div>
              </div>

              {/* Memory Usage Bar */}
              <div className="mb-2">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Memory Usage</span>
                  <span>{getMemoryUsagePercentage().toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      getMemoryUsagePercentage() > 80 ? 'bg-red-500' :
                      getMemoryUsagePercentage() > 60 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(getMemoryUsagePercentage(), 100)}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Performance Metrics by Category */}
          {Object.entries(metricsByCategory).map(([category, metrics]) => (
            <div key={category} className="bg-white rounded-lg border border-gray-200 p-4">
              <h4 className="font-medium text-gray-900 mb-4 flex items-center space-x-2">
                <ChartBarIcon className="h-5 w-5 text-blue-600" />
                <span>{category} Metrics</span>
              </h4>

              <div className="space-y-2">
                {metrics.slice(0, 10).map((metric) => (
                  <motion.div
                    key={metric.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedMetric === metric.id ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                    onClick={() => setSelectedMetric(selectedMetric === metric.id ? null : metric.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <ClockIcon className="h-4 w-4 text-gray-500" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{metric.name}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(metric.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className={`text-sm font-semibold ${
                        metric.value > 3000 ? 'text-red-600' :
                        metric.value > 1000 ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>
                        {metric.value.toFixed(1)} {metric.unit}
                      </div>
                      {metric.interfaceId && (
                        <div className="text-xs text-gray-500">{metric.interfaceId}</div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ))}

          {/* Performance Tips */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h4 className="font-medium text-gray-900 mb-4 flex items-center space-x-2">
              <InformationCircleIcon className="h-5 w-5 text-green-600" />
              <span>Performance Tips</span>
            </h4>

            <div className="space-y-3">
              {performanceScore < 70 && (
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="text-sm text-red-800">
                    <div className="font-medium">Performance Issues Detected</div>
                    <div>Your application is loading slowly. Consider optimizing images, reducing bundle size, or implementing code splitting.</div>
                  </div>
                </div>
              )}

              {latestMemory && getMemoryUsagePercentage() > 80 && (
                <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="text-sm text-yellow-800">
                    <div className="font-medium">High Memory Usage</div>
                    <div>Memory usage is high. Check for memory leaks, large objects, or unnecessary data retention.</div>
                  </div>
                </div>
              )}

              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-sm text-blue-800">
                  <div className="font-medium">General Tips</div>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    <li>Use React.memo() for expensive components</li>
                    <li>Implement virtual scrolling for large lists</li>
                    <li>Optimize images and use appropriate formats</li>
                    <li>Minimize bundle size with tree shaking</li>
                    <li>Use lazy loading for routes and components</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {performanceMetrics.length === 0 && (
            <div className="flex items-center justify-center h-32 text-gray-500">
              <div className="text-center">
                <CpuChipIcon className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <div>No performance metrics collected yet</div>
                <div className="text-sm">Metrics will appear as you use the application</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
