/**
 * Performance Baseline Recording System
 *
 * Captures initial performance metrics for each TTA interface and tracks
 * performance regressions over time with historical trend analysis and alerting.
 */

import { EventEmitter } from 'events';

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  interfaceId: string;
  category: 'load_time' | 'render_time' | 'memory_usage' | 'network' | 'custom';
}

export interface PerformanceBaseline {
  interfaceId: string;
  interfaceName: string;
  version: string;
  createdAt: string;
  metrics: {
    [metricName: string]: {
      baseline: number;
      unit: string;
      category: string;
      samples: number;
      standardDeviation: number;
      percentiles: {
        p50: number;
        p75: number;
        p90: number;
        p95: number;
        p99: number;
      };
    };
  };
}

export interface PerformanceRegression {
  id: string;
  interfaceId: string;
  metricName: string;
  baselineValue: number;
  currentValue: number;
  regressionPercentage: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  threshold: number;
  isResolved: boolean;
  resolvedAt?: string;
}

export interface PerformanceTrend {
  interfaceId: string;
  metricName: string;
  timeRange: string;
  dataPoints: Array<{
    timestamp: string;
    value: number;
  }>;
  trend: 'improving' | 'stable' | 'degrading';
  trendStrength: number; // -1 to 1, negative is degrading
  projectedValue?: number;
}

export interface PerformanceAlert {
  id: string;
  type: 'regression' | 'threshold_exceeded' | 'trend_warning';
  severity: 'low' | 'medium' | 'high' | 'critical';
  interfaceId: string;
  metricName: string;
  message: string;
  data: any;
  createdAt: string;
  acknowledged: boolean;
  acknowledgedAt?: string;
  acknowledgedBy?: string;
}

export class PerformanceBaselineManager extends EventEmitter {
  private baselines: Map<string, PerformanceBaseline> = new Map();
  private historicalData: Map<string, PerformanceMetric[]> = new Map();
  private regressions: Map<string, PerformanceRegression> = new Map();
  private alerts: Map<string, PerformanceAlert> = new Map();
  private isRecording: boolean = true;
  private recordingInterval: number = 30000; // 30 seconds
  private recordingTimer: NodeJS.Timeout | null = null;

  // Configuration
  private regressionThresholds = {
    load_time: { medium: 20, high: 40, critical: 60 }, // % increase
    render_time: { medium: 25, high: 50, critical: 75 },
    memory_usage: { medium: 30, high: 60, critical: 100 },
    network: { medium: 15, high: 30, critical: 50 },
    custom: { medium: 20, high: 40, critical: 60 }
  };

  private interfaces = [
    { id: 'patient', name: 'Patient Interface', port: 3000 },
    { id: 'clinical', name: 'Clinical Dashboard', port: 3001 },
    { id: 'admin', name: 'Admin Interface', port: 3002 },
    { id: 'public', name: 'Public Portal', port: 3003 },
    { id: 'stakeholder', name: 'Stakeholder Dashboard', port: 3004 },
    { id: 'api-docs', name: 'API Documentation', port: 3005 },
    { id: 'developer', name: 'Developer Interface', port: 3006 }
  ];

  constructor() {
    super();
    this.loadStoredData();
    this.startRecording();
  }

  private loadStoredData(): void {
    try {
      // Load baselines from localStorage
      const storedBaselines = localStorage.getItem('tta_performance_baselines');
      if (storedBaselines) {
        const baselines = JSON.parse(storedBaselines);
        Object.entries(baselines).forEach(([key, value]) => {
          this.baselines.set(key, value as PerformanceBaseline);
        });
      }

      // Load historical data
      const storedHistorical = localStorage.getItem('tta_performance_historical');
      if (storedHistorical) {
        const historical = JSON.parse(storedHistorical);
        Object.entries(historical).forEach(([key, value]) => {
          this.historicalData.set(key, value as PerformanceMetric[]);
        });
      }

      // Load regressions
      const storedRegressions = localStorage.getItem('tta_performance_regressions');
      if (storedRegressions) {
        const regressions = JSON.parse(storedRegressions);
        Object.entries(regressions).forEach(([key, value]) => {
          this.regressions.set(key, value as PerformanceRegression);
        });
      }

      console.log('📊 Performance baseline data loaded');
    } catch (error) {
      console.error('Error loading performance baseline data:', error);
    }
  }

