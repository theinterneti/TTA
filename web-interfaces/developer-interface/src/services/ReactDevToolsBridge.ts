/**
 * React DevTools Browser Extension Integration Bridge
 *
 * Provides seamless integration between the custom Component Tree Viewer
 * and the React DevTools browser extension for enhanced debugging capabilities.
 */

import { EventEmitter } from 'events';

interface ReactDevToolsHook {
  isDisabled?: boolean;
  supportsFiber?: boolean;
  renderers?: Map<number, any>;
  onCommitFiberRoot?: (id: number, root: any, priorityLevel?: any) => void;
  onCommitFiberUnmount?: (id: number, fiber: any) => void;
  inject?: (renderer: any) => number;
}

interface ComponentTreeNode {
  id: string;
  displayName: string;
  type: string;
  key: string | null;
  props: any;
  state: any;
  children: ComponentTreeNode[];
  depth: number;
  isSelected?: boolean;
  canHaveChildren: boolean;
  renderCount: number;
  lastRenderTime: number;
  actualDuration?: number;
  selfBaseDuration?: number;
}

interface DevToolsProfilerData {
  id: string;
  actualDuration: number;
  baseDuration: number;
  startTime: number;
  commitTime: number;
  interactions: Set<any>;
}

export class ReactDevToolsBridge extends EventEmitter {
  private devToolsHook: ReactDevToolsHook | null = null;
  private isConnected: boolean = false;
  private componentTree: ComponentTreeNode[] = [];
  private selectedComponentId: string | null = null;
  private profilerData: Map<string, DevToolsProfilerData> = new Map();
  private renderCounts: Map<string, number> = new Map();

  constructor() {
    super();
    this.initializeDevToolsIntegration();
  }

