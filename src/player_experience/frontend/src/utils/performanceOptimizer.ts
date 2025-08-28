/**
 * Performance optimization utilities for TTA frontend
 */

export interface PerformanceMetrics {
  fps: number;
  memory_usage: number;
  render_time: number;
  api_response_times: number[];
  bundle_size: number;
  load_time: number;
  interactive_time: number;
}

export interface OptimizationRecommendation {
  category: 'rendering' | 'api' | 'memory' | 'bundle' | 'general';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  implementation: string;
}

/**
 * Performance monitoring and optimization utility
 */
export class PerformanceOptimizer {
  private metrics: Partial<PerformanceMetrics> = {};
  private frameCount = 0;
  private lastFrameTime = 0;
  private fpsHistory: number[] = [];

  /**
   * Initialize performance monitoring
   */
  init(): void {
    this.monitorFPS();
    this.monitorMemory();
    this.monitorLoadTimes();
    this.setupPerformanceObserver();
  }

  /**
   * Monitor FPS for 3D rendering performance
   */
  private monitorFPS(): void {
    const measureFPS = (timestamp: number) => {
      if (this.lastFrameTime) {
        const delta = timestamp - this.lastFrameTime;
        const fps = 1000 / delta;
        this.fpsHistory.push(fps);
        
        // Keep only last 60 frames
        if (this.fpsHistory.length > 60) {
          this.fpsHistory.shift();
        }
        
        this.metrics.fps = this.fpsHistory.reduce((a, b) => a + b, 0) / this.fpsHistory.length;
      }
      
      this.lastFrameTime = timestamp;
      this.frameCount++;
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);
  }

  /**
   * Monitor memory usage
   */
  private monitorMemory(): void {
    if ('memory' in performance) {
      const memInfo = (performance as any).memory;
      this.metrics.memory_usage = memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit;
    }
  }

  /**
   * Monitor page load times
   */
  private monitorLoadTimes(): void {
    if (performance.timing) {
      const timing = performance.timing;
      this.metrics.load_time = timing.loadEventEnd - timing.navigationStart;
      this.metrics.interactive_time = timing.domInteractive - timing.navigationStart;
    }
  }