  private saveData(): void {
    try {
      // Save baselines
      const baselinesObj = Object.fromEntries(this.baselines);
      localStorage.setItem('tta_performance_baselines', JSON.stringify(baselinesObj));

      // Save historical data (keep only last 1000 entries per interface)
      const historicalObj = Object.fromEntries(
        Array.from(this.historicalData.entries()).map(([key, value]) => [
          key,
          value.slice(-1000)
        ])
      );
      localStorage.setItem('tta_performance_historical', JSON.stringify(historicalObj));

      // Save regressions
      const regressionsObj = Object.fromEntries(this.regressions);
      localStorage.setItem('tta_performance_regressions', JSON.stringify(regressionsObj));
    } catch (error) {
      console.error('Error saving performance baseline data:', error);
    }
  }

  public startRecording(): void {
    if (this.recordingTimer) {
      clearInterval(this.recordingTimer);
    }

    this.isRecording = true;
    this.recordingTimer = setInterval(() => {
      this.collectPerformanceMetrics();
    }, this.recordingInterval);

    console.log('📊 Performance baseline recording started');
  }

  public stopRecording(): void {
    if (this.recordingTimer) {
      clearInterval(this.recordingTimer);
      this.recordingTimer = null;
    }
    this.isRecording = false;
    console.log('📊 Performance baseline recording stopped');
  }

  private async collectPerformanceMetrics(): Promise<void> {
    for (const interface_ of this.interfaces) {
      try {
        const metrics = await this.measureInterfacePerformance(interface_);

        for (const metric of metrics) {
          this.recordMetric(metric);
        }
      } catch (error) {
        console.error(`Error collecting metrics for ${interface_.id}:`, error);
      }
    }
  }