  private initializeDevToolsIntegration(): void {
    // Check if React DevTools hook is available
    if (typeof window !== 'undefined' && (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      this.devToolsHook = (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__;
      this.setupDevToolsListeners();
      this.isConnected = true;
      console.log('🔧 React DevTools bridge connected');
    } else {
      // Fallback: Set up a listener for when DevTools becomes available
      this.setupDevToolsDetection();
    }
  }

  private setupDevToolsDetection(): void {
    if (typeof window === 'undefined') return;

    // Poll for DevTools availability
    const checkForDevTools = () => {
      if ((window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__ && !this.isConnected) {
        this.devToolsHook = (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__;
        this.setupDevToolsListeners();
        this.isConnected = true;
        console.log('🔧 React DevTools bridge connected (delayed)');
        this.emit('devtools_connected');
      }
    };

    // Check periodically for DevTools
    const interval = setInterval(() => {
      checkForDevTools();
      if (this.isConnected) {
        clearInterval(interval);
      }
    }, 1000);

    // Stop checking after 30 seconds
    setTimeout(() => {
      clearInterval(interval);
      if (!this.isConnected) {
        console.warn('React DevTools not detected - some debugging features may be limited');
      }
    }, 30000);
  }

  private setupDevToolsListeners(): void {
    if (!this.devToolsHook) return;

    // Store original hooks
    const originalOnCommitFiberRoot = this.devToolsHook.onCommitFiberRoot;
    const originalOnCommitFiberUnmount = this.devToolsHook.onCommitFiberUnmount;

    // Intercept fiber commits for component tree updates
    this.devToolsHook.onCommitFiberRoot = (id: number, root: any, priorityLevel?: any) => {
      try {
        this.handleFiberCommit(id, root, priorityLevel);

        // Call original hook if it exists
        if (originalOnCommitFiberRoot) {
          originalOnCommitFiberRoot.call(this.devToolsHook, id, root, priorityLevel);
        }
      } catch (error) {
        console.error('Error in DevTools fiber commit handler:', error);
      }
    };

    // Intercept fiber unmounts
    this.devToolsHook.onCommitFiberUnmount = (id: number, fiber: any) => {
      try {
        this.handleFiberUnmount(id, fiber);

        // Call original hook if it exists
        if (originalOnCommitFiberUnmount) {
          originalOnCommitFiberUnmount.call(this.devToolsHook, id, fiber);
        }
      } catch (error) {
        console.error('Error in DevTools fiber unmount handler:', error);
      }
    };
  }

  private handleFiberCommit(id: number, root: any, priorityLevel?: any): void {
    try {
      // Extract component tree from fiber root
      const componentTree = this.extractComponentTreeFromFiber(root.current);
      this.componentTree = componentTree;

      // Extract profiler data if available
      this.extractProfilerData(root.current);

      // Emit tree update event
      this.emit('component_tree_updated', {
        tree: componentTree,
        rootId: id,
        priorityLevel
      });
    } catch (error) {
      console.error('Error handling fiber commit:', error);
    }
  }

  private handleFiberUnmount(id: number, fiber: any): void {
    try {
      // Handle component unmounting
      const componentId = this.getFiberComponentId(fiber);
      if (componentId) {
        this.emit('component_unmounted', { componentId, rootId: id });
      }
    } catch (error) {
      console.error('Error handling fiber unmount:', error);
    }
  }

  private extractComponentTreeFromFiber(fiber: any, depth: number = 0): ComponentTreeNode[] {
    const nodes: ComponentTreeNode[] = [];

    if (!fiber) return nodes;

    try {
      // Process current fiber
      const node = this.createComponentNodeFromFiber(fiber, depth);
      if (node) {
        nodes.push(node);
      }

      // Process children
      let child = fiber.child;
      while (child) {
        const childNodes = this.extractComponentTreeFromFiber(child, depth + 1);
        if (node) {
          node.children.push(...childNodes);
        } else {
          nodes.push(...childNodes);
        }
        child = child.sibling;
      }
    } catch (error) {
      console.error('Error extracting component tree from fiber:', error);
    }

    return nodes;
  }

  private createComponentNodeFromFiber(fiber: any, depth: number): ComponentTreeNode | null {
    try {
      // Skip non-component fibers
      if (!this.isComponentFiber(fiber)) {
        return null;
      }

      const componentId = this.getFiberComponentId(fiber);
      const displayName = this.getFiberDisplayName(fiber);

      // Update render count
      const currentCount = this.renderCounts.get(componentId) || 0;
      this.renderCounts.set(componentId, currentCount + 1);

      return {
        id: componentId,
        displayName,
        type: this.getFiberType(fiber),
        key: fiber.key,
        props: fiber.memoizedProps || {},
        state: fiber.memoizedState || {},
        children: [],
        depth,
        canHaveChildren: !!fiber.child,
        renderCount: this.renderCounts.get(componentId) || 1,
        lastRenderTime: Date.now(),
        actualDuration: fiber.actualDuration,
        selfBaseDuration: fiber.selfBaseDuration
      };
    } catch (error) {
      console.error('Error creating component node from fiber:', error);
      return null;
    }
  }

  private isComponentFiber(fiber: any): boolean {
    // Check if fiber represents a React component
    return fiber && (
      fiber.type &&
      (typeof fiber.type === 'function' || typeof fiber.type === 'object') &&
      fiber.tag !== undefined
    );
  }

  private getFiberComponentId(fiber: any): string {
    // Generate unique ID for component
    return `${fiber.type?.name || 'Unknown'}_${fiber.index || 0}_${fiber.key || 'no-key'}`;
  }

  private getFiberDisplayName(fiber: any): string {
    if (fiber.type?.displayName) {
      return fiber.type.displayName;
    }

    if (fiber.type?.name) {
      return fiber.type.name;
    }

    if (typeof fiber.type === 'string') {
      return fiber.type;
    }

    return 'Unknown';
  }

  private getFiberType(fiber: any): string {
    if (typeof fiber.type === 'string') {
      return 'host'; // DOM element
    }

    if (typeof fiber.type === 'function') {
      return fiber.type.prototype?.isReactComponent ? 'class' : 'function';
    }

    return 'unknown';
  }

  private extractProfilerData(fiber: any): void {
    try {
      if (fiber.actualDuration !== undefined) {
        const componentId = this.getFiberComponentId(fiber);

        this.profilerData.set(componentId, {
          id: componentId,
          actualDuration: fiber.actualDuration,
          baseDuration: fiber.selfBaseDuration || 0,
          startTime: fiber.actualStartTime || 0,
          commitTime: Date.now(),
          interactions: fiber.interactions || new Set()
        });
      }

      // Process children
      let child = fiber.child;
      while (child) {
        this.extractProfilerData(child);
        child = child.sibling;
      }
    } catch (error) {
      console.error('Error extracting profiler data:', error);
    }
  }

  // Public API methods

  public getComponentTree(): ComponentTreeNode[] {
    return this.componentTree;
  }

  public selectComponent(componentId: string): void {
    this.selectedComponentId = componentId;

    // Try to select component in React DevTools if available
    if (this.devToolsHook && this.devToolsHook.renderers) {
      try {
        // This would integrate with DevTools selection if the API is available
        this.emit('component_selected', { componentId });
      } catch (error) {
        console.error('Error selecting component in DevTools:', error);
      }
    }
  }

  public getSelectedComponent(): string | null {
    return this.selectedComponentId;
  }

  public getComponentProfilerData(componentId: string): DevToolsProfilerData | null {
    return this.profilerData.get(componentId) || null;
  }

  public getAllProfilerData(): Map<string, DevToolsProfilerData> {
    return new Map(this.profilerData);
  }

  public isDevToolsConnected(): boolean {
    return this.isConnected;
  }

  public getDevToolsCapabilities(): string[] {
    const capabilities = ['component_tree', 'render_tracking'];

    if (this.devToolsHook?.supportsFiber) {
      capabilities.push('fiber_inspection');
    }

    if (this.profilerData.size > 0) {
      capabilities.push('performance_profiling');
    }

    return capabilities;
  }

  public inspectComponent(componentId: string): any {
    // Find component in tree and return detailed inspection data
    const findComponent = (nodes: ComponentTreeNode[]): ComponentTreeNode | null => {
      for (const node of nodes) {
        if (node.id === componentId) {
          return node;
        }
        const found = findComponent(node.children);
        if (found) return found;
      }
      return null;
    };

    const component = findComponent(this.componentTree);
    if (!component) return null;

    return {
      ...component,
      profilerData: this.getComponentProfilerData(componentId),
      devToolsData: this.isConnected ? {
        canInspect: true,
        hasDevToolsSupport: true
      } : null
    };
  }

  public dispose(): void {
    // Clean up listeners and references
    this.removeAllListeners();
    this.componentTree = [];
    this.profilerData.clear();
    this.renderCounts.clear();
    this.selectedComponentId = null;
  }
}

// Singleton instance
export const reactDevToolsBridge = new ReactDevToolsBridge();