  /**
   * Setup Performance Observer for detailed metrics
   */
  private setupPerformanceObserver(): void {
    if ('PerformanceObserver' in window) {
      // Monitor resource loading
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.name.includes('/api/')) {
            if (!this.metrics.api_response_times) {
              this.metrics.api_response_times = [];
            }
            this.metrics.api_response_times.push(entry.duration);
          }
        });
      });
      
      resourceObserver.observe({ entryTypes: ['resource'] });

      // Monitor rendering performance
      const paintObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.name === 'first-contentful-paint') {
            console.log('First Contentful Paint:', entry.startTime);
          }
        });
      });
      
      paintObserver.observe({ entryTypes: ['paint'] });
    }
  }

  /**
   * Get current performance metrics
   */
  getMetrics(): PerformanceMetrics {
    this.monitorMemory(); // Update memory usage
    
    return {
      fps: this.metrics.fps || 0,
      memory_usage: this.metrics.memory_usage || 0,
      render_time: this.metrics.render_time || 0,
      api_response_times: this.metrics.api_response_times || [],
      bundle_size: this.metrics.bundle_size || 0,
      load_time: this.metrics.load_time || 0,
      interactive_time: this.metrics.interactive_time || 0,
    };
  }

  /**
   * Generate optimization recommendations based on metrics
   */
  getOptimizationRecommendations(): OptimizationRecommendation[] {
    const metrics = this.getMetrics();
    const recommendations: OptimizationRecommendation[] = [];

    // FPS recommendations
    if (metrics.fps < 30) {
      recommendations.push({
        category: 'rendering',
        priority: 'high',
        title: 'Low FPS Detected',
        description: `Current FPS is ${metrics.fps.toFixed(1)}, which may cause stuttering in 3D scenes.`,
        implementation: 'Reduce 3D scene complexity, optimize materials, or implement LOD (Level of Detail) system.'
      });
    } else if (metrics.fps < 45) {
      recommendations.push({
        category: 'rendering',
        priority: 'medium',
        title: 'Suboptimal FPS',
        description: `FPS is ${metrics.fps.toFixed(1)}. Consider optimizations for smoother experience.`,
        implementation: 'Review 3D scene complexity and consider reducing particle counts or shadow quality.'
      });
    }

    // Memory recommendations
    if (metrics.memory_usage > 0.8) {
      recommendations.push({
        category: 'memory',
        priority: 'high',
        title: 'High Memory Usage',
        description: `Memory usage is at ${(metrics.memory_usage * 100).toFixed(1)}% of available heap.`,
        implementation: 'Implement object pooling, dispose unused 3D objects, and optimize texture sizes.'
      });
    } else if (metrics.memory_usage > 0.6) {
      recommendations.push({
        category: 'memory',
        priority: 'medium',
        title: 'Elevated Memory Usage',
        description: `Memory usage is at ${(metrics.memory_usage * 100).toFixed(1)}%.`,
        implementation: 'Monitor for memory leaks and consider lazy loading of assets.'
      });
    }

    // API response time recommendations
    if (metrics.api_response_times.length > 0) {
      const avgResponseTime = metrics.api_response_times.reduce((a, b) => a + b, 0) / metrics.api_response_times.length;
      
      if (avgResponseTime > 2000) {
        recommendations.push({
          category: 'api',
          priority: 'high',
          title: 'Slow API Responses',
          description: `Average API response time is ${avgResponseTime.toFixed(0)}ms.`,
          implementation: 'Implement request caching, optimize API queries, or add loading states.'
        });
      } else if (avgResponseTime > 1000) {
        recommendations.push({
          category: 'api',
          priority: 'medium',
          title: 'API Response Time Could Be Improved',
          description: `Average API response time is ${avgResponseTime.toFixed(0)}ms.`,
          implementation: 'Consider implementing optimistic updates or background prefetching.'
        });
      }
    }

    // Load time recommendations
    if (metrics.load_time > 5000) {
      recommendations.push({
        category: 'bundle',
        priority: 'high',
        title: 'Slow Page Load',
        description: `Page load time is ${(metrics.load_time / 1000).toFixed(1)} seconds.`,
        implementation: 'Implement code splitting, lazy loading, and optimize bundle size.'
      });
    } else if (metrics.load_time > 3000) {
      recommendations.push({
        category: 'bundle',
        priority: 'medium',
        title: 'Page Load Could Be Faster',
        description: `Page load time is ${(metrics.load_time / 1000).toFixed(1)} seconds.`,
        implementation: 'Consider preloading critical resources and optimizing images.'
      });
    }

    // General recommendations if performance is good
    if (recommendations.length === 0) {
      recommendations.push({
        category: 'general',
        priority: 'low',
        title: 'Performance Looks Good',
        description: 'All performance metrics are within acceptable ranges.',
        implementation: 'Continue monitoring and consider implementing performance budgets for future development.'
      });
    }

    return recommendations.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  /**
   * Apply automatic optimizations where possible
   */
  applyAutomaticOptimizations(): void {
    // Optimize images loading
    this.optimizeImageLoading();
    
    // Setup intersection observer for lazy loading
    this.setupLazyLoading();
    
    // Optimize 3D rendering settings based on device capabilities
    this.optimize3DSettings();
    
    // Setup request deduplication
    this.setupRequestDeduplication();
  }

  /**
   * Optimize image loading
   */
  private optimizeImageLoading(): void {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            img.src = img.dataset.src || '';
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
          }
        });
      });

      images.forEach((img) => imageObserver.observe(img));
    }
  }

  /**
   * Setup lazy loading for components
   */
  private setupLazyLoading(): void {
    // This would be implemented with React.lazy() in actual components
    console.log('Lazy loading setup - implement with React.lazy() in components');
  }

  /**
   * Optimize 3D settings based on device capabilities
   */
  private optimize3DSettings(): void {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return;

    // Check device capabilities
    const renderer = gl.getParameter(gl.RENDERER);
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isLowEnd = isMobile || renderer.includes('Intel');

    // Store optimization settings for 3D components to use
    const settings = {
      pixelRatio: isLowEnd ? 1 : Math.min(window.devicePixelRatio, 2),
      shadowMapSize: isLowEnd ? 512 : 1024,
      antialias: !isLowEnd,
      particleCount: isLowEnd ? 1000 : 5000,
    };

    // Store in global object for 3D components to access
    (window as any).tta3DOptimizations = settings;
  }

  /**
   * Setup request deduplication to prevent duplicate API calls
   */
  private setupRequestDeduplication(): void {
    const pendingRequests = new Map<string, Promise<any>>();
    
    // Override fetch to add deduplication
    const originalFetch = window.fetch;
    window.fetch = function(input: RequestInfo | URL, init?: RequestInit) {
      const key = `${input.toString()}_${JSON.stringify(init)}`;
      
      if (pendingRequests.has(key)) {
        return pendingRequests.get(key)!;
      }
      
      const promise = originalFetch(input, init).finally(() => {
        pendingRequests.delete(key);
      });
      
      pendingRequests.set(key, promise);
      return promise;
    };
  }

  /**
   * Generate performance report
   */
  generateReport(): {
    metrics: PerformanceMetrics;
    recommendations: OptimizationRecommendation[];
    score: number;
  } {
    const metrics = this.getMetrics();
    const recommendations = this.getOptimizationRecommendations();
    
    // Calculate performance score (0-100)
    let score = 100;
    
    // Deduct points based on issues
    if (metrics.fps < 30) score -= 30;
    else if (metrics.fps < 45) score -= 15;
    
    if (metrics.memory_usage > 0.8) score -= 25;
    else if (metrics.memory_usage > 0.6) score -= 10;
    
    if (metrics.load_time > 5000) score -= 20;
    else if (metrics.load_time > 3000) score -= 10;
    
    const avgApiTime = metrics.api_response_times.length > 0 
      ? metrics.api_response_times.reduce((a, b) => a + b, 0) / metrics.api_response_times.length 
      : 0;
    
    if (avgApiTime > 2000) score -= 15;
    else if (avgApiTime > 1000) score -= 5;
    
    score = Math.max(0, Math.min(100, score));
    
    return {
      metrics,
      recommendations,
      score: Math.round(score),
    };
  }
}

// Global performance optimizer instance
export const performanceOptimizer = new PerformanceOptimizer();

// Auto-initialize when module loads
if (typeof window !== 'undefined') {
  performanceOptimizer.init();
  performanceOptimizer.applyAutomaticOptimizations();
}

export default PerformanceOptimizer;