  private async measureInterfacePerformance(interface_: { id: string; name: string; port: number }): Promise<PerformanceMetric[]> {
    const metrics: PerformanceMetric[] = [];
    const timestamp = new Date().toISOString();

    try {
      // Measure load time
      const loadStartTime = performance.now();
      const response = await fetch(`http://localhost:${interface_.port}/health`, {
        method: 'GET',
        cache: 'no-cache'
      });
      const loadEndTime = performance.now();
      const loadTime = loadEndTime - loadStartTime;

      metrics.push({
        name: 'load_time',
        value: loadTime,
        unit: 'ms',
        timestamp,
        interfaceId: interface_.id,
        category: 'load_time'
      });

      // Measure response status
      metrics.push({
        name: 'response_status',
        value: response.status,
        unit: 'status_code',
        timestamp,
        interfaceId: interface_.id,
        category: 'network'
      });

      // Memory usage (if available)
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        metrics.push({
          name: 'memory_used',
          value: memory.usedJSHeapSize,
          unit: 'bytes',
          timestamp,
          interfaceId: interface_.id,
          category: 'memory_usage'
        });
      }

      // Navigation timing (for current interface only)
      if (interface_.id === 'developer' && 'getEntriesByType' in performance) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          metrics.push({
            name: 'dom_content_loaded',
            value: navigation.domContentLoadedEventEnd - navigation.navigationStart,
            unit: 'ms',
            timestamp,
            interfaceId: interface_.id,
            category: 'render_time'
          });
        }
      }

    } catch (error) {
      // Record error as a metric
      metrics.push({
        name: 'error_count',
        value: 1,
        unit: 'count',
        timestamp,
        interfaceId: interface_.id,
        category: 'custom'
      });
    }

    return metrics;
  }

  public recordMetric(metric: PerformanceMetric): void {
    const key = `${metric.interfaceId}_${metric.name}`;

    // Add to historical data
    if (!this.historicalData.has(key)) {
      this.historicalData.set(key, []);
    }
    this.historicalData.get(key)!.push(metric);

    // Check for regressions
    this.checkForRegression(metric);

    // Update baseline if needed
    this.updateBaseline(metric);

    // Save data periodically
    if (Math.random() < 0.1) { // 10% chance to save on each metric
      this.saveData();
    }

    this.emit('metric_recorded', metric);
  }

  private updateBaseline(metric: PerformanceMetric): void {
    const baselineKey = metric.interfaceId;

    if (!this.baselines.has(baselineKey)) {
      // Create new baseline
      this.createBaseline(metric.interfaceId);
    }

    const baseline = this.baselines.get(baselineKey)!;
    const metricKey = `${metric.interfaceId}_${metric.name}`;
    const historicalData = this.historicalData.get(metricKey) || [];

    if (historicalData.length >= 10) { // Need at least 10 samples
      const values = historicalData.map(m => m.value);
      const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
      const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
      const stdDev = Math.sqrt(variance);

      // Calculate percentiles
      const sortedValues = [...values].sort((a, b) => a - b);
      const percentiles = {
        p50: this.getPercentile(sortedValues, 50),
        p75: this.getPercentile(sortedValues, 75),
        p90: this.getPercentile(sortedValues, 90),
        p95: this.getPercentile(sortedValues, 95),
        p99: this.getPercentile(sortedValues, 99)
      };

      baseline.metrics[metric.name] = {
        baseline: mean,
        unit: metric.unit,
        category: metric.category,
        samples: values.length,
        standardDeviation: stdDev,
        percentiles
      };

      this.baselines.set(baselineKey, baseline);
    }
  }

  private getPercentile(sortedArray: number[], percentile: number): number {
    const index = (percentile / 100) * (sortedArray.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index % 1;

    if (upper >= sortedArray.length) return sortedArray[sortedArray.length - 1];
    return sortedArray[lower] * (1 - weight) + sortedArray[upper] * weight;
  }

  private createBaseline(interfaceId: string): void {
    const interface_ = this.interfaces.find(i => i.id === interfaceId);
    if (!interface_) return;

    const baseline: PerformanceBaseline = {
      interfaceId,
      interfaceName: interface_.name,
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      metrics: {}
    };

    this.baselines.set(interfaceId, baseline);
    this.emit('baseline_created', baseline);
  }

  private checkForRegression(metric: PerformanceMetric): void {
    const baseline = this.baselines.get(metric.interfaceId);
    if (!baseline || !baseline.metrics[metric.name]) return;

    const baselineMetric = baseline.metrics[metric.name];
    const regressionPercentage = ((metric.value - baselineMetric.baseline) / baselineMetric.baseline) * 100;

    const thresholds = this.regressionThresholds[metric.category] || this.regressionThresholds.custom;
    let severity: 'low' | 'medium' | 'high' | 'critical' | null = null;

    if (regressionPercentage >= thresholds.critical) {
      severity = 'critical';
    } else if (regressionPercentage >= thresholds.high) {
      severity = 'high';
    } else if (regressionPercentage >= thresholds.medium) {
      severity = 'medium';
    } else if (regressionPercentage >= 10) {
      severity = 'low';
    }

    if (severity) {
      const regressionId = `${metric.interfaceId}_${metric.name}_${Date.now()}`;
      const regression: PerformanceRegression = {
        id: regressionId,
        interfaceId: metric.interfaceId,
        metricName: metric.name,
        baselineValue: baselineMetric.baseline,
        currentValue: metric.value,
        regressionPercentage,
        severity,
        detectedAt: metric.timestamp,
        threshold: thresholds[severity],
        isResolved: false
      };

      this.regressions.set(regressionId, regression);
      this.createAlert('regression', severity, regression);
      this.emit('regression_detected', regression);
    }
  }

  private createAlert(type: PerformanceAlert['type'], severity: PerformanceAlert['severity'], data: any): void {
    const alertId = `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    let message = '';
    switch (type) {
      case 'regression':
        message = `Performance regression detected in ${data.interfaceId}: ${data.metricName} increased by ${data.regressionPercentage.toFixed(1)}%`;
        break;
      case 'threshold_exceeded':
        message = `Performance threshold exceeded in ${data.interfaceId}: ${data.metricName}`;
        break;
      case 'trend_warning':
        message = `Performance trend warning for ${data.interfaceId}: ${data.metricName} is degrading`;
        break;
    }

    const alert: PerformanceAlert = {
      id: alertId,
      type,
      severity,
      interfaceId: data.interfaceId,
      metricName: data.metricName,
      message,
      data,
      createdAt: new Date().toISOString(),
      acknowledged: false
    };

    this.alerts.set(alertId, alert);
    this.emit('alert_created', alert);
  }

  // Public API methods

  public getBaseline(interfaceId: string): PerformanceBaseline | null {
    return this.baselines.get(interfaceId) || null;
  }

  public getAllBaselines(): PerformanceBaseline[] {
    return Array.from(this.baselines.values());
  }

  public getHistoricalData(interfaceId: string, metricName: string): PerformanceMetric[] {
    const key = `${interfaceId}_${metricName}`;
    return this.historicalData.get(key) || [];
  }

  public getRegressions(interfaceId?: string): PerformanceRegression[] {
    const regressions = Array.from(this.regressions.values());
    return interfaceId ? regressions.filter(r => r.interfaceId === interfaceId) : regressions;
  }

  public getAlerts(acknowledged?: boolean): PerformanceAlert[] {
    const alerts = Array.from(this.alerts.values());
    return acknowledged !== undefined ? alerts.filter(a => a.acknowledged === acknowledged) : alerts;
  }

  public acknowledgeAlert(alertId: string, acknowledgedBy: string): void {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedAt = new Date().toISOString();
      alert.acknowledgedBy = acknowledgedBy;
      this.alerts.set(alertId, alert);
      this.emit('alert_acknowledged', alert);
    }
  }

  public generateTrendAnalysis(interfaceId: string, metricName: string, timeRange: string = '24h'): PerformanceTrend | null {
    const historicalData = this.getHistoricalData(interfaceId, metricName);
    if (historicalData.length < 10) return null;

    // Filter data by time range
    const now = new Date();
    const timeRangeMs = this.parseTimeRange(timeRange);
    const cutoffTime = new Date(now.getTime() - timeRangeMs);

    const filteredData = historicalData.filter(d => new Date(d.timestamp) >= cutoffTime);
    if (filteredData.length < 5) return null;

    // Calculate trend
    const dataPoints = filteredData.map(d => ({
      timestamp: d.timestamp,
      value: d.value
    }));

    const trendStrength = this.calculateTrendStrength(dataPoints);
    let trend: 'improving' | 'stable' | 'degrading' = 'stable';

    if (trendStrength > 0.3) {
      trend = 'degrading'; // Values increasing (worse performance)
    } else if (trendStrength < -0.3) {
      trend = 'improving'; // Values decreasing (better performance)
    }

    return {
      interfaceId,
      metricName,
      timeRange,
      dataPoints,
      trend,
      trendStrength
    };
  }

  private parseTimeRange(timeRange: string): number {
    const unit = timeRange.slice(-1);
    const value = parseInt(timeRange.slice(0, -1));

    switch (unit) {
      case 'h': return value * 60 * 60 * 1000;
      case 'd': return value * 24 * 60 * 60 * 1000;
      case 'w': return value * 7 * 24 * 60 * 60 * 1000;
      default: return 24 * 60 * 60 * 1000; // Default to 24 hours
    }
  }

  private calculateTrendStrength(dataPoints: Array<{ timestamp: string; value: number }>): number {
    if (dataPoints.length < 2) return 0;

    // Simple linear regression to calculate trend
    const n = dataPoints.length;
    const xValues = dataPoints.map((_, i) => i);
    const yValues = dataPoints.map(d => d.value);

    const sumX = xValues.reduce((sum, x) => sum + x, 0);
    const sumY = yValues.reduce((sum, y) => sum + y, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
    const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);

    // Normalize slope to -1 to 1 range
    const maxValue = Math.max(...yValues);
    const minValue = Math.min(...yValues);
    const range = maxValue - minValue;

    return range > 0 ? Math.max(-1, Math.min(1, slope / range * n)) : 0;
  }

  public dispose(): void {
    this.stopRecording();
    this.saveData();
    this.removeAllListeners();
  }
}

// Singleton instance
export const performanceBaselineManager = new PerformanceBaselineManager();
